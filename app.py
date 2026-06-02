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

tab1, tab2, tab3 = st.tabs([
    "📈 多 OFDMA 功率譜密度 (PSD) 換算",
    "📊 SC-QAM + OFDMA 混合加總",
    "🧮 多通道純數值 TCP 加總"
])

# ==========================================
# TAB 1: 多 OFDMA 功率譜密度 (PSD) 換算
# ==========================================
with tab1:
    st.header("多 OFDMA 區塊等效頻寬功率換算")
    st.markdown
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        ofdma_block_num = st.slider("請選擇 OFDMA 區塊數量", min_value=1, max_value=4, value=2, key="t1_ofdma_num")
        
        st.subheader("📥 各 OFDMA 區塊獨立參數輸入")
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
                
        st.subheader("🎯 目標等效換算頻寬")
        bw_target = st.number_input("你想換算成的目標頻寬 (Target Bandwidth, MHz)", value=92.00, step=0.1, format="%.2f", key=f"t1_target_bw")
        
    with col2:
        # 進行純物理 PSD 運算
        total_psd = 0.0
        valid = True
        
        # 算一個原始的未轉換總複合功率 (TCP) 作為對照
        raw_linear_sum = sum([db_to_linear(d["power"]) for d in ofdma_inputs])
        raw_tcp_dbmv = linear_to_db(raw_linear_sum)
        total_raw_bw = sum([d["bw"] for d in ofdma_inputs])
        
        for d in ofdma_inputs:
            if d["bw"] <= 0:
                valid = False
                break
            # 計算單一通道的 PSD (mW / MHz)
            ch_linear_power = db_to_linear(d["power"])
            ch_psd = ch_linear_power / d["bw"]
            total_psd += ch_psd
            
        st.subheader("📊 1. 原始未轉換總合參考")
        st.metric(label="原始通道線性加總總功率 (TCP)", value=f"{raw_tcp_dbmv:.2f} dBmV")
        st.info(f"🌐 原始實體通道加總總頻寬: {total_raw_bw:.2f} MHz")
        
        st.subheader("🎯 2. 等效目標頻寬換算結果")
        if valid and bw_target > 0:
            # 總 PSD 乘上目標頻寬得到目標頻寬下的總線性功率
            final_target_linear = total_psd * bw_target
            final_converted_p = linear_to_db(final_target_linear)
            
            st.metric(label=f"等效在 {bw_target:.2f} MHz 下的複合總功率", value=f"{final_converted_p:.2f} dBmV")
            st.success("✅ 已採用標準功率譜密度 (PSD) 疊加公式，算值出來多少就是多少。")
        else:
            st.error("所有頻寬輸入數值必須大於 0")

# ==========================================
# TAB 2 & TAB 3 保持純淨計算
# ==========================================
with tab2:
    st.header("SC-QAM 與多個 OFDMA 總功率混合加總")
    col1, col2 = st.columns([1.2, 1])
    with col1:
        qam_count = st.number_input("SC-QAM 通道數量", min_value=0, max_value=32, value=8, step=1, key="t2_qam_count")
        qam_p = st.number_input("單一 SC-QAM 通道功率 (dBmV)", value=30.50, step=0.1, format="%.2f", key="t2_qam_p")
        mix_ofdma_num = st.slider("OFDMA 區塊數量", min_value=0, max_value=4, value=1, key="t2_ofdma_num")
        mix_ofdma_linears = []
        for i in range(mix_ofdma_num):
            p = st.number_input(f"OFDMA 區塊 {i} 功率 (dBmV)", value=33.00, step=0.1, format="%.2f", key=f"t2_op_{i}")
            mix_ofdma_linears.append(db_to_linear(p))
    with col2:
        total_qam_linear = db_to_linear(qam_p) * qam_count if qam_count > 0 else 0
        mix_tcp = linear_to_db(total_qam_linear + sum(mix_ofdma_linears))
        st.metric(label="🔋 混合總輸出功率 (TCP)", value=f"{mix_tcp:.2f} dBmV")

with tab3:
    st.header("多通道純數值複合總功率計算")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        ch_num = st.slider("欲計算的總通道數量", min_value=1, max_value=32, value=8, key="t3_slider")
        ch_powers = []
        for i in range(ch_num):
            p = st.number_input(f"通道 {i} 功率 (dBmV)", value=30.00, step=0.01, format="%.2f", key=f"t3_p_{i}")
            ch_powers.append(p)
    with col2:
        tcp_dbmv = linear_to_db(sum([db_to_linear(p) for p in ch_powers]))
        st.metric(label="📊 純公式加總總功率 (TCP)", value=f"{tcp_dbmv:.2f} dBmV")
