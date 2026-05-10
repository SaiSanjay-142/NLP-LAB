import os
import re
import pandas as pd
from typing import List, Dict
from PyPDF2 import PdfReader
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class TFIDFSearchEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.documents: List[str] = []
        self.doc_metadata: List[Dict[str, str]] = []
        self.tfidf_matrix = None
        self.stop_words = set(stopwords.words('english'))

    def preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        tokens = word_tokenize(text)
        filtered_tokens = [word for word in tokens if word not in self.stop_words]
        return " ".join(filtered_tokens)

    def extract_text_from_pdf(self, file_stream) -> str:
        text = ""
        try:
            reader = PdfReader(file_stream)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text

    def add_document(self, filename: str, file_stream=None, text_content: str=None):
        ext = os.path.splitext(filename)[1].lower()
        
        raw_text = ""
        if text_content is not None:
            raw_text = text_content
        elif file_stream is not None:
            if ext == '.txt':
                raw_text = file_stream.read().decode('utf-8')
            elif ext == '.pdf':
                raw_text = self.extract_text_from_pdf(file_stream)
            else:
                return False, f"Unsupported file format: {ext}"
        else:
            return False, "No content provided."
            
        if not raw_text.strip():
            return False, f"Warning: Extracted empty text from {filename}"

        cleaned_text = self.preprocess_text(raw_text)
        
        self.documents.append(cleaned_text)
        self.doc_metadata.append({
            "filename": filename,
            "snippet": raw_text[:200] + "..." if len(raw_text) > 200 else raw_text
        })
        
        # Rebuild index automatically
        self.build_index()
        return True, f"Added document: {filename}"

    def build_index(self):
        if not self.documents:
            self.tfidf_matrix = None
            return
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if self.tfidf_matrix is None:
            return []

        cleaned_query = self.preprocess_text(query)
        if not cleaned_query:
            return []

        query_vector = self.vectorizer.transform([cleaned_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        ranked_indices = similarities.argsort()[::-1]
        
        results = []
        for idx in ranked_indices[:top_k]:
            score = float(similarities[idx])
            if score > 0.0:
                results.append({
                    "filename": self.doc_metadata[idx]["filename"],
                    "score": round(score, 4),
                    "snippet": self.doc_metadata[idx]["snippet"]
                })
                
        return results

# Global singleton instance
engine = TFIDFSearchEngine()
