import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

from fabricore.retrieval.schemas import DocumentChunk, RetrievedDocument


class DocumentRetriever:
    def __init__(
        self,
        embedding_model: str,
        vector_store_dir: str,
    ) -> None:
        self.model = SentenceTransformer(
            embedding_model
        )

        vector_store_path = Path(vector_store_dir)

        self.index = faiss.read_index(
            str(
                vector_store_path
                / "documents.faiss"
            )
        )

        metadata = json.loads(
            (
                vector_store_path
                / "chunks.json"
            ).read_text(
                encoding="utf-8"
            )
        )

        self.chunks = [
            DocumentChunk.model_validate(item)
            for item in metadata
        ]

        if self.index.ntotal != len(self.chunks):
            raise ValueError(
                "FAISS index size does not match "
                "stored chunk metadata."
            )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[RetrievedDocument]:
        if not query.strip():
            raise ValueError(
                "Query must not be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        query_embedding = self.model.encode_query(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, self.index.ntotal),
        )

        results: list[RetrievedDocument] = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0:
                continue

            chunk = self.chunks[index]

            results.append(
                RetrievedDocument(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    source=chunk.source,
                    title=chunk.title,
                    content=chunk.content,
                    score=float(score),
                )
            )

        return results