import os
import logging
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.readers.gcs import GCSReader
from llama_index.llms.vertex import Vertex
from llama_index.embeddings.vertex import VertexTextEmbedding

#logger setup
logger = logging.getLogger(__name__)

class MMIRetriever:
    """
    Retrieves MMI scale definitions from knowledge base stored in GCS, using LlamaIndex for RAG.
    """
    def __init__(self, gcsBucket : str, blobPath : str, project_id : str, llm, embedding_model):
        """
        Constructor

        Args: 
            GCS_bucketName (str) : Name of GCS bucket where mmi_table.json is stored
            mmi_blobPath (str) : Path to mmi_table.json in the bucket
            projectID (str) : GCP project ID
        """
        self.gcsBucket=gcsBucket
        self.blobPath=blobPath
        self.project_id=project_id
        self.llm=llm
        self.embedding_model=embedding_model
      
        self._index=None
       

    def indexing(self):
        """
        reads and load data from GCS bucket and index to VectorStore
        Build new index if unsuccessful
        """
        try:
            reader = GCSReader(self.gcsBucket)
            documents = reader.load_data([self.blobPath])
            self._index = VectorStoreIndex.from_documents(documents)
            logger.info("Indexing complete..")
        except Exception as e:
            logger.error(f"Failed loading/indexing documents from GCS. {e}")
      

        return 
    

    def retrieve(self, query : str, top_k : int) -> list[str]:
        """
        Retrieve similar texts from MMI documents

        Args: 
            query (str) : user input query
            top_k (int) : number of top matches to return

        Returns:
            list[str]: List of matched texts
        """
        if(not self._index):
            raise ValueError("Empty Index")
        
        retriever = self._index.as_retriever(top_k)
        results = retriever.retrieve(query) # returns node
        return [node.get_text() for node in results]