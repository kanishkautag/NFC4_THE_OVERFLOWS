import os

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()
from langchain_core.messages import HumanMessage

class RAGPipeline:
    def __init__(self, faiss_index_path="../faiss_index"):
        self.faiss_index_path = faiss_index_path
        self.index = None
        self.embeddings_model = None # Initialize embeddings model once
        self.llm = None
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        """Initializes the RAG pipeline by loading the pre-built FAISS index."""
        # Initialize Google Generative AI Embeddings model for query embedding
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it.")
        self.embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)

        # Load the pre-built FAISS index
        if not os.path.exists(self.faiss_index_path):
            raise FileNotFoundError(f"FAISS index not found at {self.faiss_index_path}. Please run create_index.py first.")
        
        # When loading, we need to provide the embeddings model that was used to create the index
        self.index = FAISS.load_local(self.faiss_index_path, self.embeddings_model, allow_dangerous_deserialization=True)

    def retrieve(self, query, k=5):
        """Retrieves the top k most relevant chunks for a given query using the loaded FAISS index."""
        # Use the loaded FAISS index's similarity search
        docs = self.index.similarity_search(query, k=k)
        return docs

    def generate(self, query, retrieved_chunks):
        """Generates a new clause using the user's query and retrieved chunks."""
        prompt = f"**User Intent:** {query}"

        for i, doc in enumerate(retrieved_chunks):
            prompt += f"{i+1}. {doc.page_content}\n"

        prompt += """
**Instructions:**
- Based solely on the user’s intent and the examples provided above, draft a clear, concise, and legally sound clause.
- Retrieve supporting examples from your RAG index **only if** they directly illustrate or inform the user’s specific request.
- Do **not** include any irrelevant or tangential fragments.
- Do not give irrelevant references or contexts which are not related to the prompt/topic or arent covered in the corpus.
- Attribute any borrowed language or structure from retrieved examples by noting “[Adapted from Example X]” in brackets.
"""


        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def get_metadata_and_source(self, retrieved_chunks):
        if not retrieved_chunks:
            return None, None

        # Assuming the source is stored in the metadata of the retrieved documents
        # and all chunks come from the same source.
        first_chunk = retrieved_chunks[0]
        metadata = first_chunk.metadata if hasattr(first_chunk, 'metadata') else {}
        source = metadata.get('source', 'Unknown')
        return metadata, source

    def summarize_text(self, text: str) -> str:
        """Summarizes the given text using the LLM."""
        prompt = f"""
        Please summarize the following text concisely and accurately.
        Text:
        {text}
        Summary:
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
