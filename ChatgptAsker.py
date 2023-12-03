import os

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

import streamlit as st

GPT_MODEL = st.secrets["GPT_MODEL"]
MAX_TOKEN_LENGTH_WITHOUT_FUNCTION = int(
    st.secrets["MAX_TOKEN_LENGTH_WITHOUT_FUNCTION"]
)
MAX_TOKEN_LENGTH_WITH_FUNCTION = int(st.secrets["MAX_TOKEN_LENGTH_WITH_FUNCTION"])

import time
import openai
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken


class ChatgptAnswer:
    def __init__(self, arg):
        if arg["choices"][0]["finish_reason"] == "function_call":
            self.kind = "function"
            self.func_name = arg["choices"][0]["message"]["function_call"]["name"]

            import json

            self.func_param = json.loads(
                arg["choices"][0]["message"]["function_call"]["arguments"]
            )
        else:
            self.kind = "message"
            self.message = arg["choices"][0]["message"]["content"]
        pass

    def is_function(self):
        return self.kind == "function"

    def is_message(self):
        return self.kind == "message"


class ChatgptAsker:
    def __init__(self, system_prompt=""):
        self.system_message = {"role": "system", "content": system_prompt}
        self.messages = []
        self.messages.append(self.system_message)
        pass

    @staticmethod
    def text_token_count(text):
        tokenizer = tiktoken.encoding_for_model(GPT_MODEL)
        token_count = len(tokenizer.encode(text))
        return token_count

    def current_token_count(self):
        text = " ".join(message["content"] for message in self.messages)
        return ChatgptAsker.text_token_count(text)

    def append(self, role, content):
        self.messages.append({"role": role, "content": content})

    def pop(self):
        self.messages.pop(-1)
        # while self.current_token_count() > MAX_TOKEN_LENGTH and len(self.messages) > 1:
        #     self.messages.pop(1)

    def current_messages(self, with_func=False):
        max_length = 0
        if with_func is True:
            max_length = MAX_TOKEN_LENGTH_WITH_FUNCTION
        else:
            max_length = MAX_TOKEN_LENGTH_WITHOUT_FUNCTION
        messages = []
        token_len = ChatgptAsker.text_token_count(self.system_message["content"])
        for i in range(len(self.messages) - 1, 0, -1):
            if (
                token_len + ChatgptAsker.text_token_count(self.messages[i]["content"])
                > max_length
            ):
                break
            messages.append(self.messages[i])
            token_len += ChatgptAsker.text_token_count(self.messages[i]["content"])
        messages.append(self.system_message)
        messages.reverse()
        return messages

    # @retry(wait=wait_random_exponential(min=21, max=25), stop=stop_after_attempt(3))
    def ask(self, input, functions=None, model=GPT_MODEL):
        self.append("user", input)
        response = None
        if functions is not None:
            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=self.current_messages(True),
                functions=functions,
                function_call="auto",
            )
        else:
            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=self.current_messages(),
            )
        return ChatgptAnswer(response)

    # @retry(wait=wait_random_exponential(min=21, max=25), stop=stop_after_attempt(5))
    def answer_partly(self, data, num, totnum):
        self.append(
            "user",
            f"Reference this data to answer to above prompt.\
            Remember! They are only extracted vehicles from more than 1000000 various different vehicles from company's database.\
            You cannot receive lots of tokens at once, so I'm going to combine the answer of you at last, manually.\
            And this is the number {num + 1} out of {totnum} vehicles.\n\
            You should know what the first answer should be, and what the last answer should be.\
            So Remember! Don't mention of other information. Only mention about this vehicle!\
            And you must mention the index of vehicle for convenience.\
            Do not answer until you think the answer is perfect.\
            \n\n\
            {data}",
        )
        messages = self.current_messages()
        # print(messages)
        response = openai.ChatCompletion.create(model=GPT_MODEL, messages=messages)
        print(f"-----------{num} : response out of {totnum}--------------------")
        self.pop()
        return response["choices"][0]["message"]["content"]

    # @retry(wait=wait_random_exponential(min=21, max=25), stop=stop_after_attempt(5))
    def answer(self, data_list):
        pushed_cnt = 0

        response_list = []
        for i in range(len(data_list)):
            response_list.append(self.answer_partly(data_list[i], i, len(data_list)))
        result = "\n".join(response_list)
        return result
