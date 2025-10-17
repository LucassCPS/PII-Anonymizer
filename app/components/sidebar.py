import streamlit as st
from typing import Dict, Any
from core import config

def render_sidebar(default_system_prompt: str) -> Dict[str, Any]:
    with st.sidebar:
        st.header("Configurações do Ambiente/Modelo")

        env_path = st.text_input("Caminho do env", value="backend.env", help="Ex.: backend.env ou .env")
        refresh = st.button("Recarregar .env")

        if "env_cache" not in st.session_state or refresh:
            base_url, api_key, available_models, env_source, raw_env = config.load_env_and_models(env_path)
            st.session_state.env_cache = {
                "base_url": base_url,
                "api_key": api_key,
                "models": available_models,
                "env_source": env_source,
                "raw_env": raw_env,
            }

        cache = st.session_state.env_cache
        
        st.caption(f"Arquivo alvo: `{env_path}`")
        st.caption(f"Fontes usadas: {cache['env_source']}")
        st.caption(f"BASE_URL: {cache['base_url'] or '—'}")
        
        selected_model_id = None
        selected_model_name = None
        
        if not cache["models"]:
            st.error("Nenhum modelo encontrado (chaves começando com MODEL_). Ajuste o caminho do arquivo.")
        else:
            selected_label = st.selectbox(
                "Selecione o modelo",
                options=list(cache["models"].keys()),
                format_func=lambda k: f"{k} → {cache['models'][k]}",
                index=0
            )
            selected_model_id = cache["models"][selected_label]
            selected_model_name = selected_label

        temperature = st.slider("Temperature", 0.0, 2.0, 0.2, 0.1)
        max_tokens = st.number_input("Max tokens (0 = auto)", min_value=0, value=0, step=10)
        do_stream = st.toggle("Streaming em tempo real", value=True)

        st.markdown("---")
        st.subheader("Instruções do modelo (System Prompt)")

        current_prompt = st.session_state.get("system_prompt", default_system_prompt)

        with st.expander("Editar instruções", expanded=False):
            uploaded = st.file_uploader("Opcional: carregar .txt com instruções", type=["txt"])
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

            col_sp1, col_sp2 = st.columns(2)
            with col_sp1:
                if st.button("Aplicar instruções"):
                    st.session_state.system_prompt = edited_prompt
                    st.success("Instruções atualizadas.")
            with col_sp2:
                if st.button("Restaurar padrão"):
                    st.session_state.system_prompt = default_system_prompt
                    st.success("Instruções restauradas para o padrão.")

    return {
        "base_url": cache["base_url"],
        "api_key": cache["api_key"],
        "model": selected_model_id,
        "model_name": selected_model_name,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "do_stream": do_stream,
        "system_prompt": st.session_state.get("system_prompt", default_system_prompt)
    }