from langchain.tools import tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_experimental.text_splitter import SemanticChunker
from tools.fs_tools import FileSystemTools
from init_rag import RAGInitializer


class RAGTool:
    def __init__(self, rag_initializer):
        self.rag_initializer = rag_initializer
    
    def retrieve_from_vector_store(self, query):     
        """Perform MMR Search on the vector store """           
        vector_store = self.rag_initializer.get_vector_store()
        results = vector_store.max_marginal_relevance_search(
            query,
            k=10,
            fetch_k=30,
            lambda_mult=0.7
        )
        return results


    @tool
    def retrieve_from_vector_store_mmr(self, query):     
        """Perform MMR Search on the vector store containing resume information"""           
        vector_store = self.rag_initializer.get_vector_store()
        results = vector_store.max_marginal_relevance_search(
            query,
            k=10,
            fetch_k=30,
            lambda_mult=0.7
        )
        return results

    @tool
    def retrieve_from_vector_store_similarity(self, query):     
        """Perform Similarity Search on the vector store containing resume information"""           
        vector_store = self.rag_initializer.get_vector_store()
        results = vector_store.similarity_search(
            query,
            k=10
        )
        return results




