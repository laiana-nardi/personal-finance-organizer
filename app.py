import streamlit as st
import requests

st.set_page_config(page_title="Pluggy API Demo", layout="centered")
st.title("Pluggy API - Demo com Streamlit")


# Função para autenticar e obter API Key
@st.cache_data
def get_api_key():
    url = "https://api.sandbox.pluggy.ai/auth"
    payload = {
        "clientId": st.secrets["pluggy"]["client_id"],
        "clientSecret": st.secrets["pluggy"]["client_secret"]
    }

    try:
        response = requests.post(url, json=payload, verify=False)
        response.raise_for_status()
    
        return response.json().get("apiKey")
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na autenticação: {e}")
        return None

# Função para gerar Link Token
def generate_link_token(api_key):
    url = "https://api.sandbox.pluggy.ai/link/token"
    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

    payload = {"clientUserId": "demo_user_001"}
    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        response.raise_for_status()
        return response.json().get("linkToken")
    # except requests.exceptions.RequestException as e:
    #     st.error(f"Erro ao gerar Link Token: {e}")
    #     return None
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            st.error(f"Erro ao gerar Link Token: {e} | Resposta: {e.response.text}")
        else:
            st.error(f"Erro ao gerar Link Token: {e}")
        return None


# Execução principal
st.write("Este app conecta à API da Pluggy (modo sandbox).")

# Botão para iniciar
if st.button("Conectar com Pluggy"):
    with st.spinner("Autenticando..."):
        api_key = get_api_key()

    if api_key:
        st.success("Autenticado com sucesso!")
        st.write("Gerando Link Token...")

        link_token = generate_link_token(api_key)

        if link_token:
            st.success("Link Token gerado com sucesso!")
            link_url = f"https://pluggy.ai/link?link_token={link_token}"

            st.markdown("### Abrir Pluggy Link")
            st.write("Clique no botão abaixo para abrir a interface de conexão:")
            st.markdown(f"[Abrir Pluggy Link]({link_url})", unsafe_allow_html=True)
            st.code(link_url, language="text")

            st.info("Dica: selecione uma instituição 'Sandbox' e simule a conexão.")
        else:
            st.error("Falha ao gerar Link Token.")
    else:
        st.error("Falha na autenticação com a API.")
