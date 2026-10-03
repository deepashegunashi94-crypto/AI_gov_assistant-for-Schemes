import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


DOCUMENT_FILE = Path(
    "data/schemes/rag_documents.json"
)

VECTORSTORE_DIR = Path("vectorstore")

INDEX_FILE = VECTORSTORE_DIR / "schemes.index"
METADATA_FILE = VECTORSTORE_DIR / "metadata.json"


MODEL_NAME = "all-MiniLM-L6-v2"


def main():

    print("Loading RAG documents...")

    with open(
        DOCUMENT_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        documents = json.load(f)

    print(
        f"Documents loaded: {len(documents)}"
    )


    # Extract text
    texts = [
        document["text"]
        for document in documents
    ]


    print("\nLoading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME
    )


    print("Creating embeddings...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )


    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )


    print(
        f"Embeddings created: "
        f"{embeddings.shape}"
    )


    # Create FAISS index
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(embeddings)


    print(
        f"FAISS vectors: {index.ntotal}"
    )


    # Create vectorstore directory
    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # Save FAISS index
    faiss.write_index(
        index,
        str(INDEX_FILE)
    )


    # Save metadata
    metadata = []

    for document in documents:

        metadata.append({
            "id": document.get("id"),
            "schemeName": document.get(
                "schemeName"
            ),
            "slug": document.get(
                "slug"
            ),
            "category": document.get(
                "category"
            ),
            "state": document.get(
                "state"
            ),
            "text": document.get(
                "text"
            )
        })


    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=2,
            ensure_ascii=False
        )


    print("\n" + "=" * 60)
    print("RAG BUILD COMPLETED")
    print("=" * 60)

    print(
        f"Documents: {len(documents)}"
    )

    print(
        f"Vectors: {index.ntotal}"
    )

    print(
        f"Dimension: {dimension}"
    )

    print(
        f"Index: {INDEX_FILE}"
    )

    print(
        f"Metadata: {METADATA_FILE}"
    )


if __name__ == "__main__":
    main()