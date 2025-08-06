# main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Imports from App 1 (Summarizer) ---
import fitz  # PyMuPDF for PDF handling
import faiss
import numpy as np
import ollama
from gtts import gTTS
import uuid
from pathlib import Path
import logging

# --- Imports from App 2 (RAG/Risk) ---
from rag_pipeline import RAGPipeline
from risk_assessor import RiskAssessor
from test import text_to_pdf
# from pdf_processor import extract_text_from_pdf # This is now handled by PDFProcessor class
import io
import os
import time

# --- 1. Basic App Configuration ---

# Configure logging (from App 1)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI App and add CORS middleware (from App 2)
app = FastAPI(title="Integrated Legal AI Assistant", version="2.0.0")

origins = [
    "*"  # Allows all origins for development. Restrict this in production!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create and mount static directories for temporary files (from App 1)
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
app.mount("/temp", StaticFiles(directory="temp"), name="temp")


# --- 2. Helper Classes and Initializations ---

# PDFProcessor Class from App 1 (handles summarization and text-to-speech)
class PDFProcessor:
    """Class to handle PDF processing, summarization, and TTS"""

    @staticmethod
    def extract_text_from_pdf(pdf_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            text = "\n".join(page.get_text("text") for page in doc)
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise HTTPException(status_code=400, detail="Error processing PDF file")

    @staticmethod
    def split_text(text: str, chunk_size: int = 500) -> list:
        """Split text into chunks"""
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    @staticmethod
    def store_embeddings(text_chunks: list):
        """Store embeddings using FAISS (placeholder implementation)"""
        # Note: This is a placeholder. A real implementation would generate embeddings.
        dimension = 768  # Adjust based on the embedding model
        index = faiss.IndexFlatL2(dimension)
        stored_chunks = text_chunks
        return index, stored_chunks

    @staticmethod
    def retrieve_top_chunks(query: str, stored_chunks: list, top_k: int = 3) -> str:
        """Retrieve top text chunks (simple implementation)"""
        # Note: This is a placeholder. A real implementation would use the FAISS index.
        return " ".join(stored_chunks[:top_k])

    @staticmethod
    def summarize_text(text: str) -> str:
        """Summarize text using Ollama"""
        try:
            response = ollama.chat(
                model="mistral",
                messages=[{"role": "user", "content": f"Summarize this text in a clear and concise way: {text}"}]
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            # Fallback summary if Ollama is not available
            sentences = text.split('. ')
            return '. '.join(sentences[:3]) + "..." if len(sentences) > 3 else text

    @staticmethod
    def text_to_speech(text: str) -> str:
        """Convert text to speech and return filename"""
        try:
            tts = gTTS(text=text, lang="en")
            filename = f"{uuid.uuid4()}.mp3"
            filepath = TEMP_DIR / filename
            tts.save(str(filepath))
            return filename
        except Exception as e:
            logger.error(f"Error converting text to speech: {e}")
            raise HTTPException(status_code=500, detail="Error generating audio")

# Initialize all required components
pdf_processor = PDFProcessor()
rag_pipeline = RAGPipeline(faiss_index_path="faiss_index")
risk_assessor = RiskAssessor()

# --- 3. Pydantic Models for Request Bodies (from App 2) ---

class ClauseRequest(BaseModel):
    prompt: str

class PdfRequest(BaseModel):
    clause: str

class EvaluationResponse(BaseModel):
    clause: str
    risk: str
    classification: str
    source: str
    feedback_options: list[str]


# --- 4. API Endpoints ---

# Endpoint to serve the HTML Frontend (from App 1)
@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the main HTML page for the PDF Summarizer"""
    # The entire HTML, CSS, and JS is contained in this string.
    # No separate .html file is needed.
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI-Powered PDF Summarizer</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .animate-fadeInUp { animation: fadeInUp 0.8s ease-out forwards; }
            .glass-effect {
                backdrop-filter: blur(16px);
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .hero-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .drag-drop-zone {
                border: 3px dashed rgba(255, 255, 255, 0.3);
                transition: all 0.3s ease;
            }
            .drag-drop-zone:hover, .drag-drop-zone.dragover {
                border-color: rgba(255, 193, 7, 0.6);
                background: rgba(255, 255, 255, 0.05);
            }
            .summary-container, .loading-spinner { display: none; }
        </style>
    </head>
    <body class="hero-bg min-h-screen text-white">
        <div class="content-layer container mx-auto px-6 py-12">
            <div class="text-center mb-12 animate-fadeInUp">
                <h1 class="text-5xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-orange-400">
                    📄 AI-Powered PDF Summarizer 🎤
                </h1>
                <p class="text-xl text-white/80">Upload a PDF file to generate a summary and listen to it!</p>
            </div>
            <div class="max-w-4xl mx-auto">
                <div class="glass-effect rounded-2xl p-8 mb-8">
                    <div id="uploadZone" class="drag-drop-zone rounded-2xl p-12 text-center cursor-pointer">
                        <input type="file" id="fileInput" accept=".pdf" class="hidden">
                        <svg class="w-16 h-16 mx-auto mb-4 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
                        <h3 class="text-2xl font-semibold mb-2">Upload PDF File</h3>
                        <p class="text-white/70">Drag and drop, or click to browse</p>
                    </div>
                </div>
                <div id="loadingSpinner" class="loading-spinner text-center mb-8">
                    <div class="glass-effect rounded-2xl p-8"><div class="flex items-center justify-center space-x-3"><svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-yellow-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg><span class="text-xl font-medium">Processing PDF...</span></div></div>
                </div>
                <div id="summaryContainer" class="summary-container">
                    <div class="glass-effect rounded-2xl p-8 mb-6">
                        <h2 class="text-2xl font-bold mb-6">📑 Summary</h2>
                        <div id="summaryText" class="text-white/90 text-lg leading-relaxed"></div>
                    </div>
                    <div id="audioContainer" class="glass-effect rounded-2xl p-8">
                        <h3 class="text-xl font-bold mb-4">🎧 Listen to Summary</h3>
                        <audio id="audioPlayer" controls class="w-full"></audio>
                    </div>
                </div>
                <div id="errorContainer" class="hidden"><div class="bg-red-500/10 border border-red-500/20 rounded-2xl p-6"><div class="flex items-center"><svg class="w-6 h-6 text-red-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg><div><h3 class="text-red-400 font-semibold">Error</h3><p id="errorMessage" class="text-red-300"></p></div></div></div></div>
            </div>
        </div>
        <script>
            const uploadZone = document.getElementById('uploadZone');
            const fileInput = document.getElementById('fileInput');
            const loadingSpinner = document.getElementById('loadingSpinner');
            const summaryContainer = document.getElementById('summaryContainer');
            const summaryText = document.getElementById('summaryText');
            const audioPlayer = document.getElementById('audioPlayer');
            const errorContainer = document.getElementById('errorContainer');
            const errorMessage = document.getElementById('errorMessage');

            uploadZone.addEventListener('click', () => fileInput.click());
            uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
            uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
                if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
            });
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) handleFile(e.target.files[0]);
            });

            async function handleFile(file) {
                if (file.type !== 'application/pdf') {
                    showError('Please select a PDF file.');
                    return;
                }
                hideError();
                showLoading();
                const formData = new FormData();
                formData.append('file', file);
                try {
                    const response = await fetch('/upload-pdf/', { method: 'POST', body: formData });
                    if (!response.ok) {
                        const errData = await response.json();
                        throw new Error(errData.detail || 'Failed to process PDF');
                    }
                    const data = await response.json();
                    hideLoading();
                    showSummary(data.summary, data.audio_filename);
                } catch (error) {
                    hideLoading();
                    showError('Error processing PDF: ' + error.message);
                }
            }
            function showLoading() { loadingSpinner.style.display = 'block'; summaryContainer.style.display = 'none'; }
            function hideLoading() { loadingSpinner.style.display = 'none'; }
            function showSummary(summary, audioFilename) {
                summaryText.textContent = summary;
                audioPlayer.src = `/temp/${audioFilename}`;
                summaryContainer.style.display = 'block';
            }
            function showError(message) { errorMessage.textContent = message; errorContainer.classList.remove('hidden'); }
            function hideError() { errorContainer.classList.add('hidden'); }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Endpoint for Summarizer/TTS (from App 1)
@app.post("/upload-pdf/")
async def upload_pdf_and_summarize(file: UploadFile = File(...)):
    """Process uploaded PDF, return summary and audio filename."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        pdf_content = await file.read()
        pdf_text = pdf_processor.extract_text_from_pdf(pdf_content)
        
        if not pdf_text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # This implementation summarizes the entire document text for better results.
        # The chunking/retrieval is kept for potential future RAG-based summarization.
        summary = pdf_processor.summarize_text(pdf_text)
        audio_filename = pdf_processor.text_to_speech(summary)
        
        return {
            "summary": summary,
            "audio_filename": audio_filename,
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoint for RAG-based clause evaluation (from App 2)
@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate(request: ClauseRequest):
    """Evaluates a prompt to generate and assess a legal clause."""
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    if len(request.prompt.split()) < 3:
        raise HTTPException(status_code=400, detail="Prompt is too short to be meaningful.")

    retrieved_chunks = rag_pipeline.retrieve(request.prompt)
    if not retrieved_chunks:
        raise HTTPException(status_code=404, detail="No relevant information found.")

    generated_clause = rag_pipeline.generate(request.prompt, retrieved_chunks)
    risk = risk_assessor.assess_risk(generated_clause)
    classification = risk_assessor.classify_clause(generated_clause)
    _, source = rag_pipeline.get_metadata_and_source(retrieved_chunks)

    return EvaluationResponse(
        clause=generated_clause,
        risk=risk,
        classification=classification,
        source=source,
        feedback_options=["Accept", "Re-generate", "Edit"]
    )

# Endpoint to download a clause as a PDF (from App 2)
@app.post("/download_pdf")
async def download_pdf(request: PdfRequest):
    """Generates a PDF from a given clause text."""
    if not request.clause or not request.clause.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty.")

    output_filename = "generated_clause.pdf"
    text_to_pdf(request.clause, output_filename)

    return FileResponse(
        output_filename,
        media_type='application/pdf',
        filename=output_filename
    )

# Note: The `/summarize_pdf` endpoint from App 2 was removed because the
# `/upload-pdf/` endpoint provides the same functionality plus text-to-speech,
# and is what the HTML frontend is designed to use.


# --- 5. Main Execution Block ---

if __name__ == "__main__":
    import uvicorn
    # Using 0.0.0.0 to make it accessible on your local network
    uvicorn.run(app, host="0.0.0.0", port=8000)