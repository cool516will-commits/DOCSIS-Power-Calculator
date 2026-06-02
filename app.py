import streamlit as st
import math

st.set_page_config(page_title="DOCSIS RF Calculator", layout="wide")

st.title("📡 DOCSIS RF Power Calculator (Pure Engineering Mode)")


# -----------------------------
# FUNCTION
# -----------------------------
def bw_scale(power_dbmv, bw_mhz):
    if bw_mhz <= 0:
        return None
    return power_dbmv + 10 * math.log10(bw_mhz / 6.0)


def lin(p_db):
    return 10 ** (p_db / 10)


# -----------------------------
# SC-QAM
# -----------------------------
st.header("📶 SC-QAM")

scqam_count = st.number_input("SC-QAM Channel Count", 0, 500, 10)
scqam_power = st.number_input("SC-QAM Power (dBmV per channel)", 0.0)

scqam_bw = 6.0
scqam_norm = bw_scale(scqam_power, scqam_bw)

scqam_total = lin(scqam_norm) * scqam_count


# -----------------------------
# OFDM
# -----------------------------
st.header("📡 OFDM")

ofdm_count = st.number_input("OFDM Channel Count", 0, 10, 1)
ofdm_power = st.number_input("OFDM Power (dBmV)", 0.0)
ofdm_bw = st.number_input("OFDM BW (MHz)", 192.0)

ofdm_norm = bw_scale(ofdm_power, ofdm_bw)
ofdm_total = lin(ofdm_norm) * ofdm_count


# -----------------------------
# OFDMA
# -----------------------------
st.header("📡 OFDMA")

ofdma_count = st.number_input("OFDMA Channel Count", 0, 10, 1)
ofdma_power = st.number_input("OFDMA Power (dBmV)", 0.0)
ofdma_bw = st.number_input("OFDMA BW (MHz)", 6.4)

ofdma_norm = bw_scale(ofdma_power, ofdma_bw)
ofdma_total = lin(ofdma_norm) * ofdma_count


# -----------------------------
# RESULT
# -----------------------------
st.header("📊 Results")

scqam_db = 10 * math.log10(scqam_total) if scqam_total > 0 else 0
ofdm_db = 10 * math.log10(ofdm_total) if ofdm_total > 0 else 0
ofdma_db = 10 * math.log10(ofdma_total) if ofdma_total > 0 else 0

grand_total = scqam_total + ofdm_total + ofdma_total
grand_db = 10 * math.log10(grand_total) if grand_total > 0 else 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("SC-QAM Total (dBmV eq.)", round(scqam_db, 2))

with col2:
    st.metric("OFDM Total (dBmV eq.)", round(ofdm_db, 2))

with col3:
    st.metric("OFDMA Total (dBmV eq.)", round(ofdma_db, 2))

with col4:
    st.metric("🔥 GRAND TOTAL", round(grand_db, 2))
