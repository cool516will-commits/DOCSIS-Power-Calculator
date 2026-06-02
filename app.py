import streamlit as st
import math

st.set_page_config(page_title="DOCSIS RF Engineer Tool", layout="wide")

st.title("📡 DOCSIS RF Calculator (Engineering Safe Model)")


# -----------------------------
# BASIC FUNCTIONS
# -----------------------------
def lin(db):
    return 10 ** (db / 10)


def db(lin_val):
    return 10 * math.log10(lin_val) if lin_val > 0 else 0


# -----------------------------
# SC-QAM (NO BW MODEL)
# -----------------------------
st.header("📶 SC-QAM (Integrated Power Model)")

n_scqam = st.number_input("SC-QAM Channel Count", 1, 500, 8)

scqam_powers = []

for i in range(n_scqam):
    c1, c2 = st.columns(2)

    with c1:
        p = st.number_input(f"CH{i+1} Power (dBmV)", value=30.0, key=f"sc_{i}")

    with c2:
        st.write("BW fixed = 1.6 MHz (NO scaling)")

    scqam_powers.append(p)

scqam_total_lin = sum(lin(p) for p in scqam_powers)
scqam_total_db = db(scqam_total_lin)


# -----------------------------
# OFDM (PSD MODEL)
# -----------------------------
st.header("📡 OFDM (PSD Model)")

n_ofdm = st.number_input("OFDM Channel Count", 1, 10, 1)

ofdm_bw = st.number_input("OFDM BW (MHz)", 192.0)

ofdm_powers = []

for i in range(n_ofdm):
    c1, c2 = st.columns(2)

    with c1:
        p = st.number_input(f"OFDM{i+1} Power (dBmV)", value=0.0, key=f"ofd_{i}")

    with c2:
        st.write(f"BW = {ofdm_bw} MHz (used for PSD scaling)")

    # PSD normalization
    p_norm = p + 10 * math.log10(ofdm_bw / 6.0)
    ofdm_powers.append(p_norm)

ofdm_total_db = db(sum(lin(p) for p in ofdm_powers))


# -----------------------------
# OFDMA (PSD MODEL)
# -----------------------------
st.header("📡 OFDMA (PSD Model)")

n_ofdma = st.number_input("OFDMA Channel Count", 1, 10, 1)

ofdma_bw = st.selectbox("OFDMA BW (MHz)", [1.6, 3.2, 6.4, 12.8, 25.6], index=2)

ofdma_powers = []

for i in range(n_ofdma):
    c1, c2 = st.columns(2)

    with c1:
        p = st.number_input(f"OFDMA{i+1} Power (dBmV)", value=0.0, key=f"ofdma_{i}")

    with c2:
        st.write(f"BW = {ofdma_bw} MHz")

    p_norm = p + 10 * math.log10(ofdma_bw / 6.0)
    ofdma_powers.append(p_norm)

ofdma_total_db = db(sum(lin(p) for p in ofdma_powers))


# -----------------------------
# FINAL SUM (SAFE DOMAIN)
# -----------------------------
st.header("📊 Final Result")

grand_lin = (
    lin(scqam_total_db) +
    lin(ofdm_total_db) +
    lin(ofdma_total_db)
)

grand_db = db(grand_lin)


# -----------------------------
# OUTPUT
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("SC-QAM (true sum)", round(scqam_total_db, 2))

with col2:
    st.metric("OFDM (PSD)", round(ofdm_total_db, 2))

with col3:
    st.metric("OFDMA (PSD)", round(ofdma_total_db, 2))

with col4:
    st.metric("🔥 TOTAL", round(grand_db, 2))
