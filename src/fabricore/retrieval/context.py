from fabricore.retrieval.schemas import RetrievedDocument


def format_retrieved_context(
    documents: list[RetrievedDocument],
) -> str:
    if not documents:
        return (
            "No reference documents were retrieved."
        )

    sections: list[str] = []

    for document in documents:
        sections.append(
            "\n".join(
                [
                    "REFERENCE DOCUMENT",
                    f"Document ID: {document.document_id}",
                    f"Source: {document.source}",
                    f"Section: {document.title}",
                    f"Relevance Score: {document.score:.4f}",
                    "",
                    document.content,
                ]
            )
        )

    return "\n\n---\n\n".join(sections)