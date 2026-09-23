import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.embedding_model = None
        self.dimension = 384
        self.index = None
        self.documents = []
        self.is_initialized = False
        self._reader = None

    def _get_embedding_model(self):
        if self.embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        return self.embedding_model

    def reset(self):
        self.documents = []
        self.index = None
        self.is_initialized = False

    def extract_text(self, file, file_name):
        """Extract text from PDF, DOCX, TXT, or Images."""
        ext = file_name.split('.')[-1].lower()
        
        if ext == 'pdf':
            try:
                import fitz  # PyMuPDF
                file_bytes = file.read()
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                text = "\n".join([page.get_text() for page in doc])
                return text
            except Exception as e:
                logger.error(f"Error reading PDF {file_name}: {e}")
                return ""
                
        elif ext in ['docx', 'doc']:
            try:
                from docx import Document
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_file:
                    for chunk in file.chunks():
                        temp_file.write(chunk)
                    temp_path = temp_file.name
                
                doc = Document(temp_path)
                text = "\n".join([p.text for p in doc.paragraphs])
                os.unlink(temp_path)
                return text
            except Exception as e:
                logger.error(f"Error reading DOCX {file_name}: {e}")
                return ""
                
        elif ext == 'txt':
            try:
                return file.read().decode('utf-8')
            except Exception:
                return file.read().decode('latin-1')

        elif ext in ['html', 'htm']:
            try:
                from bs4 import BeautifulSoup
                raw_html = file.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(raw_html, "html.parser")
                
                # Extract text and separate by newlines so chunks make sense
                text = soup.get_text(separator="\n", strip=True)
                return text
            except Exception as e:
                logger.error(f"Error reading HTML {file_name}: {e}")
                return ""
                
        elif ext in ['png', 'jpg', 'jpeg', 'webp']:
            try:
                import easyocr
                import tempfile
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_file:
                    for chunk in file.chunks():
                        temp_file.write(chunk)
                    temp_path = temp_file.name
                
                if not self._reader:
                    self._reader = easyocr.Reader(['en'], gpu=False)
                    
                results = self._reader.readtext(temp_path)
                os.unlink(temp_path)
                return " ".join([res[1] for res in results])
            except Exception as e:
                logger.error(f"Error reading image {file_name}: {e}")
                return ""
        return ""

    def chunk_text(self, text, chunk_size=500, overlap=50):
        """Split text into overlapping chunks."""
        if not text:
            return []
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i : i + chunk_size])
            if chunk.strip():
                chunks.append(chunk.strip())
        return chunks

    def add_context(self, files=None, text_context=""):
        """Process files and raw text, then embed and index."""
        import faiss
        
        all_chunks = []
        
        if text_context:
            all_chunks.extend(self.chunk_text(text_context))
            
        if files:
            for f in files:
                text = self.extract_text(f, f.name)
                if text:
                    all_chunks.extend(self.chunk_text(text))
                    
        if not all_chunks:
            return 0
            
        model = self._get_embedding_model()
        embeddings = model.encode(all_chunks).astype('float32')
        
        if not self.is_initialized:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            self.is_initialized = True
            
        self.index.add(embeddings)
        self.documents.extend(all_chunks)
        
        return len(all_chunks)

    def search(self, query, top_k=3):
        """Find the most relevant chunks for a query."""
        if not self.is_initialized or len(self.documents) == 0:
            return []
            
        model = self._get_embedding_model()
        query_embedding = model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.documents):
                results.append(self.documents[idx])
        return results