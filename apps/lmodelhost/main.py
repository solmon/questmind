import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from typing import Any

app = FastAPI()

# Placeholder: load a local Hugging Face model (update model name as needed)
# For example, use "distilbert-base-uncased-finetuned-sst-2-english" for sentiment analysis
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
nlp = pipeline("sentiment-analysis", model=model_name)

class InferenceRequest(BaseModel):
    text: str

class InferenceResponse(BaseModel):
    result: Any

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post("/infer", response_model=InferenceResponse)
def infer(request: InferenceRequest):
    result = nlp(request.text)
    return {"result": result}
