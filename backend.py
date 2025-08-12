import requests
import streamlit as st

API_BASE_URL = "https://api.pluggy.ai"

def get_auth_token(force_new: bool = False):
    """
    Retorna apiKey e guarda em st.session_state["pluggy_api_key"].
    """
    if "pluggy_api_key" not in st.session_state or force_new:
        client_id = st.secrets["pluggy"]["client_id"]
        client_secret = st.secrets["pluggy"]["client_secret"]
        url = f"{API_BASE_URL}/auth"
        resp = requests.post(url, json={
            "clientId": client_id,
            "clientSecret": client_secret
        })
        resp.raise_for_status()
        data = resp.json()
        st.session_state["pluggy_api_key"] = data.get("apiKey")
        # st.write("DEBUG - Novo pluggy_api_key:", st.session_state["pluggy_api_key"])
    # else:
        # st.write("DEBUG - Reutilizando pluggy_api_key:", st.session_state["pluggy_api_key"])

    return st.session_state["pluggy_api_key"]

def create_connect_token():
    """
    Cria connect token com includeSandbox=True usando apiKey atual.
    """
    token = get_auth_token(force_new=False)
    url = f"{API_BASE_URL}/connect_token"
    headers = {
        "X-API-KEY": token,
        "accept": "application/json",
        "content-type": "application/json"
    }
    payload = {"options": {"includeSandbox": True}}
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    data = resp.json()
    # st.write("DEBUG - create_connect_token:", data)
    return data

def fetch_item_status(item_id):
    token = get_auth_token(False)
    url = f"{API_BASE_URL}/items/{item_id}"
    headers = {"X-API-KEY": token}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def fetch_accounts(item_id):
    token = get_auth_token(False)
    url = f"{API_BASE_URL}/accounts?itemId={item_id}"
    headers = {"X-API-KEY": token}
    resp = requests.get(url, headers=headers)
    # st.write("resp", resp.text)
    resp.raise_for_status()
    return resp.json()

def fetch_account_details(account_id):
    token = get_auth_token(False)
    url = f"{API_BASE_URL}/accounts/{account_id}"
    headers = {"X-API-KEY": token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_transactions_list(account_id):
    token = get_auth_token(False)
    url = f"{API_BASE_URL}/transactions?accountId={account_id}"
    headers = {"X-API-KEY": token}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def fetch_transaction_details(transaction_id):
    token = get_auth_token(False)
    url = f"{API_BASE_URL}/transactions/{transaction_id}"
    headers = {"X-API-KEY": token}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()