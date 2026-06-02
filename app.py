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
    return 10 * math.log10(linear) if linear > 0 else 0.0

st.title("📡 EdisonSu DOCSIS Power Calculator")

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 1. OFDMA 頻寬等效換算",
    "📈 2. 多 OFDMA 區塊 PSD 疊加",
    "📟 3. SC-QAM 多通道計算 (含個別 BW)",
    "📊 4. 多通道複合總功率 TCP 計算"
])

# 1. OFDMA 頻寬等效換算
with tab1:
    st.markdown("## OFDMA Power & Bandwidth Converter")
    col1, col2 = st.columns(2)
    with col1:
        p_meas = st.number_input("量測總功率 (dBmV)", value=33.00, step=0.1, key="t1_p")
        bw_meas = st.number_input("量測頻寬 (MHz)", value=95.00, step=1.0, key="t1_bw_m")
        bw_target = st.number_input("目標頻寬 (MHz)", value=6.50, step=0.1, key="t1_bw_t")
    with col2:
        if bw_meas > 0 and bw_target > 0:
            res = p_meas + 10 * math.log10(bw_target / bw_meas)
            st.title(f"{res:.2f} dBmV")

# 2. 多 OFDMA 區塊 PSD 疊加
with tab2:
    st.markdown("## 多 OFDMA 區塊等效頻寬功率換算")
    num = st.slider("OFDMA 區塊數量", 1, 4, 2, key="t2_num")
    blocks = []
    for i in range(num):
        c = st.columns(2)
        p = c[0].number_input(f"區塊 {i} 功率 (dBmV)", value=41.00, key=f"t2_p_{i}")
        bw = c[1].number_input(f"區塊 {i} 頻寬 (MHz)", value=96.00, key=f"t2_bw_{i}")
        blocks.append({"p": p, "bw": bw})
    target_bw = st.number_input("目標頻寬 (MHz)", value=96.00, key="t2_target")
    
    psd_sum = sum([db_to_linear(b["p"]) / b["bw"] for b in blocks if b["bw"] > 0])
    if target_bw > 0:
        res = linear_to_db(psd_sum * target_bw)
        st.metric("複合總功率", f"{res:.2f} dBmV")

# 3. SC-QAM 多通道計算 (對齊 Excel 邏輯，開放個別設定 BW)
with tab3:
    st.markdown("## SC-QAM 多通道計算 (個別 BW 設定)")
    num = st.slider("SC-QAM 通道數量", 1, 16, 8, key="t3_num")
    
    chans = []
    for i in range(num):
        c = st.columns(2)
        with c[0]:
            p = st.number_input(f"通道 {i} 功率 (dBmV)", value=30.00, key=f"t3_p_{i}")
        with c[1]:
            bw = st.number_input(f"通道 {i} 頻寬 (MHz)", value=1.60, step=0.1, key=f"t3_bw_{i}")
        chans.append({"p": p, "bw": bw})
    
    # 根據 Excel 邏輯：線性 PSD = 10^((P - 10*log10(BW))/10)
    linear_psd_list = [10 ** ((ch["p"] - 10 * math.log10(ch["bw"])) / 10) for ch in chans if ch["bw"] > 0]
    
    if len(linear_psd_list) > 0:
        avg_psd_linear = sum(linear_psd_list) / len(linear_psd_list)
        total_bw = sum([ch["bw"] for ch in chans])
        
        if total_bw > 0:
            res = 10 * math.log10(avg_psd_linear * total_bw)
            st.title(f"{res:.2f} dBmV")
            st.write(f"---")
            st.write(f"平均線性 PSD: {avg_psd_linear:.2f}")
            st.write(f"總頻寬: {total_bw:.2f} MHz")

# 4. 多通道複合總功率 TCP 計算
with tab4:
    st.markdown("## 多通道複合總功率計算 (TCP)")
    num = st.slider("總通道數量", 1, 16, 2, key="t4_num")
    chans = []
    for i in range(num):
        c = st.columns(2)
        p = c[0].number_input(f"通道 {i} 功率 (dBmV)", value=30.00, key=f"t4_p_{i}")
        chans.append(p)
        
    linear_sum = sum([db_to_linear(p) for p in chans])
    res = linear_to_db(linear_sum)
    st.title(f"{res:.2f} dBmV")
