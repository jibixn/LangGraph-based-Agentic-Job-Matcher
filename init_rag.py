from langchain.tools import tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_experimental.text_splitter import SemanticChunker
from tools.fs_tools import FileSystemTools
from pathlib import Path

class RAGInitializer:

    def __init__(self, embedding_model):
        
        self.fs_tools = FileSystemTools()
        self.embeddings = embedding_model
        self.vector_store = None
        self.text_splitter = None

    def initialize_components(self):             

        self.vector_store = Chroma(
            collection_name="resumes",
            embedding_function=self.embeddings,
            persist_directory="./chroma_langchain_db",  
        )

        text_splitter = SemanticChunker(self.embeddings)

        return self.embeddings, self.vector_store, text_splitter

    def add_to_vector_store(self, folder):

        embeddings, vector_store, text_splitter = self.initialize_components()
        folder_path = Path(folder) 
        text = ""

        for file in folder_path.glob("*.pdf"):

            text = self.fs_tools.extract_info(file)
            chunks = text_splitter.split_documents([text])

            # metadatas = [
            #     {
            #         "source": file.name,
            #         "resume": file.stem
            #     }
            #     for _ in chunks
            # ]

            vector_store.add_documents(
                documents = chunks                
            )
    def get_vector_store(self):
        return self.vector_store

