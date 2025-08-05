<<<<<<< Updated upstream
# RAG Clause Generator

A Python-based web application that uses Retrieval-Augmented Generation (RAG) to generate legal clauses from a database of contract documents.

## Features

- **RAG-powered clause generation**: Uses semantic search to find relevant contract context
- **Multiple LLM support**: Works with Google Gemini API or OpenAI GPT-4
- **Document chunking**: Splits contracts into 500-token chunks with 50-token overlap
- **Semantic search**: Uses SentenceTransformers for embedding and cosine similarity
- **Modern web interface**: Beautiful, responsive UI with real-time generation
- **Output formatting**: Saves generated clauses to `output.txt` with proper formatting
- **Diverse outputs**: Generates 5 different clauses per query, shuffled for variety

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. API Keys Setup

You need to set up API keys for either Google Gemini or OpenAI. Create a `.env` file in the project root:

#### Option A: Google Gemini (Recommended - Free Tier Available)
```bash
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Option B: OpenAI GPT-4
```bash
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Free API Options

#### Google Gemini (Recommended)
- **Free tier**: 15 requests per minute, 1500 requests per day
- **Cost**: Free for most use cases
- **Setup**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your API key

#### OpenAI GPT-4
- **Free tier**: $5 credit for new users
- **Cost**: ~$0.03 per 1K tokens
- **Setup**: Visit [OpenAI Platform](https://platform.openai.com/api-keys) to get your API key

### 4. Run the Application

```bash
python app.py
```

The web application will be available at `http://localhost:5000`

## Usage

1. **Open the web interface** in your browser
2. **Enter your query** describing the type of clause you need
3. **Click "Generate Clauses"** to start the RAG process
4. **View results** in the web interface and check `output.txt` for saved output

### Example Queries

- "Draft a mutual NDA clause for a SaaS partnership"
- "Create a non-compete clause for software developers"
- "Generate a data protection clause for cloud services"
- "Write a termination clause for consulting agreements"
- "Draft an intellectual property assignment clause"

## How It Works

### 1. Document Processing
- Loads all `.txt` files from `full_contract_txt/` directory
- Splits each document into 500-token chunks with 50-token overlap
- Creates embeddings using SentenceTransformers (`all-MiniLM-L6-v2`)

### 2. Retrieval-Augmented Generation
- User query is embedded using the same model
- Top 10 most relevant chunks are retrieved using cosine similarity
- Context is provided to the LLM for clause generation

### 3. Clause Generation
- LLM generates 5 diverse clauses (50-120 words each)
- Clauses are shuffled for variety
- Results are saved to `output.txt` and displayed in the web interface

## File Structure

```
NFC4_THE_OVERFLOWS/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # API keys (create this)
├── output.txt            # Generated clauses (created automatically)
├── templates/
│   └── index.html        # Web interface
├── full_contract_txt/    # Contract documents
└── README.md            # This file
```

## API Endpoints

- `GET /` - Web interface
- `POST /generate` - Generate clauses
- `GET /health` - Health check

## Technical Details

### Embedding Model
- **Model**: `all-MiniLM-L6-v2` (SentenceTransformers)
- **Dimensions**: 384
- **Performance**: Fast and accurate for semantic search

### Text Chunking
- **Chunk size**: 500 tokens
- **Overlap**: 50 tokens
- **Tokenizer**: tiktoken (cl100k_base)

### LLM Configuration
- **Gemini**: `gemini-pro` model
- **OpenAI**: `gpt-4` model
- **Temperature**: 0.7 (for diversity)
- **Max tokens**: 1000

## Troubleshooting

### Common Issues

1. **"No API key found"**
   - Ensure you've created a `.env` file with your API key
   - Check that the API key is valid and has sufficient credits

2. **"Directory full_contract_txt not found"**
   - Ensure the contract documents are in the correct directory
   - Check file permissions

3. **"Error generating clauses"**
   - Check your internet connection
   - Verify API key has sufficient credits/quota
   - Try reducing the number of documents if memory issues occur

### Performance Tips

- **Large document sets**: Consider reducing chunk size for memory efficiency
- **Faster processing**: Use GPU if available for embedding generation
- **API costs**: Monitor usage and set up billing alerts

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for educational and research purposes.
=======
# Legal Clause Generator
>>>>>>> Stashed changes

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
