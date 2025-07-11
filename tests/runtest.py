import os
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = "gemini-embedding-001"
DIMENSIONALITY = 3072

from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(
    api_key=os.environ['PINECONE_API']
    )

spec = ServerlessSpec(cloud="aws", region="us-east-1")

index_name = "mmi-gemini-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(name=index_name, spec=spec, dimension=3072, metric="cosine")

def embed_text(
    texts: list[str],
    task: str = "RETRIEVAL_DOCUMENT",
    model_name: str = "gemini-embedding-001",
    dimensionality: int | None = 3072,
) -> list[list[float]]:
    """Embeds texts with a pre-trained, foundational model."""
    model = TextEmbeddingModel.from_pretrained(model_name)
    kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}

    embeddings = []
    for text in texts:
        text_input = TextEmbeddingInput(text, task)
        embedding = model.get_embeddings([text_input], **kwargs)
        print(f"Embedding for: {text[:50]}...")  # show a preview
        embeddings.append(embedding[0].values)

    return embeddings

def load_texts_from_file(file_path: str) -> list[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
