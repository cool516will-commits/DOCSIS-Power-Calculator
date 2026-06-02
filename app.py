import streamlit as st
import math

# 網頁頁面基礎設定
st.set_page_config(
    page_title="EdisonSu DOCSIS Power Calculator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def db_to_linear(db):
    return 10 ** (db / 10)

def linear_to_db(linear):
    if linear <= 0:
        return 0
    return 10 * math.log10(linear)

st.title("📡 EdisonSu DOCSIS Power Calculator")

tab1, tab2 = st.tabs([
    "📈 多 OFDMA 功率譜密度 (PSD) 換算",
    "📊 多通道純數值 TCP 功率計算"
])

# ==========================================
# TAB 1: 多 OFDMA 功率譜密度 (PSD) 換算 (完美對齊 image_9c429b.png)
# ==========================================
with tab1:
    st.markdown("### 多 OFDMA 區塊等效頻寬功率換算 (基於 PSD 疊加)")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        ofdma_block_num = st.slider("請選擇 OFDMA 區塊數量", min_value=1, max_value=4, value=2, key="t1_ofdma_num")
        
        st.markdown("#### 📥 各 OFDMA 區塊獨立參數輸入")
        ofdma_inputs = []
        
        for i in range(ofdma_block_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                default_p = 33.00 if i == 0 else 35.00
                p = st.number_input(f"OFDMA 區塊 {i} 總功率 (dBmV)", value=default_p, step=0.1, format="%.2f", key=f"t1_op_{i}")
            with c_lines[1]:
                default_bw = 96.00
                bw = st.number_input(f"OFDMA 區塊 {i} 總頻寬 (MHz)", value=default_bw, step=1.0, format="%.2f", key=f"t1_obw_{i}")
            ofdma_inputs.append({"power": p, "bw": bw})
                
        st.markdown("#### 🎯 目標等效換算頻寬")
        bw_target = st.number_input("你想換算成的目標頻寬 (Target Bandwidth, MHz)", value=48.00, step=0.1, format="%.2f", key=f"t1_target_bw")
        
    with col2:
        # 進行純物理 PSD 運算
        total_psd = 0.0
        
        raw_linear_sum = sum([db_to_linear(d["power"]) for d in ofdma_inputs])
        raw_tcp_dbmv = linear_to_db(raw_linear_sum)
        total_raw_bw = sum([d["bw"] for d in ofdma_inputs])
        
        for d in ofdma_inputs:
            if d["bw"] > 0:
                ch_linear_power = db_to_linear(d["power"])
                ch_psd = ch_linear_power / d["bw"]
                total_psd += ch_psd
            
        st.markdown("#### 📊 1. 原始未轉換總合參考")
        st.metric(label="原始通道線性加總總功率 (TCP)", value=f"{raw_tcp_dbmv:.2f} dBmV")
        st.write(f"原始實體通道加總總頻寬: {total_raw_bw:.2f} MHz")
        
        st.markdown("#### 🎯 2. 等效目標頻寬換算結果")
        if bw_target > 0:
            final_target_linear = total_psd * bw_target
            final_converted_p = linear_to_db(final_target_linear)
            
            st.metric(label=f"等效在 {bw_target:.2f} MHz 下的複合總功率", value=f"{final_converted_p:.2f} dBmV")
            st.success("✅ 已採用標準功率譜密度 (PSD) 疊加公式直出。")

# ==========================================
# TAB 2: 多通道純數值 TCP 功率計算 (無任何頻寬判定限制)
# ==========================================
with tab2:
    st.markdown("### 多通道複合總功率計算 (Total Composite Power)")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        ch_num = st.slider("欲計算的總通道數量", min_value=1, max_value=12, value=2, key="t2_slider")
        st.markdown("#### 📥 各通道實際數據輸入")
        ch_data = []
        
        for i in range(ch_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                if i == 0: default_p = 33.00
                elif i == 1: default_p = 30.25
                else: default_p = 30.00
                p = st.number_input(f"通道 {i} 功率 (dBmV)", value=default_p, step=0.01, format="%.2f", key=f"t2_p_{i}")
            with c_lines[1]:
                default_bw = 96.00
                bw = st.number_input(f"通道 {i} 頻寬 (MHz)", value=default_bw, step=0.1, format="%.2f", key=f"t2_bw_{i}")
            ch_data.append({"power": p, "bw": bw})
            
    with col2:
        total_linear = sum([db_to_linear(ch["power"]) for ch in ch_data])
        tcp_dbmv = linear_to_db(total_linear)
        total_bw = sum([ch["bw"] for ch in ch_data])
        
        st.markdown("#### 📊 Multi-Channel 複合總功率 (TCP)")
        st.metric(label="Total Composite Power", value=f"{tcp_dbmv:.2f} dBmV")
        st.write(f"所有通道線性加總功率: {tcp_dbmv:.2f} dBmV")
        st.write(f"目前累積總頻寬: {total_bw:.2f} MHz")
