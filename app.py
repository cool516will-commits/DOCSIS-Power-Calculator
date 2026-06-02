import streamlit as st
import math

st.set_page_config(
    page_title="EdisonSu DOCSIS Power Calculator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def db_to_linear(db):
    return 10 ** (db / 10)

def linear_to_db(linear):
    if linear <= 0:
        return 0.0
    return 10 * math.log10(linear)

st.title("📡 EdisonSu DOCSIS Power Calculator")

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 1. OFDMA 頻寬等效換算",
    "📈 2. 多 OFDMA 區塊 PSD 疊加",
    "📟 3. SC-QAM 多通道加總",
    "📊 4. 多通道純數值 TCP 計算"
])

with tab1:
    st.markdown("## OFDMA Power & Bandwidth Converter")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        p_meas = st.number_input("1. 輸入量測到的總功率 (Measured Power, dBmV)", value=33.00, step=0.1, format="%.2f", key="t1_p_meas")
        bw_meas = st.number_input("2. 量測訊號的總頻寬 (Measured Bandwidth, MHz)", value=95.00, step=1.0, format="%.2f", key="t1_bw_meas")
        bw_target = st.number_input("3. 你想換算成的目標頻寬 (Target Bandwidth, MHz)", value=6.50, step=0.1, format="%.2f", key="t1_bw_target")
    with col2:
        st.markdown("#### 等效換算後的功率 (Converted Power)")
        if bw_meas > 0 and bw_target > 0:
            p_converted = p_meas + 10 * math.log10(bw_target / bw_meas)
            st.title(f"{p_converted:.2f} dBmV")

with tab2:
    st.markdown("## 多 OFDMA 區塊等效頻寬功率換算")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        ofdma_num = st.slider("請選擇 OFDMA 區塊數量", min_value=1, max_value=4, value=2, key="t2_ofdma_num")
        ofdma_blocks = []
        for i in range(ofdma_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                p = st.number_input(f"OFDMA 區塊 {i} 總功率 (dBmV)", value=41.00, step=0.1, format="%.2f", key=f"t2_p_{i}")
            with c_lines[1]:
                bw = st.number_input(f"OFDMA 區塊 {i} 總頻寬 (MHz)", value=96.00, step=1.0, format="%.2f", key=f"t2_bw_{i}")
            ofdma_blocks.append({"power": p, "bw": bw})
        t2_target_bw = st.number_input("你想換算成的目標頻寬 (Target Bandwidth, MHz)", value=96.00, step=1.0, format="%.2f", key=f"t2_target_bw")
    with col2:
        raw_linear_sum = sum([db_to_linear(b["power"]) for b in ofdma_blocks])
        raw_tcp = linear_to_db(raw_linear_sum)
        total_physical_bw = sum([b["bw"] for b in ofdma_blocks])
        st.markdown("#### 📊 1. 原始未轉換總合參考")
        st.metric(label="原始通道線性加總總功率 (TCP)", value=f"{raw_tcp:.2f} dBmV")
        total_psd = 0.0
        for b in ofdma_blocks:
            if b["bw"] > 0:
                total_psd += (db_to_linear(b["power"]) / b["bw"])
        st.markdown("#### 🎯 2. 等效目標頻寬換算結果")
        if t2_target_bw > 0:
            final_target_linear = total_psd * t2_target_bw
            final_converted_power = linear_to_db(final_target_linear)
            st.metric(label=f"等效在 {t2_target_bw:.2f} MHz 下的複合總功率", value=f"{final_converted_power:.2f} dBmV")

with tab3:
    st.markdown("## SC-QAM 多通道純公式加總")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        qam_num = st.slider("請選擇 SC-QAM 通道數量", min_value=1, max_value=16, value=8, key="t3_qam_num")
        qam_channels = []
        default_qam_powers = [29.25, 32.00, 32.25, 29.75, 29.75, 30.25, 30.25, 30.75]
        for i in range(qam_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                d_p = default_qam_powers[i] if i < len(default_qam_powers) else 30.00
                qp = st.number_input(f"SC-QAM 通道 {i} 功率 (dBmV)", value=d_p, step=0.01, format="%.2f", key=f"t3_p_{i}")
            with c_lines[1]:
                qbw = st.number_input(f"SC-QAM 通道 {i} 參考頻寬 (MHz)", value=6.40, step=0.1, format="%.2f", key=f"t3_bw_{i}")
            qam_channels.append({"power": qp, "bw": qbw})
    with col2:
        total_qam_linear = sum([db_to_linear(ch["power"]) for ch in qam_channels])
        qam_tcp = linear_to_db(total_qam_linear)
        st.markdown("#### 📊 SC-QAM 純公式加總結果")
        st.title(f"{qam_tcp:.2f} dBmV")

with tab4:
    st.markdown("## 多通道複合總功率計算 (Total Composite Power)")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        multi_num = st.slider("欲計算的總通道數量", min_value=1, max_value=16, value=2, key="t4_multi_num")
        multi_channels = []
        for i in range(multi_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                val_p = 33.00 if i == 0 else 30.25
                mp = st.number_input(f"通道 {i} 功率 (dBmV)", value=val_p, step=0.01, format="%.2f", key=f"t4_p_{i}")
            with c_lines[1]:
                mbw = st.number_input(f"通道 {i} 頻寬 (MHz)", value=96.00, step=1.0, format="%.2f", key=f"t4_bw_{i}")
            multi_channels.append({"power": mp, "bw": mbw})
    with col2:
        total_multi_linear = sum([db_to_linear(ch["power"]) for ch in multi_channels])
        multi_tcp = linear_to_db(total_multi_linear)
        st.markdown("#### 📊 Multi-Channel 複合總功率 (TCP)")
        st.title(f"{multi_tcp:.2f} dBmV")
