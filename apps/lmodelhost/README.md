# lmodelhost

A FastAPI service for hosting a local Hugging Face model.

## Features
- Health check endpoint
- Placeholder for model inference using Hugging Face Transformers

## Requirements
- Python (managed by UV)
- FastAPI
- pydantic
- poe (task runner)
- huggingface/transformers

## Usage

1. Install dependencies:
   ```sh
   uv pip install -r requirements.txt
   ```
2. Run the server:
   ```sh
   poe serve
   ```

## Development
- Add your model loading and inference logic in `main.py`.
