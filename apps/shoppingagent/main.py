import gradio as gr
from llm_client import get_top3_items

def llm_agent(input_text):
    # Call local vLLM OpenAI API for top 3 items
    result = get_top3_items(input_text)
    return result

def human_review(items_dict):
    # Human-in-the-loop: display and allow edit/approval
    items = items_dict.get("items", [])
    if not items:
        return "No items found. Please refine your query."
    return f"[HUMAN REVIEW REQUIRED]\nTop 3 items: {', '.join(items)}"

with gr.Blocks() as demo:
    gr.Markdown("# Shopping Agent (Human-in-the-Loop Demo)")
    inp = gr.Textbox(label="Shopping Query")
    out = gr.Textbox(label="Agent Output")
    def run_pipeline(query):
        llm_out = llm_agent(query)
        human_out = human_review(llm_out)
        return human_out
    inp.submit(run_pipeline, inp, out)

demo.launch()
