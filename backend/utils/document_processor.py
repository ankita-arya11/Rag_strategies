from pathlib import Path
from typing import Optional
import pypdf
import docx2txt


class DocumentProcessor:
    """Process and extract text from various document formats"""
    
    SUPPORTED_FORMATS = {'.pdf', '.txt', '.docx', '.doc'}
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a document file.
        
        Supports: PDF, TXT, DOCX
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {extension}")
        
        if extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif extension == '.txt':
            return self._extract_from_txt(file_path)
        elif extension in {'.docx', '.doc'}:
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"No extraction method for {extension}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            reader = pypdf.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            text = docx2txt.process(file_path)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    def get_document_metadata(self, file_path: str) -> dict:
        """Get metadata about a document"""
        path = Path(file_path)
        
        metadata = {
            "filename": path.name,
            "extension": path.suffix,
            "size_bytes": path.stat().st_size,
            "created_at": path.stat().st_ctime,
            "modified_at": path.stat().st_mtime
        }
        
        # Try to get text length
        try:
            text = self.extract_text(file_path)
            metadata["text_length"] = len(text)
            metadata["word_count"] = len(text.split())
        except:
            pass
        
        return metadata
