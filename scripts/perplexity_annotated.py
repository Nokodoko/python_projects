#!/usr/bin/env python3
import os
import json
import requests
from typing import List, Dict
from helpers import dmenu

API_KEY: str = os.getenv('PERPLEXITY', '')
if not API_KEY:
    raise ValueError("PERPLEXITY api_key is not set")
URL: str = "https://api.perplexity.ai/chat/completions"
PROMPT: str = "What is your Query?"
QUERY: List[str] = dmenu('yellow', PROMPT)

HEADERS: Dict[str, str] = {
    "accept": "application/json",
    "content-type": "application/json",
}

def messages(query: List[str]) -> List[Dict[str, str]]:
    return [
        {
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


#.ChatCompletionChunk.choices[]|.message.content
def http_request(messages: List[Dict[str, str]]) -> None:
    response_stream = requests.post(url=URL, headers=HEADERS, json=messages, stream=True)
        model="mistral-7b-instruct",
    )
    for response in response_stream:
        j_data = json.loads(response)
        j_response = [item['message']['content'] for item in j_data['ChatCompletionChunk']['choices']]
        print(j_response)

    #def http_request(messages: List[Dict[str, str]]) -> None:
    #    response_stream = client.chat.completions.create(
    #        model="mistral-7b-instruct",
    #        messages=messages,
    #        stream=True,
    #    )
    #    for response in response_stream:
    #        j_data = json.loads(response)
    #        j_response = [item['message']['content'] for item in j_data['ChatCompletionChunk']['choices']]
    #        print(j_response)


if __name__ == "__main__":
    http_request(messages(QUERY))
