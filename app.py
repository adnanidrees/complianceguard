import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ComplianceGuard — Consent Manager", page_icon="✅", layout="wide")
st.title("✅ ComplianceGuard — Consent & Opt-out Manager")
st.caption("Upload contacts CSV → filter by consent (yes/no) + unsubscribe keywords → export clean sendable list.")

st.markdown("**CSV columns suggested:** `phone, name (optional), consent (yes/no), notes (optional)`")

csv = st.file_uploader("Upload contacts CSV", type=["csv"])
keyword_text = st.text_input("Unsubscribe keywords (comma-separated)", "stop, unsub, remove, optout, unsubscribe")
normalize_phone = st.checkbox("Normalize PK phone format (remove spaces/dashes, keep digits only)", True)

if csv:
    df = pd.read_csv(csv, dtype=str).fillna("")
    st.subheader("Preview")
    st.dataframe(df.head(20), use_container_width=True)

    # Normalize phone numbers
    if normalize_phone and "phone" in df.columns:
        df["phone"] = df["phone"].astype(str).str.replace(r"\D", "", regex=True)

    # Consent boolean
    def to_bool(x: str):
        x = (x or "").strip().lower()
        return x in ("yes", "y", "true", "1", "ok", "allowed", "consent")
    consent_col = "consent" if "consent" in df.columns else None
    if consent_col:
        df["consent_bool"] = df[consent_col].map(to_bool)
    else:
        df["consent_bool"] = True  # if no column, assume consented (user can refine)

    # Unsubscribe keywords
    kws = [k.strip().lower() for k in keyword_text.split(",") if k.strip()]
    def has_unsub(row):
        if not kws: return False
        text = " ".join([str(v).lower() for v in row.values])
        return any(k in text for k in kws)
    df["unsub_request"] = df.apply(has_unsub, axis=1)

    # Final flag
    df["sendable"] = df["consent_bool"] & ~df["unsub_request"]

    # Summary
    total = len(df); sendable = int(df["sendable"].sum()); blocked = total - sendable
    st.markdown(f"**Total:** {total} | **Sendable:** {sendable} | **Blocked (no consent / unsub):** {blocked}")

    with st.expander("🔎 Blocked (review)"):
        st.dataframe(df[~df["sendable"]], use_container_width=True)
    with st.expander("✅ Sendable list"):
        st.dataframe(df[df["sendable"]], use_container_width=True)

    # Downloads
    out_cols = [c for c in df.columns if c not in ("consent_bool","unsub_request")]
    sendable_df = df[df["sendable"]][out_cols]
    buf1 = io.BytesIO(); sendable_df.to_csv(buf1, index=False, encoding="utf-8")
    st.download_button("⬇️ Download sendable.csv", buf1.getvalue(), "sendable.csv", "text/csv")

    buf2 = io.BytesIO(); df.to_csv(buf2, index=False, encoding="utf-8")
    st.download_button("⬇️ Download labeled_all.csv", buf2.getvalue(), "labeled_all.csv", "text/csv")

st.markdown("---")
st.caption("Tip: Broadcasts me hamesha opt-out keyword support rakhein (e.g., 'STOP').")
