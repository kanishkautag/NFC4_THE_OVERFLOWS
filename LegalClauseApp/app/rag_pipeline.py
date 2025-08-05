import os

from sentence_transformers import SentenceTransformer
import pdf_processor # type: ignore
import numpy as np
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

class RAGPipeline:
    def __init__(self, pdfs_dir):
        self.pdfs_dir = pdfs_dir
        self.chunks = []
        self.index = None
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        """Initializes the RAG pipeline by processing all PDFs."""
        all_chunks = []
        for filename in os.listdir(self.pdfs_dir):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(self.pdfs_dir, filename)
                text = pdf_processor.extract_text_from_pdf(pdf_path)
                chunks = pdf_processor.chunk_text(text)
                all_chunks.extend(chunks)
        
        self.chunks = all_chunks
        embeddings = pdf_processor.create_embeddings(self.chunks)
        self.index = pdf_processor.create_faiss_index(embeddings)

    def retrieve(self, query, k=5):
        """Retrieves the top k most relevant chunks for a given query."""
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode([query])
        distances, indices = self.index.search(query_embedding, k)
        return [self.chunks[i] for i in indices[0]]

    def generate(self, query, retrieved_chunks):
        """Generates a new clause using the user's query and retrieved chunks."""
        prompt = f"**User Intent:** {query}"

        for i, chunk in enumerate(retrieved_chunks):
            prompt += f"{i+1}. {chunk}\n"

        prompt += "\n**Instructions:**\nDraft a new legal clause based on the user's intent and the provided examples. The clause should be clear, concise, and legally sound."

        llm = ChatOllama(model="mistral")
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
