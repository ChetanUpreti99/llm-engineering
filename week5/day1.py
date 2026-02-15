import os
from pathlib import Path
from dotenv import load_dotenv
from glob import glob
from openai import OpenAI
import gradio as gr

load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    print(f"OpenAI API Key exists and begins  {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")

MODEL = "gpt-4.1-nano"
openAI = OpenAI()

knowledge = {}
employeeFileNames = glob("knowledge-base/employees/*")

for employeeFile in employeeFileNames:
    name = Path(employeeFile).stem.split(' ')[-1]
    with open(employeeFile, "r", encoding="utf-8") as f:
        knowledge[name.lower()] = f.read()

productFilenames = glob("knowledge-base/products/*")

for productFile in productFilenames:
    name = Path(productFile).stem
    with open(productFile, "r", encoding="utf-8") as f:
        knowledge[name.lower()] = f.read()


def get_relevant_context(message):
    text = ''.join(ch for ch in message if ch.isalpha() or ch.isspace())
    words = text.lower().split()
    return [knowledge[word] for word in words if word in knowledge]   


def additional_context(message):
    relevant_context = get_relevant_context(message)
    if not relevant_context:
        result = "There is no additional context relevant to the user's question."
    else:
        result = "The following additional context might be relevant in answering the user's question:\n\n"
        result += "\n\n".join(relevant_context)
    return result

SYSTEM_PREFIX = """
You represent Insurellm, the Insurance Tech company.
You are an expert in answering questions about Insurellm; its employees and its products.
You are provided with additional context that might be relevant to the user's question.
Give brief, accurate answers. If you don't know the answer, say so.

Relevant context:
"""

def chat(message, history):
    system_message = SYSTEM_PREFIX + additional_context(message)
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openAI.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

view = gr.ChatInterface(chat, type="messages").launch(inbrowser=True)