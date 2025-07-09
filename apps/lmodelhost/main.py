
import os
# os.environ["TRANSFORMERS_VERBOSITY"] = "error"
# os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"

# Load environment variables from .env file if present
from dotenv import load_dotenv
load_dotenv()

# Set Hugging Face token from environment variable if available
hf_token = os.environ.get("HUGGINGFACE_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token

# Import model config loader

from apps.lmodelhost.model_configs import get_enabled_models
from apps.lmodelhost.model_loader import load_all_pipelines
from apps.lmodelhost.routes import create_model_router, InferenceRequest, InferenceResponse
from apps.lmodelhost.vllm_rayserve import create_vllm_rayserve_router
from fastapi import FastAPI

app = FastAPI()

model_configs = get_enabled_models()
model_pipes = load_all_pipelines(model_configs)

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# Register subroutes for each enabled model
for model_key, pipe in model_pipes.items():
    # If model_key is 'deepseekqwin' or similar, use vllm+ray serve
    if "deepseek" in model_key.lower() or "qwin" in model_key.lower():
        model_id = model_configs[model_key]["model_id"]
        router = create_vllm_rayserve_router(model_id)
        app.include_router(router, prefix=f"/{model_key}")
    else:
        router = create_model_router(model_key, pipe)
        app.include_router(router, prefix=f"/{model_key}")


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


# ...existing code...
