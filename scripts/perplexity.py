#!/usr/bin/env python3
from openai import OpenAI
import os
from helpers import dmenu
from typing import List, Dict

API_KEY: str = os.getenv('PERPLEXITY', '')
if not API_KEY:
    raise ValueError("PERPLEXITY api key is not available")


def messages(query: str) -> List[Dict[str, str]]:
    return [{
        "role": "system",
        "content": (
            "You are an artificial intelligence assistant and you need to "
            "engage in a helpful, detailed, polite conversation with a user."
        ),
    },
    {
        "role": "user",
        "content": (
            f"{query}"
        ),
    },
]

client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai")

# chat completion without streaming
# response = client.chat.completions.create(
#    model="mistral-7b-instruct",
#    messages=messages,
# )
# print(response)

# chat completion with streaming
response_stream = client.chat.completions.create(
    model="mistral-7b-instruct",
    messages=messages,
    stream=True,
)
for response in response_stream:
    print(response)
