from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_embedding_model():

    global _model

    if _model is None:

        print(
            "Loading embedding model..."
        )

        _model = SentenceTransformer(
            MODEL_NAME
        )

        print(
            "Embedding model loaded."
        )

    return _model


def create_embeddings(texts):

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    return embeddings