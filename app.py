import streamlit as st
import pandas as pd
import math
import numpy as np

st.set_page_config(
    page_title="DOCSIS RF Power Calculator Pro",
    layout="wide"
)

st.title("📡 DOCSIS RF Power Calculator - Stable Edition")


# -----------------------------
# SAFE POWER MODEL
# -----------------------------
def bw_scale_power(power_dbmv, bw_mhz):
    if bw_mhz is None or power_dbmv is None:
        return np.nan
    try:
        bw_mhz = float(bw_mhz)
        power_dbmv = float(power_dbmv)
        if bw_mhz <= 0:
            return np.nan
        return power_dbmv + 10 * math.log10(bw_mhz / 6.0)
    except:
        return np.nan


def total_power(df):
    if df is None or df.empty:
        return 0

    if "Normalized_6MHz" not in df.columns:
        return 0

    vals = pd.to_numeric(df["Normalized_6MHz"], errors="coerce").dropna()

    if len(vals) == 0:
        return 0

    lin = (10 ** (vals / 10)).sum()

    if lin <= 0:
        return 0

    return 10 * math.log10(lin)


def safe_df(df):
    """ensure numeric safety"""
    df = df.copy()

    for col in ["Power_dBmV", "BW_MHz"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# -----------------------------
# SC-QAM
# -----------------------------
st.header("📶 SC-QAM (Dynamic)")

scqam_df = st.data_editor(
    pd.DataFrame([
        {"Channel": "SC-QAM 1", "Power_dBmV": 0.0, "BW_MHz": 6.0}
    ]),
    num_rows="dynamic",
    use_container_width=True
)

scqam_df = safe_df(scqam_df)

scqam_df["Normalized_6MHz"] = scqam_df.apply(
    lambda r: bw_scale_power(r.get("Power_dBmV"), r.get("BW_MHz")),
    axis=1
)


# -----------------------------
# OFDM
# -----------------------------
st.header("📡 OFDM (Dynamic)")

ofdm_df = st.data_editor(
    pd.DataFrame([
        {"Channel": "OFDM 1", "Power_dBmV": 0.0, "BW_MHz": 192.0}
    ]),
    num_rows="dynamic",
    use_container_width=True
)

ofdm_df = safe_df(ofdm_df)

ofdm_df["Normalized_6MHz"] = ofdm_df.apply(
    lambda r: bw_scale_power(r.get("Power_dBmV"), r.get("BW_MHz")),
    axis=1
)


# -----------------------------
# OFDMA
# -----------------------------
st.header("📡 OFDMA (Dynamic Multi-Channel)")

ofdma_df = st.data_editor(
    pd.DataFrame([
        {"Channel": "OFDMA 1", "Power_dBmV": 0.0, "BW_MHz": 6.4}
    ]),
    num_rows="dynamic",
    use_container_width=True
)

ofdma_df = safe_df(ofdma_df)

ofdma_df["Normalized_6MHz"] = ofdma_df.apply(
    lambda r: bw_scale_power(r.get("Power_dBmV"), r.get("BW_MHz")),
    axis=1
)


# -----------------------------
# SUMMARY
# -----------------------------
st.header("📊 Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("SC-QAM")
    st.dataframe(scqam_df, use_container_width=True)

with col2:
    st.subheader("OFDM")
    st.dataframe(ofdm_df, use_container_width=True)

with col3:
    st.subheader("OFDMA")
    st.dataframe(ofdma_df, use_container_width=True)


# -----------------------------
# TOTAL
# -----------------------------
st.header("📈 Total Power")

scqam_total = total_power(scqam_df)
ofdm_total = total_power(ofdm_df)
ofdma_total = total_power(ofdma_df)

st.metric("SC-QAM Total", round(scqam_total, 2))
st.metric("OFDM Total", round(ofdm_total, 2))
st.metric("OFDMA Total", round(ofdma_total, 2))

grand_total = 10 * math.log10(
    sum([
        10 ** (scqam_total / 10) if scqam_total else 0,
        10 ** (ofdm_total / 10) if ofdm_total else 0,
        10 ** (ofdma_total / 10) if ofdma_total else 0
    ])
)

st.divider()
st.metric("🔥 GRAND TOTAL", round(grand_total, 2))
