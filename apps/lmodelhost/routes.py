from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict

class InferenceRequest(BaseModel):
    text: str

class InferenceResponse(BaseModel):
    result: Any

def create_model_router(model_key: str, pipe) -> APIRouter:
    router = APIRouter()
    @router.post("/infer", response_model=InferenceResponse)
    def infer(request: InferenceRequest):
        if "text-generation" in str(pipe.task):
            result = pipe(request.text, max_new_tokens=256)
        else:
            result = pipe(request.text)
        return {"result": result}
    return router
