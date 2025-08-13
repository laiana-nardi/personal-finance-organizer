import streamlit as st
import pandas as pd
import os
import time
from backend import (
    create_connect_token,
    fetch_accounts,
    fetch_account_details,
    fetch_transactions_list,
    fetch_transaction_details,
    fetch_item_status,
)

# CSV file to store user-item mapping
CSV_FILE = "item_ids.csv"

st.set_page_config(page_title="Pluggy Open Finance", layout="wide")
st.title("Pluggy + Streamlit Open Finance Demo")

# Ensure CSV exists
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["name", "item_id"]).to_csv(CSV_FILE, index=False)

# Ask for user name
user_name = st.text_input("Enter your name (unique key)")

if user_name:
    df = pd.read_csv(CSV_FILE)
    existing_row = df[df["name"] == user_name]

    if not existing_row.empty:
        st.success(f"Access already exists for: {user_name}")
        st.session_state["item_id"] = existing_row.iloc[0]["item_id"]

        if st.button("Connect another bank"):
            st.session_state["connect_token"] = create_connect_token()["accessToken"]
    else:
        if st.button("Connect my account"):
            st.session_state["connect_token"] = create_connect_token()["accessToken"]

    

# If we have a connect token, show the widget
if st.session_state.get("connect_token"):
    connect_token = st.session_state["connect_token"]
    st.components.v1.html(f"""
        <script src="https://cdn.pluggy.ai/pluggy-connect/latest/pluggy-connect.js"></script>
        <div id="pluggy-container" style="min-height: 400px;"></div>
        <script>
            localStorage.clear();
            const connect = new PluggyConnect({{
              connectToken: "{connect_token}",
              includeSandbox: true,
              container: '#pluggy-container',
              onSuccess: function(itemData) {{
                alert("Account connected! Item ID: " + itemData.item.id);
              }},
              onError: function(error) {{
                alert("Error: " + JSON.stringify(error));
              }},
              onClose: function() {{
                console.log("Widget closed");
              }}
            }});
            connect.init();
        </script>
    """, height=500)

# Manual Item ID input
item_id_input = st.text_input("Paste the Item ID returned by the widget here")

if item_id_input and user_name:
    st.session_state["item_id"] = item_id_input
    df = pd.read_csv(CSV_FILE)

    if user_name in df["name"].values:
        df.loc[df["name"] == user_name, "item_id"] = item_id_input
    else:
        df = pd.concat([df, pd.DataFrame([[user_name, item_id_input]], columns=["name", "item_id"])], ignore_index=True)

    df.to_csv(CSV_FILE, index=False)
    st.success(f"Item ID saved for {user_name}: {item_id_input}")

# Dashboard if we have item_id
if st.session_state.get("item_id"):
    st.header("Financial Data")
    try:
        with st.spinner("Waiting for data synchronization..."):
            for _ in range(10):
                item_status = fetch_item_status(st.session_state["item_id"])
                if item_status.get("status") == "UPDATED":
                    break
                time.sleep(2)
            else:
                st.error("Item not updated in time. Please try again.")
                st.stop()

        # Fetch accounts
        accounts_list = fetch_accounts(st.session_state["item_id"])
        st.subheader("Accounts List Response")
        st.json(accounts_list)

        # Account details & transactions
        st.subheader("Account Details and Transactions")
        for account in accounts_list.get("results", []):
            details = fetch_account_details(account["id"])
            st.write(f"Account details: {account['name']}")
            st.json(details)

            transactions_list = fetch_transactions_list(account["id"])
            st.write(f"Transactions for account: {account['name']}")
            st.json(transactions_list)

            st.write(f"Details for up to 5 transactions in account: {account['name']}")
            for tx in transactions_list.get("results", [])[:5]:
                tx_detail = fetch_transaction_details(tx["id"])
                st.json(tx_detail)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
