import streamlit as st
from typing import Dict, Any
from core import config

DEFAULT_ENV_PATH = "backend.env"
DEFAULT_DO_STREAM = True   # mude aqui se quiser desativar
DEFAULT_MAX_TOKENS = 0     # 0 = auto

def render_sidebar(default_system_prompt: str) -> Dict[str, Any]:
    with st.sidebar:
        st.header("Configurações do Modelo")

        # carrega/env cache silenciosamente (sem input de .env)
        if "env_cache" not in st.session_state:
            base_url, api_key, available_models, env_source, raw_env = config.load_env_and_models(DEFAULT_ENV_PATH)
            st.session_state.env_cache = {
                "base_url": base_url,
                "api_key": api_key,
                "models": available_models,
                "env_source": env_source,
                "raw_env": raw_env,
            }

        cache = st.session_state.env_cache

        # apenas seleção de modelo (a partir das chaves MODEL_* do env)
        selected_model_id = None
        selected_model_name = None
        if not cache["models"]:
            st.error("Nenhum modelo encontrado (MODEL_*). Ajuste seu backend.env no container.")
        else:
            selected_label = st.selectbox(
                "Selecione o modelo",
                options=list(cache["models"].keys()),
                format_func=lambda k: f"{k} → {cache['models'][k]}",
                index=0
            )
            selected_model_id = cache["models"][selected_label]
            selected_model_name = selected_label

        # mantém só a temperatura
        temperature = st.slider("Temperature", 0.0, 2.0, 0.2, 0.1)

        # editor opcional do system prompt
        st.markdown("---")
        st.subheader("Instruções do modelo (System Prompt)")
        current_prompt = st.session_state.get("system_prompt", default_system_prompt)
        with st.expander("Editar instruções", expanded=False):
            uploaded = st.file_uploader("Opcional: carregar .txt", type=["txt"])
            if uploaded:
                try:
                    content = uploaded.read().decode("utf-8")
                    st.session_state.system_prompt = content
                    st.success("Instruções carregadas do arquivo.")
                except Exception as e:
                    st.error(f"Erro ao ler arquivo: {e}")

            edited_prompt = st.text_area(
                "Edite as instruções",
                value=current_prompt,
                height=260,
                key="system_prompt_editor"
            )
            col1, col2 = st.columns(2)
            if col1.button("Aplicar instruções"):
                st.session_state.system_prompt = edited_prompt
                st.success("Instruções atualizadas.")
            if col2.button("Restaurar padrão"):
                st.session_state.system_prompt = default_system_prompt
                st.success("Padrão restaurado.")

    # retorna tudo que o app precisa (sem exibir na UI)
    return {
        "base_url": cache["base_url"],
        "api_key": cache["api_key"],
        "model": selected_model_id,
        "model_name": selected_model_name,
        "temperature": temperature,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "do_stream": DEFAULT_DO_STREAM,
        "system_prompt": st.session_state.get("system_prompt", default_system_prompt),
    }
