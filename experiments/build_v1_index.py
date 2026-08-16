from fabricore.config.settings import get_settings
from fabricore.retrieval.document_loader import (
    MarkdownDocumentLoader,
)
from fabricore.retrieval.indexer import DocumentIndexer


def main() -> None:
    settings = get_settings()

    loader = MarkdownDocumentLoader(
        document_dir=settings.document_dir,
    )

    chunks = loader.load()

    print(
        f"Loaded {len(chunks)} document chunks."
    )

    indexer = DocumentIndexer(
        embedding_model=settings.embedding_model,
        vector_store_dir=settings.vector_store_dir,
    )

    indexer.build(chunks)


if __name__ == "__main__":
    main()