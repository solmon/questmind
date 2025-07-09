import requests

VLLM_API_URL = "http://localhost:8000/v1/chat/completions"
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

PROMPT_TEMPLATE = (
    "You are a helpful shopping assistant. Respond ONLY with a JSON object in the following format:\n"
    "{{\n  \"items\": [\"<item1>\", \"<item2>\", \"<item3>\"]\n}}\n"
    "List the top 3 most relevant products for the following user query. Respond only with valid JSON, no extra text.\n"    
)

def get_top3_items(query: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(query=query)
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ],
        "max_tokens": 256,
        "temperature": 0.7
    }
    response = requests.post(VLLM_API_URL, json=payload, timeout=30)
    response.raise_for_status()
    result = response.json()
    print(f"LLM response: {result}")  # Debugging output
    # Extract the model's reply (OpenAI format)
    content = result["choices"][0]["message"]["content"]
    try:
        import re, json
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                return {"items": []}
        return {"items": []}
    except Exception:
        return {"items": []}
