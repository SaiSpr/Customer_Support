__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

import streamlit as st
from PIL import Image

from customer_support import CustomerSupportPipeline
from ui.graph_renderer import GraphRenderer

import os
import openai

image = Image.open("Vasuki_logo.png")
col1, col2 = st.columns([1,2])
with col1: 
     st.image(image,use_column_width=True)
#st.image(image)
with col2:
     st.title('')
st.markdown("✨Greetings! I'm Vasuki, your expert CustomerSupport Chatbot.. ✨")

openai.api_key = st.secrets['OPENAI_API_KEY']
api_key = openai.api_key

# Set the OpenAI API key as an environment variable
os.environ['OPENAI_API_KEY'] = api_key


chatbot_started = False


def get_answer(query: str, pipeline):
    """
    Queries the model with a given question and returns the answer.
    """
    res, is_over = pipeline.run(query)
    return res, is_over


def start_chatbot():
    tab1, tab2 = st.tabs(["Chat", "Graph"])

    with tab1:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "pipeline" not in st.session_state:
            pipeline = CustomerSupportPipeline()
            st.session_state.pipeline = pipeline
            res, is_over = pipeline.run("")
            for prompt in res:
                st.session_state.messages.append(
                    {"role": "assistant", "content": prompt.message}
                )
        else:
            pipeline = st.session_state.pipeline

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("What is Up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            responses, is_over = get_answer(
                st.session_state.messages[-1]["content"], pipeline
            )

            for full_response in responses:
                answer = full_response.message
                message_placeholder.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

    with tab2:
        st.session_state._graph = GraphRenderer().get(
            type(pipeline._current_node).__name__
        )
        

        st.graphviz_chart(st.session_state._graph, use_container_width=True)


start_chatbot()
