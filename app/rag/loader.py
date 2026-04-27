from pathlib import Path


def load_documents(folder_path: str) -> list[dict]:
    documents = []

    folder = Path(folder_path)

    for file in folder.glob("*.txt"):
        content = file.read_text(encoding="utf-8")

        documents.append(
            {
                "source": file.name,
                "content": content,
            }
        )

    return documents