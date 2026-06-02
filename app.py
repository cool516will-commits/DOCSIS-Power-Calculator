import streamlit as st
import pandas as pd
import math
import numpy as np

st.set_page_config(page_title="DOCSIS RF Tool", layout="wide")

st.title("📡 DOCSIS RF Power Calculator (Per-Channel True Model)")


# -----------------------------
# FUNCTION
# -----------------------------
def bw_scale(p, bw):
    try:
        return float(p) + 10 * math.log10(float(bw) / 6.0)
    except:
        return np.nan


def to_lin(db):
    try:
        return 10 ** (float(db) / 10)
    except:
        return 0


def total_db(series):
    vals = pd.to_numeric(series, errors="coerce").dropna()
    if len(vals) == 0:
        return 0
    return 10 * math.log10(sum([10 ** (v / 10) for v in vals]))


# -----------------------------
# SC-QAM (PER CHANNEL)
# -----------------------------
st.header("📶 SC-QAM (Per Channel)")

scqam_df = st.data_editor(
    pd.DataFrame([
        {"Channel": "SC-QAM 1", "Power_dBmV": 0.0, "BW_MHz": 6.0}
    ]),
    num_rows="dynamic",
    use_container_width=True
)

scqam_df["Normalized"] = scqam_df.apply(
    lambda r: bw_scale(r["Power_dBmV"], r["BW_MHz"]),
    axis=1
)


# -----------------------------
# OFDM (PER BLOCK)
# -----------------------------
st.header("📡 OFDM (Per Channel)")

ofdm_df = st.data_editor(
    pd.DataFrame([
        {"Channel": "OFDM 1", "Power_dBmV": 0.0, "BW_MHz": 192.0}
    ]),
    num_rows="dynamic",
    use_container_width=True
)

ofdm_df["Normalized"] = ofdm_df.apply(
    lambda r: bw_scale(r["Power_dBmV"], r["BW_MHz"]),
    axis=1
)


# -----------------------------
# OFDMA (PER CHANNEL)
# -----------------------------
st.header("📡 OFDMA (Per Channel)")

ofdma_df = st.data_editor(
    pd.DataFrame([
        {"Channel": "OFDMA 1", "Power_dBmV": 0.0, "BW_MHz": 6.4}
    ]),
    num_rows="dynamic",
    use_container_width=True
)

ofdma_df["Normalized"] = ofdma_df.apply(
    lambda r: bw_scale(r["Power_dBmV"], r["BW_MHz"]),
    axis=1
)


# -----------------------------
# RESULTS
# -----------------------------
st.header("📊 Results")

scqam_total = total_db(scqam_df["Normalized"])
ofdm_total = total_db(ofdm_df["Normalized"])
ofdma_total = total_db(ofdma_df["Normalized"])

grand_lin = (
    sum([10 ** (scqam_total / 10),
         10 ** (ofdm_total / 10),
         10 ** (ofdma_total / 10)])
)

grand_db = 10 * math.log10(grand_lin) if grand_lin > 0 else 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("SC-QAM", round(scqam_total, 2))

with col2:
    st.metric("OFDM", round(ofdm_total, 2))

with col3:
    st.metric("OFDMA", round(ofdma_total, 2))

with col4:
    st.metric("🔥 TOTAL", round(grand_db, 2))
