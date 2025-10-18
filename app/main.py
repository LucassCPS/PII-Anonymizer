import streamlit as st
import os
from core import llm_client
from components import sidebar
import json

SYSTEM_PROMPT_FILE = "system_prompt_default.txt"
DEFAULT_SYSTEM_PROMPT = ""

try:
    if os.path.exists(SYSTEM_PROMPT_FILE):
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            DEFAULT_SYSTEM_PROMPT = f.read().strip()
    else:
        DEFAULT_SYSTEM_PROMPT = "Instruções Padrão não encontradas. Crie o arquivo system_prompt_default.txt."
except Exception as e:
    DEFAULT_SYSTEM_PROMPT = f"Erro ao ler prompt: {e}"

st.set_page_config(page_title="LLM Chat")
st.title("Analisador de Dados Sensíveis")

st.markdown("""
<style>
.block-container {
    max-width: 95% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

main .block-container {
    padding-top: 1rem !important;
}

textarea {
    min-height: 200px !important;
    width: 100% !important;
}

div.stButton > button {
    width: 100%;
    border-radius: 8px !important;
    font-weight: 600;
}

[data-testid="stHorizontalBlock"] {
    align-items: start !important;
}

[data-testid="stJson"] {
    font-size: 0.9rem !important;
}

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
div.stButton > button { width: 100%; margin: 0; }
section[data-testid="stSidebar"] + div [data-testid="column"] { padding-left: 0 !important; padding-right: 0 !important; }
</style>
""", unsafe_allow_html=True)


if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
if "history" not in st.session_state:
    st.session_state.history = []

config_data = sidebar.render_sidebar(DEFAULT_SYSTEM_PROMPT)

base_url = config_data.get("base_url")
api_key = config_data.get("api_key")
model = config_data.get("model")
temp = config_data.get("temperature")
max_tokens = config_data.get("max_tokens")
do_stream = config_data.get("do_stream")
system_prompt = config_data.get("system_prompt")

if not api_key: 
    st.error("API_KEY não encontrada.") 
    st.stop()
if not base_url: 
    st.error("BASE_URL não definida.")
    st.stop()
if not model: 
    st.error("Nenhum modelo disponível.") 
    st.stop()

client = llm_client.get_client(base_url, api_key)

user_input = st.text_area("Texto a ser analisado:", height=180, placeholder="Cole aqui o texto...")
analyze_clicked = st.button("Analisar", type="primary", use_container_width=True)

if analyze_clicked:
    if not user_input.strip():
        st.warning("Insira um texto antes de analisar.")
        st.stop()
    if not model:
        st.error("Nenhum modelo disponível.")
        st.stop()

    messages = [
        {"role": "system", "content": st.session_state.system_prompt.strip()},
        {"role": "user", "content": user_input.strip()},
    ]

    try:
        with st.spinner("Analisando..."):
            if do_stream:
                stream = client.chat.completions.create(stream=True, model=model, messages=messages, temperature=temp)
                full_text = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    token = getattr(delta, "content", None)
                    if token:
                        full_text += token
            else:
                resp = client.chat.completions.create(model=model, messages=messages, temperature=temp)
                full_text = resp.choices[0].message.content.strip()

        st.markdown("### Resultado da análise")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Entrada:**")
            st.code(user_input.strip(), language="text")
        with col2:
            st.markdown("**Saída:**")
            try:
                parsed = json.loads(full_text)
                st.json(parsed)
            except Exception:
                st.code(full_text, language="json")

    except Exception as e:
        st.error(f"Erro ao chamar o modelo: {e}")