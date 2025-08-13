# 💸 Personal Finance Organizer

Streamlit app to organize personal finances with Open Finance integration via Pluggy sandbox environment.

---

## 🚀 Objectives

- Connect to Open Finance APIs to fetch real banking data (e.g., balance, transactions).  
- Enable manual and automatic categorization of income and expenses.  
- Display interactive dashboards for cash flow, budgeting, and goals.  

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Pluggy** (sandbox environment)
- **Requests**
- **CSV** (for temporary storage of Item IDs)

---

## 📊 Data Sources

- Real data from Pluggy Open Finance sandbox.  
- Synthetic data manually created for testing and prototyping.

---

## 🧭 Current Features

- Connect a bank account using Pluggy widget (one bank per connection).  
- Store Item ID locally in CSV per user (keyed by user name).  
- Fetch accounts and transactions for connected bank accounts.  
- Dashboard **currently just prints JSON responses** from Pluggy API.  
- Basic session handling for **one user at a time**.  

---

## 🔮 Future Plans / Scalability

- Support multiple users with proper **user authentication**.  
- Replace CSV storage with a **database** (e.g., SQLite, PostgreSQL) to safely store Item IDs per user.  
- Ensure **session isolation** so each user sees only their own financial data.  
- Handle **concurrent access** when multiple users connect banks simultaneously.  
- Implement analysis and visualizations on top of raw JSON data (e.g., spending breakdown, charts).  
- Potentially extend the system to support multiple Open Finance providers beyond Pluggy.

---

## 📌 Usage

1. Run the Streamlit app:  
   ```bash
   streamlit run app.py
