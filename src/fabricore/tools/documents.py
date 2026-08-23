from fabricore.retrieval.retriever import DocumentRetriever
from fabricore.retrieval.schemas import RetrievedDocument


class DocumentSearchTool:
    """Search approved reference documents."""

    def __init__(self, retriever: DocumentRetriever) -> None:
        self.retriever = retriever

    def run(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[RetrievedDocument]:
        return self.retriever.search(
            query=query,
            top_k=top_k,
        )