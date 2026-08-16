from fabricore.config.settings import get_settings
from fabricore.retrieval.retriever import DocumentRetriever


def main() -> None:
    settings = get_settings()

    retriever = DocumentRetriever(
        embedding_model=settings.embedding_model,
        vector_store_dir=settings.vector_store_dir,
    )

    queries = [
        "high vibration on P-101",
        "response to high reactor temperature",
        "equipment protection trip",
        "shift handover requirements",
    ]

    for query in queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)

        results = retriever.search(
            query=query,
            top_k=3,
        )

        for rank, (chunk, score) in enumerate(
            results,
            start=1,
        ):
            print(
                f"\n[{rank}] score={score:.4f}"
            )
            print(
                f"Document : {chunk.document_id}"
            )
            print(
                f"Section  : {chunk.title}"
            )
            print(
                f"Source   : {chunk.source}"
            )
            print(
                f"Content  : {chunk.content[:300]}"
            )


if __name__ == "__main__":
    main()