import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

st.title("Simple LLM Chat")
prompt = st.text_area("Enter your prompt:", "generate a broken formatted json")

if st.button("Send"):
    with st.spinner("Getting response..."):
        messages = [
            {"role": "user", "content": prompt}
        ]
        try:
            response = client.chat.completions.create(
                model=os.getenv("MODEL_MISTRAL"),
                messages=messages
            )
            st.success("Response:")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"An error occurred: {e}")