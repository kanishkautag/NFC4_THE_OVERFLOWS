import os

from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
import numpy as np
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage

class RAGPipeline:
    def __init__(self, faiss_index_path="../faiss_index"):
        self.faiss_index_path = faiss_index_path
        self.index = None
        self.embeddings_model = None # Initialize embeddings model once
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        """Initializes the RAG pipeline by loading the pre-built FAISS index."""
        # Initialize Google Generative AI Embeddings model for query embedding
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it.")
        self.embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)

        # Load the pre-built FAISS index
        if not os.path.exists(self.faiss_index_path):
            raise FileNotFoundError(f"FAISS index not found at {self.faiss_index_path}. Please run create_index.py first.")
        
        # When loading, we need to provide the embeddings model that was used to create the index
        self.index = FAISS.load_local(self.faiss_index_path, self.embeddings_model, allow_dangerous_deserialization=True)

    def retrieve(self, query, k=5):
        """Retrieves the top k most relevant chunks for a given query using the loaded FAISS index."""
        # Use the loaded FAISS index's similarity search
        docs = self.index.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

    def generate(self, query, retrieved_chunks):
        """Generates a new clause using the user's query and retrieved chunks."""
        prompt = f"**User Intent:** {query}"

        for i, chunk in enumerate(retrieved_chunks):
            prompt += f"{i+1}. {chunk}\n"

        prompt += "\n**Instructions:**\nDraft a new legal clause based on the user's intent and the provided examples. The clause should be clear, concise, and legally sound."

        llm = ChatOllama(model="mistral")
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
