from flask import Flask, render_template, request, jsonify
import os
from rag_pipeline import RAGPipeline
from risk_assessor import RiskAssessor # Import RiskAssessor

app = Flask(__name__)

# Initialize RAGPipeline with the path to the FAISS index
rag_pipeline = RAGPipeline(faiss_index_path="../faiss_index")
risk_assessor = RiskAssessor() # Initialize RiskAssessor

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
    
    # Assess the risk of the generated clause
    risk_assessment = risk_assessor.assess_risk(generated_clause, user_prompt)
    risk_level = risk_assessment.get("risk_level", "Unknown")
    reasoning = risk_assessment.get("reasoning", "No reasoning provided.")

    print(f"Generated Clause: {generated_clause}") # Add this line for debugging
    print(f"Risk Level: {risk_level}")
    print(f"Reasoning: {reasoning}")

    return jsonify({
        "clause": generated_clause,
        "risk_level": risk_level,
        "reasoning": reasoning
    })

if __name__ == '__main__':
    app.run(debug=True)
