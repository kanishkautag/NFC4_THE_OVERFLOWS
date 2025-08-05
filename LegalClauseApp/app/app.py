from flask import Flask, render_template, request, jsonify
import os
from rag_pipeline import RAGPipeline

app = Flask(__name__)

# Initialize RAGPipeline
PDFS_DIR = "C:/Users/Ankit Prasad/Documents/GitHub/NFC4_THE_OVERFLOWS/LegalClauseApp/pdfs"
rag_pipeline = RAGPipeline(PDFS_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_clause', methods=['POST'])
def generate_clause():
    user_prompt = request.json.get('prompt')
    
    if not user_prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Retrieve relevant chunks using the RAG pipeline
    retrieved_chunks = rag_pipeline.retrieve(user_prompt)
    
    # Generate the clause using the RAG pipeline
    generated_clause = rag_pipeline.generate(user_prompt, retrieved_chunks)
    
    # For now, we'll return only the generated clause as per the updated request
    print(f"Generated Clause: {generated_clause}") # Add this line for debugging
    return jsonify({
        "clause": generated_clause
    })

if __name__ == '__main__':
    app.run(debug=True)
