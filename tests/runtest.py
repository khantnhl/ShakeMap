import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.credentialUtils import get_credentials
from agents.MMIRetriever import MMIRetriever
from llama_index.llms.vertex import Vertex
from llama_index.embeddings.vertex import VertexTextEmbedding

llm = Vertex(model="gemini-2.5-flash", project="gen-lang-client-0175492774", credentials=get_credentials())

embedder = VertexTextEmbedding(project="gen-lang-client-0175492774", credentials=get_credentials())

retriever = MMIRetriever(
    gcsBucket="earthquake_bukt",
    blobPath="mmi/mmi_table.json",
    project_id="gen-lang-client-0175492774",
    llm=llm,
    embedding_model=embedder
)

retriever.indexing()
retriever.retrieve(query="")