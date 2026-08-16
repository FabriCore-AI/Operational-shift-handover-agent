from pathlib import Path

from fabricore.retrieval.schemas import DocumentChunk


class MarkdownDocumentLoader:
    def __init__(self, document_dir: str) -> None:
        self.document_dir = Path(document_dir)

    def load(self) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []

        for path in sorted(self.document_dir.rglob("*.md")):
            category = path.parent.name

            chunks.extend(
                self._load_document(
                    path=path,
                    category=category,
                )
            )

        return chunks

    def _load_document(
        self,
        path: Path,
        category: str,
    ) -> list[DocumentChunk]:
        text = path.read_text(
            encoding="utf-8",
        ).strip()

        lines = text.splitlines()

        document_title = ""
        document_id = ""

        for line in lines:
            if line.startswith("# "):
                document_title = line[2:].strip()

            if line.startswith("Document ID:"):
                document_id = line.split(
                    ":",
                    1,
                )[1].strip()

        if not document_id:
            raise ValueError(
                f"Document ID missing: {path}"
            )

        sections = self._split_sections(lines)

        chunks: list[DocumentChunk] = []

        for index, (section_title, content) in enumerate(
            sections,
            start=1,
        ):
            chunk_id = (
                f"{document_id}-{index:02d}"
            )

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    source=path.name,
                    category=category,
                    title=section_title,
                    content=content,
                    metadata={
                        "document_id": document_id,
                        "source": path.name,
                        "category": category,
                        "title": document_title,
                    },
                )
            )

        return chunks

    @staticmethod
    def _split_sections(
        lines: list[str],
    ) -> list[tuple[str, str]]:
        sections: list[tuple[str, str]] = []

        current_title: str | None = None
        current_lines: list[str] = []

        for line in lines:
            if line.startswith("## "):
                if current_title and current_lines:
                    sections.append(
                        (
                            current_title,
                            "\n".join(
                                current_lines
                            ).strip(),
                        )
                    )

                current_title = line[3:].strip()
                current_lines = []

                continue

            if line.startswith("# "):
                continue

            if line.startswith(
                "Document ID:"
            ):
                continue

            if line.startswith("Equipment:"):
                continue

            if line.startswith("Area:"):
                continue

            if line.startswith("Status:"):
                continue

            if line.startswith("Version:"):
                continue

            if line.startswith("Procedure:"):
                continue

            current_lines.append(line)

        if current_title and current_lines:
            sections.append(
                (
                    current_title,
                    "\n".join(
                        current_lines
                    ).strip(),
                )
            )

        return [
            section
            for section in sections
            if section[1]
        ]