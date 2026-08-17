from pypdf import PdfReader
from pathlib import Path
from langchain.tools import tool
from langchain_core.documents import Document


class FileSystemTools:           

    
    def extract_info(self, file_path: str) -> Document:
        """Extract text from a PDF file and return it as a LangChain Document."""
        content = ""
        reader = PdfReader(file_path)
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                content += text + "\n"
        return Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "resume": Path(file_path).stem
            }
        )
        
    @tool
    def extract_info_tool(self, file_path: str) -> Document:
        """Extract text from a PDF file and return it as a LangChain Document."""
        content = ""
        reader = PdfReader(file_path)
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                content += text + "\n"
        return Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "resume": Path(file_path).stem
            }
        )
