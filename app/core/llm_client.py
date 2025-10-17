import streamlit as st
from openai import OpenAI
from typing import Dict, List, Any

@st.cache_resource
def get_client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key=api_key)

def call_llm(client: OpenAI, model: str, messages: List[Dict[str, str]], temperature: float, max_tokens: int, do_stream: bool) -> str:
    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }
    if max_tokens:
        kwargs["max_tokens"] = int(max_tokens)

    if do_stream:
        stream = client.chat.completions.create(stream=True, **kwargs)
        full_text = ""
        with st.chat_message("assistant"):
            container = st.empty()
            for chunk in stream:
                try:
                    delta = chunk.choices[0].delta
                    token = getattr(delta, "content", None)
                    if token:
                        full_text += token
                        container.markdown(full_text)
                except Exception:
                    pass
        return full_text.strip()
    else:
        resp = client.chat.completions.create(**kwargs)
        text = resp.choices[0].message.content.strip()
        with st.chat_message("assistant"):
            st.markdown(text)
        return text