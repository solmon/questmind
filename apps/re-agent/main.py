import os
from dotenv import load_dotenv

load_dotenv()

# os.environ["CURL_CA_BUNDLE"] = "/usr/local/share/ca-certificates/trusted_certs.crt"
# os.environ["REQUESTS_CA_BUNDLE"] = "/usr/local/share/ca-certificates/trusted_certs.crt"
# os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = "/usr/local/share/ca-certificates/trusted_certs.crt"
# cat /usr/local/share/ca-certificates/trusted_certs.crt | sudo tee -a $(python3 -m certifi)

os.environ["CURL_CA_BUNDLE"] = "/home/solmon/github/questmind/zscaler_root.crt"
os.environ["REQUESTS_CA_BUNDLE"] = "/home/solmon/github/questmind/zscaler_root.crt"
os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = "/home/solmon/github/questmind/zscaler_root.crt"

# Disable Hugging Face telemetry for Gradio
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

import gradio as gr
import requests
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
import httpx
import logging
import http.client as http_client
import signal
from contextlib import contextmanager

# Enable HTTP and gRPC debug logging
http_client.HTTPSConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("grpc").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

# Example config (replace with your Gemini API key)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Configure ChatGoogleGenerativeAI with proper transport settings
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.1,
    transport="rest",  # Force REST API instead of gRPC
    client_options={"api_endpoint": "https://generativelanguage.googleapis.com"}
)

# Create a simple agent using LangGraph's prebuilt agent
agent = create_react_agent(
    model=llm,
    tools=[],  # Add tools here if needed
    prompt="You are a helpful assistant."
)

def run_agent(input_text):
    print("reached:")
    try:
        # with timeout(30):  # 30 second timeout
        response = agent.invoke({"messages": [HumanMessage(content=input_text)]})
        # The response is a dict with 'messages' key
        if isinstance(response, dict) and "messages" in response:
            return response["messages"][-1].content
        print("Response:", response)
        return str(response)
    # except TimeoutError:
    #     return "Request timed out - possible network/SSL issue"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Test the API first
    print("Testing LLM with ChatGoogleGenerativeAI...")
    try:
        test_result = llm.invoke([HumanMessage(content="Hello, just say 'ChatGoogleGenerativeAI working'")])
        print(f"LLM test result: {test_result.content}")
    except Exception as e:
        print(f"LLM test failed: {e}")
    
    demo = gr.Interface(
        fn=run_agent,
        inputs=gr.Textbox(label="Ask the agent"),
        outputs=gr.Textbox(label="Response"),
        title="re-agent: LangGraph + ChatGoogleGenerativeAI Agent",
        description="A local agent powered by LangGraph and ChatGoogleGenerativeAI with proper SSL config."
    )
    demo.launch()

if __name__ == "__main__":
    main()
