import streamlit as st
import requests
import json

st.set_page_config(page_title="Chatbot Ollama", layout="centered")
st.title("🤖 Chat com Ollama")

# Define a URL do Ollama (pega dos secrets do Streamlit Cloud ou usa localhost)
OLLAMA_BASE_URL = st.secrets.get("OLLAMA_BASE_URL", " http://127.0.0.1:4040")
MODEL_NAME = "llama3.2"  # ou outro modelo instalado (mistral, qwen2.5, phi3, etc.)

# Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens anteriores na tela
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada do usuário
if prompt := st.chat_input("Digite sua mensagem..."):
    # Renderiza e salva a mensagem do usuário
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Chamada com streaming para o endpoint do Ollama
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        payload = {
            "model": MODEL_NAME,
            "messages": st.session_state.messages,
            "stream": True
        }

        try:
            res = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload,
                stream=True,
                timeout=60
            )
            res.raise_for_status()

            # Processamento do stream linha a linha
            for line in res.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    chunk = data.get("message", {}).get("content", "")
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.ConnectionError:
            st.error("Não foi possível conectar ao servidor Ollama. Verifique se o serviço está ativo ou se a URL está correta.")
        except Exception as e:
            st.error(f"Erro na requisição: {e}")
