import streamlit as st
import time
from backend import (
    create_connect_token,
    fetch_accounts,
    fetch_account_details,
    fetch_transactions_list,
    fetch_transaction_details,
    fetch_item_status,
)

st.set_page_config(page_title="Pluggy Open Finance", layout="wide")

st.title(":link: Pluggy + Streamlit Open Finance Demo")

if 'connect_token' not in st.session_state:
    st.session_state['connect_token'] = None

if 'item_id' not in st.session_state:
    st.session_state['item_id'] = None

if st.button(":key: Connect my account"):
    try:
        token_data = create_connect_token()
        st.session_state['connect_token'] = token_data['accessToken']
        st.success("Connect token generated! The widget will load below.")
    except Exception as e:
        st.error(f"Error generating connect token: {e}")

if st.session_state['connect_token']:
    connect_token = st.session_state['connect_token']
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
                alert("Account connected! Please copy this Item ID: " + itemData.item.id);
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

item_id_input = st.text_input(":inbox_tray: Paste the Item ID returned by the widget here")

if item_id_input:
    st.session_state['item_id'] = item_id_input
    st.success(f"Item ID saved: {item_id_input}")

if st.session_state['item_id']:
    st.header(":bar_chart: Financial Data")
    try:
        with st.spinner("⏳ Waiting for data synchronization..."):
            for _ in range(10):
                item_status = fetch_item_status(st.session_state['item_id'])
                if item_status.get("status") == "UPDATED":
                    break
                time.sleep(2)
            else:
                st.error("Item not updated in time. Please try again.")
                st.stop()

        # Fetch list of accounts
        accounts_list = fetch_accounts(st.session_state['item_id'])
        st.subheader(":page_facing_up: Accounts List Response")
        st.json(accounts_list)

        # Fetch details for each account and transactions
        st.subheader(":page_facing_up: Account Details (individual retrieves)")
        for account in accounts_list.get('results', []):
            details = fetch_account_details(account['id'])
            st.write(f"Account details: {account['name']}")
            st.json(details)

            st.write(f"Transactions for account: {account['name']}")
            transactions_list = fetch_transactions_list(account['id'])
            st.json(transactions_list)

            st.write(f"Details for up to 5 transactions of account: {account['name']}")
            for tx in transactions_list.get('results', [])[:5]:
                tx_detail = fetch_transaction_details(tx['id'])
                st.json(tx_detail)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
