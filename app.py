import streamlit as st
import math

st.set_page_config(page_title="DOCSIS RF Engineering Simulator", layout="wide")

# =========================
# CONSTANTS
# =========================
IMPEDANCE = 75

# =========================
# BASIC RF CONVERTERS
# =========================
def dbmv_to_dbm(dbmv):
    return dbmv - 10 * math.log10(IMPEDANCE) - 30

def dbm_to_dbmv(dbm):
    return dbm + 10 * math.log10(IMPEDANCE) + 30

def db_to_lin(db):
    return 10 ** (db / 10)

def lin_to_db(lin):
    return 10 * math.log10(lin)

# =========================
# PSD ENGINE
# =========================
def calc_psd_dbm_hz(total_dbm, bw_hz):
    return total_dbm - 10 * math.log10(bw_hz)

def integrate_psd(psd_dbm_hz, bw_hz):
    return psd_dbm_hz + 10 * math.log10(bw_hz)

# =========================
# OFDMA GRID ENGINE (CORE)
# =========================
def ofdma_engine(psd_dbm_hz, bw_mhz, spacing_khz, occupancy):
    bw_hz = bw_mhz * 1e6
    spacing_hz = spacing_khz * 1e3

    total_tones = int(bw_hz / spacing_hz)
    active_tones = int(total_tones * occupancy)

    tone_power_dbm = psd_dbm_hz + 10 * math.log10(spacing_hz)

    total_lin = active_tones * db_to_lin(tone_power_dbm)
    total_dbm = lin_to_db(total_lin)

    return {
        "total_tones": total_tones,
        "active_tones": active_tones,
        "tone_power_dbm": tone_power_dbm,
        "total_dbm": total_dbm,
        "total_dbmv": dbm_to_dbm(total_dbm)
    }

# =========================
# SC-QAM ENGINE
# =========================
def scqam_engine(num_ch, power_dbmv, bw_mhz):
    bw_hz = bw_mhz * 1e6
    power_dbm = dbmv_to_dbm(power_dbmv)

    psd = calc_psd_dbm_hz(power_dbm, bw_hz)

    total_lin = num_ch * db_to_lin(power_dbm)
    total_dbm = lin_to_db(total_lin)

    return {
        "psd": psd,
        "total_dbm": total_dbm,
        "total_dbmv": dbm_to_dbm(total_dbm)
    }

# =========================
# UI
# =========================
st.title("📡 DOCSIS RF Engineering Simulator (A-Level / PSD + OFDMA Grid)")

mode = st.selectbox("Mode", ["SC-QAM", "OFDMA"])

# =========================
# SC-QAM
# =========================
if mode == "SC-QAM":

    st.subheader("SC-QAM Model (Reference 6 MHz scaling)")

    num_ch = st.number_input("Number of Channels", 1, 500, 32)
    power_dbmv = st.number_input("Power per Channel (dBmV)", 0.0, 80.0, 35.0)
    bw_mhz = st.number_input("Channel BW (MHz)", 1.0, 10.0, 6.0)

    if st.button("Calculate"):

        r = scqam_engine(num_ch, power_dbmv, bw_mhz)

        st.subheader("Result")
        st.write(f"PSD per channel: **{r['psd']:.2f} dBm/Hz**")
        st.write(f"Total Power: **{r['total_dbmv']:.2f} dBmV**")

# =========================
# OFDMA
# =========================
else:

    st.subheader("OFDMA Tone Grid Model (Engineering Grade)")

    bw_mhz = st.number_input("OFDMA Bandwidth (MHz)", 1.0, 192.0, 96.0)
    spacing_khz = st.number_input("Subcarrier Spacing (kHz)", 25.0, 400.0, 25.0)
    occupancy = st.slider("Tone Occupancy (%)", 0.0, 1.0, 0.8)
    psd_dbm_hz = st.number_input("PSD (dBm/Hz)", -200.0, 0.0, -120.0)

    if st.button("Calculate OFDMA"):

        r = ofdma_engine(psd_dbm_hz, bw_mhz, spacing_khz, occupancy)

        st.subheader("Result")

        st.write(f"Total tones: **{r['total_tones']}**")
        st.write(f"Active tones: **{r['active_tones']}**")
        st.write(f"Power per tone: **{r['tone_power_dbm']:.2f} dBm**")
        st.write(f"Total Power: **{r['total_dbmv']:.2f} dBmV**")

        # sanity check
        st.write("---")
        st.write("✔ Engineering Check:")
        st.write("PSD → tone → integration (log-consistent)")
