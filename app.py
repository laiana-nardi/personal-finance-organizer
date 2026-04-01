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

st.set_page_config(page_title="Pluggy Open Finance", page_icon=":bar_chart:",layout="wide")
st.title(":link: Pluggy + Streamlit Open Finance App")

# Ensure CSV exists
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["name", "item_id"]).to_csv(CSV_FILE, index=False)

# Ask for user name
user_name = st.text_input("Enter your name (unique key)")

if user_name:
    df = pd.read_csv(CSV_FILE)
    existing_rows = df[df["name"] == user_name]

    if not existing_rows.empty:
        st.success(f"Access already exists for: {user_name}")
        st.session_state["item_id"] = existing_rows.iloc[0]["item_id"]

        if st.button(":arrows_counterclockwise: Connect another bank"):
            st.session_state["connect_token"] = create_connect_token()["accessToken"]
    else:
        if st.button(":key: Connect my account"):
            st.session_state["connect_token"] = create_connect_token()["accessToken"]

# If we have a connect token, show the widget
if st.session_state.get("connect_token"):
    connect_token = st.session_state["connect_token"]
    st.components.v1.html(f"""
        <script src="https://cdn.pluggy.ai/pluggy-connect/latest/pluggy-connect.js"></script>
        <div id="pluggy-container" style="min-height: 500px;"></div>
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
    st.header(":bar_chart: Financial Data")
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

        ###### Fetch accounts ######
        accounts_list = fetch_accounts(st.session_state["item_id"])
        accounts = accounts_list.get("results", [])

        # Totals
        total_balance = sum(a["balance"] for a in accounts if a["type"] == "BANK" and a.get("balance") is not None)
        total_credit_limit = sum(a["creditData"]["creditLimit"] for a in accounts if a["type"] == "CREDIT" and a.get("creditData"))
        total_credit_balance = sum(a.get("balance", 0) for a in accounts if a["type"] == "CREDIT")

        # Accounts Summary Cards
        st.subheader(":1234: Accounts Summary")
        summary_cards = [
            ("Total Bank Balance", total_balance, "#00FF00"),
            ("Total Credit Limit", total_credit_limit, "#FFD700"),
            ("Total Credit Owed", total_credit_balance, "#FF6347")
        ]

        max_cols = 3
        for i in range(0, len(summary_cards), max_cols):
            row_cards = summary_cards[i:i+max_cols]
            cols = st.columns(len(row_cards))
            for j, (title, value, color) in enumerate(row_cards):
                with cols[j]:
                    st.markdown(
                        f'<div style="background-color:#2c3e50; padding:15px; border-radius:10px; text-align:center;">'
                        f'<h4 style="color:{color};">{title}</h4>'
                        f'<p style="font-size:20px; color:#FFFFFF;">R$ {value:,.2f}</p>'
                        f'</div>', unsafe_allow_html=True
                    )

        # Account cards: max 3 per row - testing
        st.subheader(":file_folder: Account Details by Bank")
        for i in range(0, len(accounts), max_cols):
            row_accounts = accounts[i:i+max_cols]
            cols = st.columns(len(row_accounts))
            for j, account in enumerate(row_accounts):
                with cols[j]:
                    html = f"""
                    <div style='background-color:#2c3e50; padding:15px; border-radius:10px; margin-bottom:10px;'>
                        <h4 style='color:#FFD700'>{account.get('name', 'Unnamed')}</h4>
                        <p><b>Type:</b> {account.get('type')} - {account.get('subtype')}</p>
                        <p><b>Current Balance:</b> R$ {account.get('balance',0):,.2f} {account.get('currencyCode')}</p>
                    """
                    if account.get("owner"):
                        html += f"<p>Owner: {account['owner']}</p>"
                    if account.get("taxNumber"):
                        html += f"<p>Tax Number (CPF): {account.get('taxNumber')}</p>"

                    # Bank account
                    if account.get("type") == "BANK" and account.get("bankData"):
                        bank_data = account["bankData"]
                        html += f"<p>Account Number: {account.get('number')}</p>"
                        if bank_data.get("overdraftContractedLimit") is not None:
                            html += f"<p>Overdraft Limit: R$ {bank_data['overdraftContractedLimit']:,.2f}</p>"
                        if bank_data.get("closingBalance") is not None:
                            html += f"<p>Closing Balance: R$ {bank_data['closingBalance']:,.2f}</p>"

                    # Credit card
                    if account.get("type") == "CREDIT" and account.get("creditData"):
                        credit_data = account["creditData"]
                        html += f"<p>Total Credit Limit: R$ {credit_data.get('creditLimit',0):,.2f}</p>"
                        html += f"<p>Available Credit Limit: R$ {credit_data.get('availableCreditLimit',0):,.2f}</p>"
                        html += f"<p>Credit Balance Owed: R$ {account.get('balance',0):,.2f}</p>"
                        html += f"<p>Closing Date: {credit_data.get('balanceCloseDate','')}</p>"
                        html += f"<p>Due Date: {credit_data.get('balanceDueDate','')}</p>"
                        html += f"<p>Status: {credit_data.get('status','')}</p>"
                        if credit_data.get("minimumPayment"):
                            html += f"<p>Minimum Payment: R$ {credit_data['minimumPayment']:,.2f}</p>"

                    html += "</div>"
                    st.markdown(html, unsafe_allow_html=True)

        ###### Account details & transactions ######
        st.subheader(":file_folder: Account Details and Transactions")
        for account in accounts:
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
