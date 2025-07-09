import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

# Only import vllm and ray if available
try:
    from vllm import LLM, SamplingParams
    import ray
    from ray import serve
except ImportError:
    LLM = None
    SamplingParams = None
    ray = None
    serve = None

class InferenceRequest(BaseModel):
    text: str

class InferenceResponse(BaseModel):
    result: Any

def create_vllm_rayserve_router(model_id: str) -> APIRouter:
    router = APIRouter()
    llm = None
    # Set vLLM concurrency and memory utilization for small GPU
    os.environ["VLLM_MAX_CONCURRENT_REQUESTS"] = "1"
    os.environ["VLLM_GPU_MEMORY_UTILIZATION"] = os.getenv("VLLM_GPU_MEMORY_UTILIZATION", "0.6")
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"
    # You can further tune parameters below for your GPU
    # llm_kwargs = {
    #     "max_num_batched_tokens": 2048,  # reduce if OOM
    #     "max_num_seqs": 1,               # only 1 concurrent sequence
    #     "dtype": "auto",                # let vllm pick best dtype
    # }
    llm_kwargs = {
        "max_num_batched_tokens": 1024,
        "max_num_seqs": 1,
        # "dtype": "float16",
        # "swap_space": 8,  # 8 GiB swap, adjust as needed
        "tensor_parallel_size": 2,
        "max_model_len": 32768,
        "enforce_eager": True,
    }
    sampling_params = SamplingParams(max_tokens=256) if SamplingParams else None

    @router.on_event("startup")
    async def startup_event():
        nonlocal llm
        if ray and serve and LLM:
            if not ray.is_initialized():
                ray.init()
            llm = LLM(model=model_id, **llm_kwargs)

    @router.post("/infer", response_model=InferenceResponse)
    async def infer(request: InferenceRequest):
        if not llm:
            return {"result": "Model not loaded or vllm/ray not installed."}
        outputs = llm.generate([request.text], sampling_params)[0].outputs[0].text
        return {"result": outputs}

    return router
