import streamlit as st
from core import config

DEFAULT_ENV_PATH = "backend.env"
DEFAULT_DO_STREAM = True
DEFAULT_MAX_TOKENS = 0
DEFAULT_TEMPERATURE = 0.0

def render_sidebar(default_system_prompt):
    with st.sidebar:
        st.header("Configurações do Modelo")

        if "env_cache" not in st.session_state:
            base_url, api_key, available_models, raw_env = config.load_env_and_models(DEFAULT_ENV_PATH)

            st.session_state.env_cache = {
                "base_url": base_url,
                "api_key": api_key,
                "models": available_models,
                "raw_env": raw_env,
            }

        cache = st.session_state.env_cache

        model_anon_id = None
        model_anon_name = None
        
        model_resp_id = None
        model_resp_name = None

        if not cache["models"]:
            st.error("Nenhum modelo encontrado (MODEL_*). Ajuste seu backend.env no container.")
        else:
            selected_label_anon = st.selectbox(
                "Modelo 1: **Anonimização (PII)**",
                options=list(cache["models"].keys()),
                format_func=lambda k: cache['models'][k].replace('MODEL_', ''),
                index=0,
                key="model_selector_anon"
            )
            model_anon_id = cache["models"][selected_label_anon]
            model_anon_name = selected_label_anon

            selected_label_resp = st.selectbox(
                "Modelo 2: **Elaboração da Resposta**",
                options=list(cache["models"].keys()),
                format_func=lambda k: cache['models'][k].replace('MODEL_', ''),
                index=0,
                key="model_selector_resp"
            )
            model_resp_id = cache["models"][selected_label_resp]
            model_resp_name = selected_label_resp

       
        st.markdown("---")
        current_prompt = st.session_state.get("system_prompt", default_system_prompt)
        
        with st.expander("Instruções do Modelo", expanded=True):
            edited_prompt = st.text_area(
                "Instruções",
                value=current_prompt,
                height=400,
                label_visibility="collapsed"
            )

            col1, col2 = st.columns(2)
            
            if col1.button("Aplicar instruções", type="primary", use_container_width=True):
                st.session_state.system_prompt = edited_prompt 
                st.success("Instruções atualizadas.")
                
            if col2.button("Restaurar padrão", use_container_width=True):
                st.session_state.system_prompt = default_system_prompt
                st.success("Padrão restaurado.")

    return {
        "base_url": cache["base_url"],
        "api_key": cache["api_key"],
        "model_anon": model_anon_id,
        "model_anon_name": model_anon_name,
        "model_resp": model_resp_id,
        "model_resp_name": model_resp_name,
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "do_stream": DEFAULT_DO_STREAM,
        "system_prompt": st.session_state.get("system_prompt", default_system_prompt),
    }