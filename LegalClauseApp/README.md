# Legal Clause Generator

This is a full-stack web application that allows users to generate legal clauses from natural language intent. It uses a Retrieval-Augmented Generation (RAG) pipeline to retrieve relevant examples from a collection of legal documents and a generative model to draft the final clause.

## Features

*   **Web Interface:** A simple and user-friendly web interface for generating legal clauses.
*   **RAG Pipeline:** Uses a RAG pipeline with Sentence Transformers and FAISS for efficient retrieval of relevant clauses.
*   **Generative Model:** Uses the Gemini API to generate high-quality legal clauses.
*   **Risk Assessment:** A second agent assesses the risk of the generated clause and provides a safer alternative.
*   **Document Export:** Export the generated clauses to `.docx` and `.txt` files.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/LegalClauseApp.git
    cd LegalClauseApp
    ```

2.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Add your Gemini API Key:**
    *   Open the `app/rag_pipeline.py` and `app/risk_assessor.py` files.
    *   Replace `"YOUR_GEMINI_API_KEY"` with your actual Gemini API key.

4.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

5.  **Open your browser:**
    *   Navigate to `http://127.0.0.1:8000`

## Usage

1.  Enter your legal intent in the text area on the homepage.
2.  Click the "Generate Clause" button.
3.  The application will display the generated clause, a risk assessment, and the retrieved clauses for comparison.
4.  You can export the generated clause to a `.docx` or `.txt` file using the export buttons.
