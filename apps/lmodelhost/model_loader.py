import torch
from transformers import pipeline
from typing import Dict

def create_pipeline(model_key: str, model_id: str):
    """
    Returns a transformers pipeline instance based on the model type.
    """
    if "llama" in model_key.lower() or "text-gen" in model_key.lower():
        return pipeline(
            "text-generation",
            model=model_id,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
        )
    elif "sentiment" in model_key.lower():
        return pipeline("sentiment-analysis", model=model_id)
    else:
        return pipeline("text-generation", model=model_id)

def load_all_pipelines(model_configs: Dict[str, dict]):
    """
    Loads and returns a dict of model_key: pipeline_instance for all enabled models.
    """
    return {k: create_pipeline(k, v["model_id"]) for k, v in model_configs.items()}
