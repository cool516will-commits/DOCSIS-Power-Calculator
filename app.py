import streamlit as st
import math

st.set_page_config(
    page_title="DOCSIS Power Calculator",
    layout="wide"
)

# ==========================================
# Functions
# ==========================================

def dbmv_to_linear(dbmv):
    return 10 ** (dbmv / 10)


def linear_to_dbmv(linear):
    if linear <= 0:
        return 0
    return 10 * math.log10(linear)


def total_power_dbmv(power_list):

    if not power_list:
        return 0

    linear_sum = sum(
        dbmv_to_linear(p)
        for p in power_list
    )

    return linear_to_dbmv(linear_sum)


def ofdma_convert(power, source_bw, target_bw):

    if source_bw <= 0:
        return 0

    return (
        power +
        10 * math.log10(
            target_bw / source_bw
        )
    )


# ==========================================
# Title
# ==========================================

st.title("📡 DOCSIS Power Calculator")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(
    [
        "OFDMA",
        "SC-QAM",
        "MULTI"
    ]
)

# ==========================================
# OFDMA
# ==========================================

with tab1:

    st.subheader("OFDMA BW Converter")

    col1, col2 = st.columns(2)

    power = col1.number_input(
        "OFDMA Power (dBmV)",
        value=41.00,
        step=0.01
    )

    source_bw = col2.number_input(
        "OFDMA BW (MHz)",
        value=96.0,
        min_value=0.1,
        step=0.1
    )

    st.markdown("### Reference BW Conversion")

    ref_bws = [
        1.6,
        3.2,
        6.4,
        12.8,
        25.6,
        48,
        96,
        192
    ]

    result_data = []

    for bw in ref_bws:

        result = ofdma_convert(
            power,
            source_bw,
            bw
        )

        result_data.append(
            {
                "BW (MHz)": bw,
                "Power (dBmV)": round(result, 2)
            }
        )

    st.table(result_data)

# ==========================================
# SC-QAM
# ==========================================

with tab2:

    st.subheader(
        "SC-QAM Total Power Calculator"
    )

    num_ch = st.number_input(
        "Channel Count",
        min_value=1,
        max_value=128,
        value=8
    )

    powers = []

    for i in range(num_ch):

        p = st.number_input(
            f"Channel {i+1} Power (dBmV)",
            value=32.25,
            step=0.01,
            key=f"sc_{i}"
        )

        powers.append(p)

    total = total_power_dbmv(
        powers
    )

    st.metric(
        "Total SC-QAM Power",
        f"{total:.2f} dBmV"
    )

# ==========================================
# MULTI
# ==========================================

with tab3:

    st.subheader(
        "OFDMA + SC-QAM Mixed Power"
    )

    st.markdown(
        "### OFDMA Blocks"
    )

    ofdma_count = st.number_input(
        "OFDMA Block Count",
        min_value=0,
        max_value=16,
        value=1
    )

    all_powers = []

    for i in range(ofdma_count):

        col1, col2 = st.columns(2)

        p = col1.number_input(
            f"OFDMA {i+1} Power",
            value=41.0,
            step=0.01,
            key=f"ofdma_p_{i}"
        )

        bw = col2.number_input(
            f"OFDMA {i+1} BW",
            value=96.0,
            min_value=0.1,
            step=0.1,
            key=f"ofdma_bw_{i}"
        )

        all_powers.append(p)

    st.markdown("---")

    st.markdown(
        "### SC-QAM Channels"
    )

    sc_count = st.number_input(
        "SC-QAM Channel Count",
        min_value=0,
        max_value=128,
        value=8
    )

    for i in range(sc_count):

        p = st.number_input(
            f"SC-QAM {i+1} Power",
            value=32.25,
            step=0.01,
            key=f"mix_sc_{i}"
        )

        all_powers.append(p)

    total_mix = total_power_dbmv(
        all_powers
    )

    st.markdown("---")

    st.metric(
        "Total CM Output Power",
        f"{total_mix:.2f} dBmV"
    )

    st.info(
        "Calculation = Linear Power Summation"
    )
