import streamlit as st
import math

st.set_page_config(page_title="DOCSIS RF Tool", layout="wide")

st.title("📡 DOCSIS RF Calculator (Stable Per-Channel Model)")


# -----------------------------
# FUNCTION
# -----------------------------
def norm(p, bw):
    return float(p) + 10 * math.log10(float(bw) / 6.0)


def lin(db):
    return 10 ** (db / 10)


def calc_total(list_db):
    return 10 * math.log10(sum(lin(x) for x in list_db if x is not None)) if list_db else 0


# -----------------------------
# SC-QAM
# -----------------------------
st.header("📶 SC-QAM")

n_scqam = st.number_input("SC-QAM Channel Count", 1, 200, 3)

scqam_list = []

for i in range(n_scqam):
    c1, c2, c3 = st.columns(3)
    with c1:
        p = st.number_input(f"CH{i+1} Power", value=0.0, key=f"sc_p_{i}")
    with c2:
        bw = st.selectbox(f"CH{i+1} BW", [1.6, 3.2, 6.0, 6.4], key=f"sc_bw_{i}")
    with c3:
        st.write(" ")

    scqam_list.append(norm(p, bw))


# -----------------------------
# OFDM
# -----------------------------
st.header("📡 OFDM")

n_ofdm = st.number_input("OFDM Channel Count", 1, 10, 1)

ofdm_list = []

for i in range(n_ofdm):
    c1, c2 = st.columns(2)
    with c1:
        p = st.number_input(f"OFDM{i+1} Power", value=0.0, key=f"ofdm_p_{i}")
    with c2:
        bw = st.number_input(f"OFDM{i+1} BW", value=192.0, key=f"ofdm_bw_{i}")

    ofdm_list.append(norm(p, bw))


# -----------------------------
# OFDMA
# -----------------------------
st.header("📡 OFDMA")

n_ofdma = st.number_input("OFDMA Channel Count", 1, 10, 1)

ofdma_list = []

for i in range(n_ofdma):
    c1, c2 = st.columns(2)
    with c1:
        p = st.number_input(f"OFDMA{i+1} Power", value=0.0, key=f"ofdma_p_{i}")
    with c2:
        bw = st.selectbox(f"OFDMA{i+1} BW", [1.6, 3.2, 6.4, 12.8, 25.6], key=f"ofdma_bw_{i}")

    ofdma_list.append(norm(p, bw))


# -----------------------------
# RESULT
# -----------------------------
st.header("📊 Result")

scqam = calc_total(scqam_list)
ofdm = calc_total(ofdm_list)
ofdma = calc_total(ofdma_list)

total = 10 * math.log10(
    lin(scqam) + lin(ofdm) + lin(ofdma)
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("SC-QAM", round(scqam, 2))

with c2:
    st.metric("OFDM", round(ofdm, 2))

with c3:
    st.metric("OFDMA", round(ofdma, 2))

with c4:
    st.metric("TOTAL", round(total, 2))
