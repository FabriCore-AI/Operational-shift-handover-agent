from pydantic import BaseModel, ConfigDict


class DocumentChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    document_id: str
    source: str
    category: str
    title: str
    content: str
    metadata: dict[str, str]

class RetrievedDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    document_id: str
    source: str
    title: str
    content: str
    score: float