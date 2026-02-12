import requests
import streamlit as st

from budget_app.config import get_settings

settings = get_settings()
API_BASE = settings.api_base_url.rstrip("/")

st.set_page_config(page_title="Budget Platform", layout="wide")
st.title("Budget Platform")

st.subheader("1) Upload Client Budget CSV")
uploaded = st.file_uploader("Upload CSV", type=["csv"])
if st.button("Ingest CSV", disabled=uploaded is None):
    if uploaded is None:
        st.warning("Select a CSV file first")
    else:
        files = {"file": (uploaded.name, uploaded.getvalue(), "text/csv")}
        try:
            response = requests.post(f"{API_BASE}/budgets/upload-csv", files=files, timeout=60)
            if response.ok:
                st.success("Ingestion completed")
                st.json(response.json())
            else:
                st.error(response.text)
        except requests.RequestException as exc:
            st.error(f"API call failed: {exc}")

st.subheader("2) View Budget Per Client")
try:
    clients_res = requests.get(f"{API_BASE}/clients", timeout=10)
    clients_res.raise_for_status()
    clients = clients_res.json()
except requests.RequestException as exc:
    clients = []
    st.error(f"Could not load clients: {exc}")

if clients:
    options = {f"{c['client_name']} ({c['client_id']})": c["client_id"] for c in clients}
    selected = st.selectbox("Client", list(options.keys()))
    client_id = options[selected]

    try:
        budget_res = requests.get(f"{API_BASE}/clients/{client_id}/budget", timeout=10)
        budget_res.raise_for_status()
        budget = budget_res.json()
        st.metric("Total Budget", str(budget["total_amount"]))
        st.dataframe(budget["lines"], use_container_width=True)
    except requests.RequestException as exc:
        st.error(f"Could not load budget: {exc}")
else:
    st.info("No clients found yet. Upload a CSV to get started.")
