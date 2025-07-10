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
if index_name not in pc.list_indexes():
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

if __name__ == "__main__":
    # Path to your .txt file (each line is a separate text)
#     file_path = r"C:\Users\khant\projects\ShakeMap\data\mmi_table.txt"  # <- change to your actual file

#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"File not found: {file_path}")

#     texts = load_texts_from_file(file_path)

#     # Choose appropriate task
#     task = "RETRIEVAL_DOCUMENT"  # or "CODE_RETRIEVAL_QUERY", etc.

#     embeddings = embed_text(
#         texts=texts,
#         task=task,
#         model_name=MODEL_NAME,
#         dimensionality=DIMENSIONALITY
#     )

#     print(embeddings)

    index = pc.Index(index_name)

# # Create IDs like "mmi-0", "mmi-1", etc.
#     items_to_upsert = [
#         (f"mmi-{i}", embedding, {"text": text})
#         for i, (embedding, text) in enumerate(zip(embeddings, texts))
#     ]

#     index.upsert(vectors=items_to_upsert)
#     print(f"Upserted {len(items_to_upsert)} items into Pinecone.")

    # Embed query
    query = "I felt dizzy from earthquake"
    query_emb = embed_text([query], task="RETRIEVAL_QUERY")[0]

    # Search in Pinecone
    result = index.query(vector=query_emb, top_k=3, include_metadata=True)

    print(result)

    for match in result["matches"]:
        print(f"Score: {match['score']:.4f} | Text: {match['metadata']['text']}")
