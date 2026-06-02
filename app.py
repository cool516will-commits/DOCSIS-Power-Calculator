import streamlit as st
import math

st.set_page_config(page_title="DOCSIS RF Tool", layout="wide")

st.title("📡 DOCSIS RF Power Calculator (Clean Engineering Mode)")


# -----------------------------
# FUNCTION
# -----------------------------
def bw_scale(power_dbmv, bw_mhz):
    return power_dbmv + 10 * math.log10(bw_mhz / 6.0)


def lin(db):
    return 10 ** (db / 10)


def total(db_value):
    return lin(db_value)


# -----------------------------
# SC-QAM
# -----------------------------
st.header("📶 SC-QAM")

scqam_count = st.number_input("SC-QAM Channel Count", 0, 500, 10)

scqam_power = st.number_input("SC-QAM Power per Channel (dBmV)", 0.0)

scqam_bw = st.selectbox(
    "SC-QAM BW (MHz)",
    [1.6, 3.2, 6.0, 6.4],
    index=2
)

scqam_db = bw_scale(scqam_power, scqam_bw)

scqam_total_lin = lin(scqam_db) * scqam_count


# -----------------------------
# OFDM
# -----------------------------
st.header("📡 OFDM")

ofdm_count = st.number_input("OFDM Channel Count", 0, 10, 1)

ofdm_power = st.number_input("OFDM Power per Channel (dBmV)", 0.0)

ofdm_bw = st.number_input("OFDM BW (MHz)", 192.0)

ofdm_db = bw_scale(ofdm_power, ofdm_bw)

ofdm_total_lin = lin(ofdm_db) * ofdm_count


# -----------------------------
# OFDMA
# -----------------------------
st.header("📡 OFDMA")

ofdma_count = st.number_input("OFDMA Channel Count", 0, 10, 1)

ofdma_power = st.number_input("OFDMA Power per Channel (dBmV)", 0.0)

ofdma_bw = st.selectbox(
    "OFDMA BW (MHz)",
    [1.6, 3.2, 6.4, 12.8, 25.6, 51.2],
    index=2
)

ofdma_db = bw_scale(ofdma_power, ofdma_bw)

ofdma_total_lin = lin(ofdma_db) * ofdma_count


# -----------------------------
# RESULT
# -----------------------------
st.header("📊 Result")

scqam_db_total = 10 * math.log10(scqam_total_lin) if scqam_total_lin > 0 else 0
ofdm_db_total = 10 * math.log10(ofdm_total_lin) if ofdm_total_lin > 0 else 0
ofdma_db_total = 10 * math.log10(ofdma_total_lin) if ofdma_total_lin > 0 else 0

grand_lin = scqam_total_lin + ofdm_total_lin + ofdma_total_lin
grand_db = 10 * math.log10(grand_lin) if grand_lin > 0 else 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("SC-QAM Total", round(scqam_db_total, 2))

with col2:
    st.metric("OFDM Total", round(ofdm_db_total, 2))

with col3:
    st.metric("OFDMA Total", round(ofdma_db_total, 2))

with col4:
    st.metric("🔥 GRAND TOTAL", round(grand_db, 2))
