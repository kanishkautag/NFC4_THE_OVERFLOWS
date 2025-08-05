from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_pipeline import RAGPipeline
from fastapi.responses import FileResponse
from risk_assessor import RiskAssessor

app = FastAPI()

# Initialize RAGPipeline with the path to the FAISS index
rag_pipeline = RAGPipeline(faiss_index_path="faiss_index")
risk_assessor = RiskAssessor()

class ClauseRequest(BaseModel):
    prompt: str

class EvaluationResponse(BaseModel):
    clause: str
    risk: str
    classification: str
    source: str
    feedback_options: list[str]

@app.get("/")
def read_root():
    return FileResponse('templates/index.html')

@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate(request: ClauseRequest):
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    # Basic check for nonsensical prompts
    if len(request.prompt.split()) < 3:
        raise HTTPException(status_code=400, detail="Prompt is too short to be meaningful.")

    retrieved_chunks = rag_pipeline.retrieve(request.prompt)
    if not retrieved_chunks:
        raise HTTPException(status_code=404, detail="No relevant information found to generate a clause.")

    best_clause = None
    best_risk = "Very High" # Initialize with the highest possible risk
    best_classification = None
    best_source = None

    for i in range(10): # Max 10 iterations
        generated_clause = rag_pipeline.generate(request.prompt, retrieved_chunks)
        risk = risk_assessor.assess_risk(generated_clause)
        classification = risk_assessor.classify_clause(generated_clause)
        metadata, source = rag_pipeline.get_metadata_and_source(retrieved_chunks)

        # Update best result if current risk is lower or if it's the first iteration
        if risk_assessor.get_risk_level_value(risk) < risk_assessor.get_risk_level_value(best_risk):
            best_clause = generated_clause
            best_risk = risk
            best_classification = classification
            best_source = source
        
        # If desired risk level is achieved, break the loop
        if risk == "Low" or risk == "Medium":
            print(f"Optimum answer found after {i+1} iterations: Risk = {risk}")
            break
        
        # If this is the last iteration and no low/medium risk was found, use this result
        if i == 9 and (best_risk == "High" or best_risk == "Very High"):
            best_clause = generated_clause
            best_risk = risk
            best_classification = classification
            best_source = source

    return EvaluationResponse(
        clause=best_clause,
        risk=best_risk,
        classification=best_classification,
        source=best_source,
        feedback_options=["Accept", "Re-generate", "Edit"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
