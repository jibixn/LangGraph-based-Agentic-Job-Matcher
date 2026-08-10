from langchain.tools import tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_experimental.text_splitter import SemanticChunker
from tools.fs_tools import FileSystemTools
from init_rag import RAGInitializer


class RAGTool:
    def __init__(self, rag_initializer):
        self.rag_initializer = rag_initializer
    # @tool
    def retrieve_from_vector_store(self, query):     
        """Perform Similarity Search on the vector store """           
        vector_store = self.rag_initializer.get_vector_store()
        results = vector_store.similarity_search(query)
        return results




