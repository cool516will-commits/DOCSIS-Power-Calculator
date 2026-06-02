import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="DOCSIS RF Power Calculator Pro",
    layout="wide"
)

st.title("📡 DOCSIS RF Power Calculator - Full Dynamic Channel Edition")


# -----------------------------
# Power scaling model
# -----------------------------
def bw_scale_power(power_dbmv, bw_mhz):
    if bw_mhz <= 0:
        return None
    return power_dbmv + 10 * math.log10(bw_mhz / 6.0)


def total_power(df):
    if df.empty:
        return 0
    lin = df["Normalized_6MHz"].fillna(0).apply(lambda x: 10**(x/10)).sum()
    return 10 * math.log10(lin)


# -----------------------------
# SC-QAM (FULL DYNAMIC)
# -----------------------------
st.header("📶 SC-QAM Channels (Fully Editable)")

scqam_default = pd.DataFrame([
    {
        "Channel": "SC-QAM 1",
        "Power_dBmV": 0.0,
        "BW_MHz": 6.0,
        "Center_Freq_MHz": 0.0
    }
])

scqam_df = st.data_editor(
    scqam_default,
    num_rows="dynamic",
    use_container_width=True
)

scqam_df["Normalized_6MHz"] = scqam_df.apply(
    lambda r: bw_scale_power(r["Power_dBmV"], r["BW_MHz"]),
    axis=1
)


# -----------------------------
# OFDM (FULL DYNAMIC)
# -----------------------------
st.header("📡 OFDM Channels (Fully Editable)")

ofdm_default = pd.DataFrame([
    {
        "Channel": "OFDM 1",
        "Power_dBmV": 0.0,
        "BW_MHz": 192.0,
        "Center_Freq_MHz": 0.0
    }
])

ofdm_df = st.data_editor(
    ofdm_default,
    num_rows="dynamic",
    use_container_width=True
)

ofdm_df["Normalized_6MHz"] = ofdm_df.apply(
    lambda r: bw_scale_power(r["Power_dBmV"], r["BW_MHz"]),
    axis=1
)


# -----------------------------
# OFDMA (FULL DYNAMIC)
# -----------------------------
st.header("📡 OFDMA Channels (Fully Editable)")

ofdma_default = pd.DataFrame([
    {
        "Channel": "OFDMA 1",
        "Power_dBmV": 0.0,
        "BW_MHz": 6.4,
        "Center_Freq_MHz": 0.0
    }
])

ofdma_df = st.data_editor(
    ofdma_default,
    num_rows="dynamic",
    use_container_width=True
)

ofdma_df["Normalized_6MHz"] = ofdma_df.apply(
    lambda r: bw_scale_power(r["Power_dBmV"], r["BW_MHz"]),
    axis=1
)


# -----------------------------
# SUMMARY TABLES
# -----------------------------
st.header("📊 Summary")

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("SC-QAM")
    st.dataframe(scqam_df, use_container_width=True)

with c2:
    st.subheader("OFDM")
    st.dataframe(ofdm_df, use_container_width=True)

with c3:
    st.subheader("OFDMA")
    st.dataframe(ofdma_df, use_container_width=True)


# -----------------------------
# TOTAL POWER
# -----------------------------
st.header("📈 Power Summary (Engineering Model)")

scqam_total = total_power(scqam_df)
ofdm_total = total_power(ofdm_df)
ofdma_total = total_power(ofdma_df)

st.metric("SC-QAM Total (6MHz eq.)", round(scqam_total, 2))
st.metric("OFDM Total (6MHz eq.)", round(ofdm_total, 2))
st.metric("OFDMA Total (6MHz eq.)", round(ofdma_total, 2))


grand_total = 10 * math.log10(
    10**(scqam_total/10) +
    10**(ofdm_total/10) +
    10**(ofdma_total/10)
)

st.divider()
st.metric("🔥 GRAND TOTAL RF POWER", round(grand_total, 2))
