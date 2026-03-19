import streamlit as st


def init_state():
    defaults = {
        "page": "empresa",
        "empresa": None,
        "conta": None,
        "tab": "dashboard",
        "historico": [],   # list of dicts
        "status": {},      # emp_id -> ok|pendente
        "resultado": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_status(emp_id: str, conta_id: str) -> str:
    key = f"{emp_id}_{conta_id}"
    return st.session_state.status.get(key, "pendente")


def set_status(emp_id: str, conta_id: str, value: str):
    key = f"{emp_id}_{conta_id}"
    st.session_state.status[key] = value


def add_historico(item: dict):
    hist = st.session_state.historico
    # Remove duplicata mesmo emp+conta+ref
    hist = [
        h for h in hist
        if not (h["emp"] == item["emp"] and h["id"] == item["id"] and h["ref"] == item["ref"])
    ]
    hist.append(item)
    st.session_state.historico = hist
