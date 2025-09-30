import os, io, json, time
import streamlit as st

# ---- Bridge Streamlit Secrets → ENV ----
try:
    os.environ.setdefault("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY",""))
except Exception:
    pass

st.set_page_config(page_title="ComplianceGuard", page_icon="✅", layout="wide")
st.title("✅ ComplianceGuard")
st.caption("Consent + opt-out list manager")

st.write('This is a placeholder app body.')