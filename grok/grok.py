import argparse
import requests
import sys
import os
import json


def api() -> str:
    api: str = os.getenv("GROK_API", "")
    if not api:
        raise ValueError("api not available")
    return api


def load_chat(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []


def save_chat(filename, chat_thread):
    with open(filename, "w") as f:
        json.dump(chat_thread, f)


def stream_response(api_url, headers, prompt):
    # Stream response from API and print tokens as received
    response = requests.post(
        api_url, headers=headers, json={"prompt": prompt, "stream": True}, stream=True
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    for line in response.iter_lines():
        if line:
            try:
                # Assuming the API sends tokens line by line
                token = line.decode("utf-8")
                print(token, end="", flush=True)
            except Exception:
                continue


def main():
    parser = argparse.ArgumentParser(description="Shell-GPT App")
    parser.add_argument(
        "payload", type=str, nargs="?", default=None, help="Input prompt for the model"
    )
    parser.add_argument(
        "--chats", type=str, help="Chat name for storing/recalling conversation"
    )
    parser.add_argument("--prompt", type=str, help="Modify prompt before sending")
    args = parser.parse_args()

    api_url = (
        "https://grok-backend-api.example.com/generate"  # Replace with actual API URL
    )
    headers = {
        "Authorization": f"Bearer {api}"  # Replace with your API key
    }

    chat_history = []

    # Load existing chat if chat flag is used
    if args.chats:
        chat_filename = f"{args.chats}.json"
        chat_history = load_chat(chat_filename)

    # Use previous chat context if available
    context = ""
    if chat_history:
        context = "\n".join(chat_history)

    # Determine payload
    if args.payload:
        prompt = args.payload
    elif context:
        prompt = context
    else:
        prompt = sys.stdin.read()

    # Apply prompt modification if provided
    if args.prompt:
        prompt = args.prompt + "\n" + prompt

    # Append prompt to chat history
    if args.chats:
        chat_history.append(prompt)

    # Send prompt and stream response
    # Including chat context if applicable
    full_prompt = prompt
    stream_response(api_url, headers, full_prompt)

    # Save chat if chat flag used
    if args.chats:
        save_chat(chat_filename, chat_history)


if __name__ == "__main__":
    main()
