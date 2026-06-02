import streamlit as st
import math

st.set_page_config(page_title="DOCSIS RF Power Tool (Engineering Grade)", layout="wide")

# ----------------------------
# RF CONSTANTS
# ----------------------------
IMPEDANCE = 75  # ohm

def dbmv_to_dbm(dbmv):
    return dbmv - 10 * math.log10(IMPEDANCE) - 30

def dbm_to_dbmv(dbm):
    return dbm + 10 * math.log10(IMPEDANCE) + 30

def lin_power(db):
    return 10 ** (db / 10)

def db_power(lin):
    return 10 * math.log10(lin)

# ----------------------------
# PSD ENGINE
# ----------------------------
def calc_psd(total_power_dbm, bw_mhz):
    bw_hz = bw_mhz * 1e6
    return total_power_dbm - 10 * math.log10(bw_hz)

def calc_total_from_psd(psd_dbm_hz, bw_mhz):
    bw_hz = bw_mhz * 1e6
    return psd_dbm_hz + 10 * math.log10(bw_hz)

# ----------------------------
# UI
# ----------------------------
st.title("📡 DOCSIS RF Power Calculator (Engineering Grade + PSD Engine)")

mode = st.selectbox("Mode", ["SC-QAM", "OFDMA"])

st.subheader("Input")

if mode == "SC-QAM":

    num_ch = st.number_input("Number of SC-QAM Channels", 1, 500, 32)
    power_dbmv = st.number_input("Power per Channel (dBmV)", 0.0, 80.0, 35.0)
    bw_mhz = st.number_input("Channel BW (MHz)", 1.0, 10.0, 6.0)

    if st.button("Calculate"):

        power_dbm = dbmv_to_dbm(power_dbmv)
        psd = calc_psd(power_dbm, bw_mhz)

        total_lin = 0.0

        for _ in range(num_ch):
            total_lin += lin_power(power_dbm)

        total_dbm = db_power(total_lin)

        total_dbmv = dbm_to_dbmv(total_dbm)

        st.subheader("Result")

        st.write(f"Per Channel PSD: **{psd:.2f} dBm/Hz**")
        st.write(f"Total Power (linear sum): **{total_dbmv:.2f} dBmV**")
        st.write(f"Total Power (dBm): **{total_dbm:.2f} dBm**")


# ----------------------------
# OFDMA ENGINE (PSD BASED)
# ----------------------------
else:

    num_subcarriers = st.number_input("Number of Subcarriers", 1, 20000, 4096)
    spacing_khz = st.number_input("
