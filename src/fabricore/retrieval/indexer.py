import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from fabricore.retrieval.schemas import DocumentChunk


class DocumentIndexer:
    def __init__(
        self,
        embedding_model: str,
        vector_store_dir: str,
    ) -> None:
        self.model = SentenceTransformer(
            embedding_model
        )

        self.vector_store_dir = Path(
            vector_store_dir
        )

    def build(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        if not chunks:
            raise ValueError(
                "No document chunks provided."
            )

        texts = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = self.model.encode_document(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(
            dimension
        )

        index.add(embeddings)

        self.vector_store_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            index,
            str(
                self.vector_store_dir
                / "documents.faiss"
            ),
        )

        metadata_path = (
            self.vector_store_dir
            / "chunks.json"
        )

        metadata_path.write_text(
            json.dumps(
                [
                    chunk.model_dump(
                        mode="json"
                    )
                    for chunk in chunks
                ],
                indent=2,
            ),
            encoding="utf-8",
        )

        print(
            f"Indexed {len(chunks)} chunks."
        )

        print(
            f"Embedding dimension: {dimension}"
        )