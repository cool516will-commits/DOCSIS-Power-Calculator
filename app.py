import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="DOCSIS RF Power Calculator (Engineer Version)",
    layout="wide"
)

st.title("📡 DOCSIS RF Power Calculator - OFDMA Multi-Channel Edition")

# -----------------------------
# Function: BW scaling
# -----------------------------
def bw_scale_power(power_dbmv, bw_mhz):
    """
    Normalize power to 6 MHz reference (DOCSIS typical comparison)
    Assumption: constant power spectral density
    """
    if bw_mhz <= 0:
        return None
    return power_dbmv + 10 * math.log10(bw_mhz / 6.0)


# -----------------------------
# SIDEBAR SETTINGS
# -----------------------------
st.sidebar.header("⚙️ Global Settings")

ref_bw = st.sidebar.selectbox(
    "Reference Bandwidth",
    [6, 1.6, 3.2, 6.4],
    index=0
)

st.sidebar.write("All OFDMA channels will be normalized to 6 MHz equivalent unless changed.")


# -----------------------------
# SC-QAM SECTION
# -----------------------------
st.header("📶 SC-QAM Channels")

num_scqam = st.number_input("Number of SC-QAM channels", 0, 500, 10)

scqam_data = []
for i in range(num_scqam):
    col1, col2 = st.columns(2)
    with col1:
        pw = st.number_input(f"SC-QAM {i+1} Power (dBmV)", value=0.0, key=f"scqam_pw_{i}")
    with col2:
        bw = st.selectbox(f"SC-QAM {i+1} BW (MHz)", [6], key=f"scqam_bw_{i}")

    scqam_data.append({
        "Channel": f"SC-QAM {i+1}",
        "Power_dBmV": pw,
        "BW_MHz": bw,
        "Normalized_6MHz": bw_scale_power(pw, bw)
    })

scqam_df = pd.DataFrame(scqam_data)


# -----------------------------
# OFDM SECTION
# -----------------------------
st.header("📡 OFDM Channels")

num_ofdm = st.number_input("Number of OFDM channels", 0, 20, 1)

ofdm_data = []
for i in range(num_ofdm):
    col1, col2, col3 = st.columns(3)

    with col1:
        pw = st.number_input(f"OFDM {i+1} Power (dBmV)", value=0.0, key=f"ofdm_pw_{i}")
    with col2:
        bw = st.number_input(f"OFDM {i+1} BW (MHz)", value=192.0, key=f"ofdm_bw_{i}")
    with col3:
        center = st.number_input(f"Center Freq (MHz)", value=0.0, key=f"ofdm_cf_{i}")

    ofdm_data.append({
        "Channel": f"OFDM {i+1}",
        "Power_dBmV": pw,
        "BW_MHz": bw,
        "Center_Freq_MHz": center,
        "Normalized_6MHz": bw_scale_power(pw, bw)
    })

ofdm_df = pd.DataFrame(ofdm_data)


# -----------------------------
# OFDMA SECTION (MULTI-CHANNEL FIXED)
# -----------------------------
st.header("📡 OFDMA Channels (Multi-Channel Support)")

st.caption("👉 你可以新增很多條 OFDMA，每條 BW 都可以不同")

default_ofdma = pd.DataFrame([
    {
        "Channel": "OFDMA 1",
        "Power_dBmV": 0.0,
        "BW_MHz": 6.4,
        "Center_Freq_MHz": 0.0
    }
])

ofdma_df = st.data_editor(
    default_ofdma,
    num_rows="dynamic",
    use_container_width=True
)

# compute normalized
ofdma_df["Normalized_6MHz"] = ofdma_df.apply(
    lambda r: bw_scale_power(r["Power_dBmV"], r["BW_MHz"]),
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
# TOTAL POWER ESTIMATION
# -----------------------------
st.header("📈 Total Power Estimation (Simple Model)")

def total_power(df):
    if len(df) == 0:
        return 0
    lin = df["Normalized_6MHz"].apply(lambda x: 10**(x/10)).sum()
    return 10 * math.log10(lin)

total_scqam = total_power(scqam_df)
total_ofdm = total_power(ofdm_df)
total_ofdma = total_power(ofdma_df)

st.metric("SC-QAM Total (dBmV eq. 6MHz)", round(total_scqam, 2))
st.metric("OFDM Total (dBmV eq. 6MHz)", round(total_ofdm, 2))
st.metric("OFDMA Total (dBmV eq. 6MHz)", round(total_ofdma, 2))

st.divider()

st.metric(
    "🔥 GRAND TOTAL (All Channels)",
    round(
        10 * math.log10(
            10**(total_scqam/10) +
            10**(total_ofdm/10) +
            10**(total_ofdma/10)
        ),
        2
    )
)
