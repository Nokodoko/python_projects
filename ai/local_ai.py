#!/usr/bin/env python3
from langchain_core.messages import HumanMessage
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatMessagePromptTemplate

model = OllamaLLM(model="llama3.2")
template = f"""
    You are an expert in answering questions.
    Here are some reviews: {reviews}

    Here is a question to answer: {question}

    """
# NOTE: need to define reviews and question

messages = [
    HumanMessage("You are ..."),
    HumanMessage("You are ..."),
    HumanMessage("You are ..."),
    HumanMessage("You are ..."),
    HumanMessage("You are ..."),
]

prompt = ChatMessagePromptTemplate(template)
chain = prompt | model

while True:
    print("\n\n--------------------")
    question = input("Ask your question (q to quit)")
    if question == "q":
        break

    chain.invoke({"reviews": [], "question": question})
    print(result)  # NOTE: need to defined result
