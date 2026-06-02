import streamlit as st
import math

st.set_page_config(
    page_title="EdisonSu DOCSIS Power Calculator",
    layout="wide"
)

st.title("📡 EdisonSu DOCSIS Power Calculator")

# ==========================================
# Functions
# ==========================================

def db_to_linear(db):
    return 10 ** (db / 10)

def linear_to_db(linear):
    return 10 * math.log10(linear)

# ==========================================
# Tabs
# ==========================================

tab1, tab2, tab3 = st.tabs([
    "OFDMA BW Converter",
    "SC-QAM + OFDMA",
    "Multi Channel Sum"
])

# ==========================================
# TAB1
# ==========================================

with tab1:

    st.header("OFDMA Power Converter")

    col1, col2 = st.columns(2)

    with col1:

        measured_power = st.number_input(
            "Measured Power (dBmV)",
            value=15.0,
            step=0.1
        )

        measured_bw = st.number_input(
            "Measured Bandwidth (MHz)",
            value=96.0,
            step=0.1
        )

        target_bw = st.number_input(
            "Target Bandwidth (MHz)",
            value=6.0,
            step=0.1
        )

    with col2:

        if measured_bw > 0 and target_bw > 0:

            converted_power = (
                measured_power
                - 10 * math.log10(measured_bw / target_bw)
            )

            st.metric(
                "Converted Power (dBmV)",
                f"{converted_power:.2f}"
            )

            st.info(
                f"{measured_power:.2f} dBmV @ {measured_bw:.2f} MHz\n\n"
                f"Equivalent to {converted_power:.2f} dBmV @ {target_bw:.2f} MHz"
            )

# ==========================================
# TAB2
# ==========================================

with tab2:

    st.header("SC-QAM + OFDMA Total Power")

    col1, col2 = st.columns(2)

    with col1:

        scqam_power = st.number_input(
            "SC-QAM Power (dBmV)",
            value=0.0,
            step=0.1
        )

        scqam_count = st.number_input(
            "SC-QAM Count",
            value=32,
            step=1
        )

    with col2:

        ofdma_power = st.number_input(
            "OFDMA Power (dBmV)",
            value=15.0,
            step=0.1
        )

        ofdma_count = st.number_input(
            "OFDMA Count",
            value=1,
            step=1
        )

        ofdma_bw = st.number_input(
            "OFDMA Bandwidth (MHz)",
            value=96.0,
            step=0.1
        )

    if st.button("Calculate Total Power"):

        total_linear = 0

        # SC-QAM
        for _ in range(int(scqam_count)):
            total_linear += db_to_linear(scqam_power)

        # OFDMA
        for _ in range(int(ofdma_count)):
            total_linear += db_to_linear(ofdma_power)

        total_dbmv = linear_to_db(total_linear)

        equivalent_6mhz = (
            ofdma_power
            - 10 * math.log10(ofdma_bw / 6)
        )

        st.success(
            f"Total DS Power = {total_dbmv:.2f} dBmV"
        )

        st.info(
            f"OFDMA Equivalent 6MHz Power = "
            f"{equivalent_6mhz:.2f} dBmV"
        )

# ==========================================
# TAB3
# ==========================================

with tab3:

    st.header("Multi Channel Power Sum")

    st.write(
        "Paste one power value per line"
    )

    power_text = st.text_area(
        "Power List",
        height=250,
        placeholder="""
14.01
15.03
12.43
12.52
12.48
"""
    )

    if st.button("Sum Channel Power"):

        try:

            values = [
                float(x.strip())
                for x in power_text.splitlines()
                if x.strip()
            ]

            if len(values) == 0:
                st.warning("No data entered")

            else:

                total_linear = sum(
                    db_to_linear(v)
                    for v in values
                )

                total_db = linear_to_db(
                    total_linear
                )

                st.success(
                    f"Total Power = {total_db:.2f} dBmV"
                )

                st.write(
                    f"Channels Count = {len(values)}"
                )

        except Exception:

            st.error(
                "Please enter valid numbers."
            )

# ==========================================
# Footer
# ==========================================

st.divider()

st.caption(
    "EdisonSu DOCSIS RF Power Calculator v1.0"
)
