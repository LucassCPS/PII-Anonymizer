import streamlit as st
from core import llm_client
from components import sidebar
from utils import prompts
from utils import reidentifier
from utils import json_cleaner
import json
import re

DEFAULT_SYSTEM_PROMPT, PROMPT_TYPE = prompts.get_zero_shot_prompt()
DEFAULT_THIRD_PARTY_PROMPT = prompts.get_third_party_prompt()

st.set_page_config(page_title="Anonimizador de Dados")
st.title("Anonimizador de Dados Sensíveis")

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
            
textarea[disabled] {
    opacity: 1;
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
</style>
""", unsafe_allow_html=True)


if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
if "history" not in st.session_state:
    st.session_state.history = []
if "anonimized_display_text" not in st.session_state:
    st.session_state.anonimized_display_text = ""
if "pii_json_data" not in st.session_state:
    st.session_state.pii_json_data = {"status": "Aguardando análise..."}
if "show_pii_json" not in st.session_state:
    st.session_state.show_pii_json = False

config_data = sidebar.render_sidebar(DEFAULT_SYSTEM_PROMPT)

base_url = config_data.get("base_url")
api_key = config_data.get("api_key")
model_anon = config_data.get("model_anon")
model_resp = config_data.get("model_resp")
temp = config_data.get("temperature")
system_prompt = config_data.get("system_prompt")

if not api_key: 
    st.error("API_KEY não encontrada.") 
    st.stop()
if not base_url: 
    st.error("BASE_URL não definida.")
    st.stop()
if not model_anon or not model_resp:
    st.error("Pelo menos um dos modelos não está disponível.") 
    st.stop()

client = llm_client.get_client(base_url, api_key)


col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### Entrada do Usuário")
    user_input = st.text_area(
        "Cole aqui o texto do usuário para análise...", 
        height=200,
        placeholder="Cole aqui o texto do usuário para análise...",
        key="original_input",
        label_visibility="collapsed"
    )
    
    analyze_clicked = st.button(
        "Analisar e Enviar", 
        type="primary", 
        use_container_width=False, 
        key="analyze_button",
    )
with col2:
    st.markdown("### Saída Anonimizada")
    
    placeholder_anon = st.empty()
    placeholder_anon.text_area(
        "Texto Anonimizado",
        value="",
        height=200,
        key="anonimized_text_display",
        label_visibility="collapsed"
    )

    if st.button("Mostrar/Esconder PII's Detectados (JSON)", key="toggle_pii_json", use_container_width=True):
        st.session_state.show_pii_json = not st.session_state.show_pii_json

    if st.session_state.show_pii_json:
        st.markdown("**PII's Detectados (JSON):**")
        if "error" in st.session_state.pii_json_data:
             st.code(st.session_state.pii_json_data.get("raw_text", ""), language="json")
             st.warning(st.session_state.pii_json_data["error"])
        else:
             st.json(st.session_state.pii_json_data)


st.markdown("---")
st.markdown("### Resposta Recebida de um Terceiro")
placeholder_forwarded = st.empty()
placeholder_forwarded.text_area(
    "Resposta do Terceiro (Output p/ Usuário)",
    value="",
    height=200,
    key="forwarded_message_placeholder",
    label_visibility="collapsed",
    disabled=True
)

st.markdown("---")
st.markdown("### Resposta Reidentificada")
placeholder_reidentified = st.empty()
placeholder_reidentified.text_area(
    "Resposta do Terceiro com PIIs Restaurados",
    value="",
    height=100,
    key="reidentified_output_placeholder",
    label_visibility="collapsed",
    disabled=True
)


if analyze_clicked:
    if not user_input.strip():
        st.warning("Insira um texto antes de analisar.")
        st.stop()

    messages_anon = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_input.strip()},
    ]

    try:
        with st.spinner("Analisando e extraindo PIIs..."):
            full_text_pii = ""
            resp = client.chat.completions.create(model=model_anon, messages=messages_anon, temperature=temp)
            full_text_pii = resp.choices[0].message.content.strip()

        pii_json = {}
        cleaned_pii_output = json_cleaner.clean_json_output(full_text_pii)
        
        try:
            pii_json = json.loads(cleaned_pii_output)
            st.session_state.pii_json_data = pii_json
        except Exception:
            st.session_state.pii_json_data = {
                "error": "O modelo de anonimização não retornou um JSON válido.", 
                "raw_text": full_text_pii
            }
        
        simulated_anon_text = user_input.strip()

        if "entities" in st.session_state.pii_json_data:
            try:
                entities = st.session_state.pii_json_data["entities"]

                entities_sorted = sorted(entities, key=lambda e: len(e.get("text", "")), reverse=True)

                for entity in entities_sorted:
                    original_text = entity.get("text", "").strip()
                    label_text = entity.get("label", "").strip()

                    if not original_text or not label_text:
                        continue

                    try:
                        simulated_anon_text = re.sub(re.escape(original_text), f"[{label_text.upper()}]", simulated_anon_text)
                    except re.error:
                        simulated_anon_text = simulated_anon_text.replace(original_text, f"[{label_text.upper()}]")
                placeholder_anon.text_area(
                    "Texto Anonimizado (Substituições)",
                    value=simulated_anon_text,
                    height=200,
                    key="anonimized_text_display_updated",
                    label_visibility="collapsed",
                    disabled=True
                )
            except Exception as e:
                placeholder_anon.text_area(
                    "Texto Anonimizado",
                    value=f"Erro ao processar anonimização com base no JSON: {e}",
                    height=200,
                    key="anonimized_text_display_updated",
                    label_visibility="collapsed",
                    disabled=True
                )
        else:
            placeholder_anon.text_area(
                "Texto Anonimizado",
                value="Nenhum campo 'entities' foi retornado pelo modelo.",
                height=200,
                key="anonimized_text_display_updated",
                label_visibility="collapsed",
                disabled=True
            )

        st.session_state.show_pii_json = False
                
        messages_resp = [
            {"role": "system", "content": DEFAULT_THIRD_PARTY_PROMPT},
            {"role": "user", "content": simulated_anon_text},
        ]
        
        response_from_third = ""
        with st.spinner("Elaborando resposta..."):
             resp_llm = client.chat.completions.create(model=model_resp, messages=messages_resp, temperature=temp)
             response_from_third = resp_llm.choices[0].message.content.strip()

        placeholder_forwarded.text_area(
            "Resposta do Terceiro",
            value=response_from_third,
            height=200,
            key="forwarded_message_result",
            label_visibility="collapsed",
            disabled=True
        )
        
        try:
            reidentified_text = reidentifier.reidentify_text(
                anonymized_text=response_from_third,
                entities_json=st.session_state.pii_json_data
            )
        except Exception as e:
            reidentified_text = f"[ERRO NA REIDENTIFICAÇÃO: {e}]"

        placeholder_reidentified.text_area(
            "Resposta do Terceiro com PIIs Restaurados",
            value=reidentified_text,
            height=100,
            key="reidentified_output_result",
            label_visibility="collapsed",
            disabled=True
        )
    
    except Exception as e:
        st.error(f"Erro ao chamar o modelo: {e}")