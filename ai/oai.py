#!/bin/env python3

from langchain.chat_models import ChatOpenAI
import os
from typing import List

from langchain.schema.messages import HumanMessage, SystemMessage

api_key: str = os.getenv('OPENAI_API_KEY')

chat_model: ChatOpenAI = ChatOpenAI(openai_api_key=api_key)

#multishot prompts
messages: List[str] = [
    HumanMessage(content='cumulative responses should recall that quarter: int = (5*5)'),
    HumanMessage(content='which means half: in = (10*5) '),
    HumanMessage(content='whole is 100'),
    HumanMessage(content='what is three_quarters (include type annotations)?')
]

sys_message: List[str] = [
    SystemMessage(content=)
]

result_msp: ChatOpenAI = chat_model.predict_messages(messages)
print(result_msp.content)
