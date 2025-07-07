import os
from typing import Dict, List

def get_enabled_models() -> Dict[str, dict]:
    """
    Reads the ENABLED_MODELS environment variable from .env and returns a dict of model configs.
    Example .env:
    ENABLED_MODELS=llama,sentiment
    LLAMA_MODEL_ID=meta-llama/Meta-Llama-3.1-8B-Instruct
    SENTIMENT_MODEL_ID=distilbert-base-uncased-finetuned-sst-2-english
    """
    enabled = os.getenv("ENABLED_MODELS", "").split(",")
    enabled = [e.strip() for e in enabled if e.strip()]
    configs = {}
    for model in enabled:
        env_key = f"{model.upper()}_MODEL_ID"
        model_id = os.getenv(env_key)
        if model_id:
            configs[model] = {"model_id": model_id}
    return configs
