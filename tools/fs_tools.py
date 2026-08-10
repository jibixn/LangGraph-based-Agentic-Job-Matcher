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
            # print(f"Successfully Read {file_path}")
            # print(f"Extracted characters: {len(content)}")
            # print(f"Preview: {content[:200]}")

        return Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "resume": Path(file_path).stem
            }
        )
