import streamlit as st
import os
from core import llm_client
from components import sidebar
from typing import Dict, List

SYSTEM_PROMPT_FILE = "system_prompt_default.txt"
DEFAULT_SYSTEM = ""
try:
    if os.path.exists(SYSTEM_PROMPT_FILE):
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            DEFAULT_SYSTEM = f.read().strip()
    else:
        DEFAULT_SYSTEM = "Instruções Padrão não encontradas. Crie o arquivo system_prompt_default.txt."
except Exception as e:
    DEFAULT_SYSTEM = f"Erro ao ler prompt: {e}"

st.set_page_config(page_title="LLM Chat – Modelos e Instruções")
st.title("LLM Chat – Analisador de Dados Sensíveis")

st.markdown("""
<style>
div.stButton > button { width: 100%; margin: 0; }
section[data-testid="stSidebar"] + div [data-testid="column"] { padding-left: 0 !important; padding-right: 0 !important; }
</style>
""", unsafe_allow_html=True)


if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM
if "history" not in st.session_state:
    st.session_state.history = []

config_data = sidebar.render_sidebar(DEFAULT_SYSTEM)

base_url = config_data.get("base_url")
api_key = config_data.get("api_key")
model = config_data.get("model")
temp = config_data.get("temperature")
max_tokens = config_data.get("max_tokens")
do_stream = config_data.get("do_stream")
system_prompt = config_data.get("system_prompt")

if not api_key: st.error("API_KEY não encontrada."); st.stop()
if not base_url: st.error("BASE_URL não definida."); st.stop()
if not model: st.error("Nenhum modelo disponível."); st.stop()

client = llm_client.get_client(base_url, api_key)

user_input = st.text_area("Texto a ser analisado:", height=180, placeholder="Cole aqui o texto...")
col1, col2 = st.columns([1, 1], gap="small")
with col1:
    send_clicked = st.button("Analisar", type="primary", use_container_width=True)
with col2:
    clear_clicked = st.button("Limpar histórico", use_container_width=True)
    if clear_clicked:
        st.session_state.history.clear()

# Histórico
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Envio e Chamada
if send_clicked:
    if not user_input.strip():
        st.warning("Insira um texto antes de analisar.")
        st.stop()
    
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input.strip()},
    ]
    st.session_state.history.append({"role": "user", "content": user_input.strip()})
    
    try:
        answer = llm_client.call_llm(
            client=client,
            model=model,
            messages=messages,
            temperature=temp,
            max_tokens=max_tokens,
            do_stream=do_stream
        )
        st.session_state.history.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Erro ao chamar o modelo: {e}")