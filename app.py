import openai
import os
import pandas as pd
import numpy as np
import tiktoken

import psycopg2
from psycopg2.extras import execute_values, RealDictCursor

from dotenv import load_dotenv, find_dotenv

import json

_ = load_dotenv(find_dotenv())

import streamlit as st
openai.api_key = st.secrets["OPENAI_API_KEY"]

EMBEDDING_MODEL = st.secrets["EMBEDDING_MODEL"]
GPT_MODEL = st.secrets["GPT_MODEL"]

print(GPT_MODEL)

from Matadorbot import Matadorbot

bot = Matadorbot()


import streamlit as st

def chatbot(input_string):
    if input_string:
        reply = bot.request(input_string)
        return reply

if __name__ == "__main__":
    st.title("My Streamlit App")
    input_text = st.text_area("Enter text here:")

    if st.button("Ask to chatbot"):
        input_string = input_text.upper()
        st.write(bot.request(input_string), unsafe_allow_html=True)