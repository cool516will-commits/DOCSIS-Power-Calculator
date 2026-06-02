import streamlit as st
import math

# 1. 網頁頁面基礎設定
st.set_page_config(
    page_title="EdisonSu DOCSIS Power Calculator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 基礎 RF 轉換函式
def db_to_linear(db):
    return 10 ** (db / 10)

def linear_to_db(linear):
    if linear <= 0:
        return 0
    return 10 * math.log10(linear)

# 3. 網頁大標題
st.title("📡 EdisonSu DOCSIS Power Calculator")

# 4. 建立功能分頁
tab1, tab2 = st.tabs([
    "🧮 多通道 TCP 功率計算",
    "📈 SC-QAM + OFDMA 混合計算"
])

# ==========================================
# TAB 1: 多通道 TCP 功率計算
# ==========================================
with tab1:
    st.header("多通道複合總功率計算 (Total Composite Power)")
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        ch_num = st.slider("欲計算的總通道數量", min_value=1, max_value=12, value=8)
        
        st.subheader("📥 各通道實際數據輸入")
        ch_powers = []
        ch_bws = []
        
        # 為了讓你方便測 1.6M，把預設值改成 1.6
        for i in range(ch_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                p = st.number_input(f"通道 {i} 功率 (dBmV)", value=30.0 + (i % 3)*0.25, step=0.05, format="%.2f", key=f"p_{i}")
                ch_powers.append(p)
            with c_lines[1]:
                bw = st.number_input(f"通道 {i} 頻寬 (MHz)", value=1.6, step=0.1, format="%.2f", key=f"bw_{i}")
                ch_bws.append(bw)
                
    with col2:
        # 【核心修正】：結合頻寬權重進行線性加總 (對齊 Broadcom 補償邏輯)
        # 傳統標準通道基準為 6.4 MHz
        total_linear_sum = 0
        for p, bw in zip(ch_powers, ch_bws):
            if bw > 0:
                # 依據頻寬比例調整單通道貢獻功率
                bw_factor = 6.4 / bw
                total_linear_sum += db_to_linear(p) * bw_factor
        
        tcp_dbmv = linear_to_db(total_linear_sum)
        sum_bw = sum(ch_bws)
        
        # 純功率加總 (未考慮頻寬補償的原始 Composite 值)
        raw_composite = linear_to_db(sum([db_to_linear(p) for p in ch_powers]))
        
        st.metric(label="🔋 Total CM Legacy Output Power", value=f"{tcp_dbmv:.2f} dBmV")
        st.success(f"🎯 已自動對齊 Broadcom 終端機 legacy 輸出算法")
        st.info(f"📈 原始通道複合總功率 (Composite Power): {raw_composite:.2f} dBmV")
        st.info(f"🌐 目前通道累積總頻寬: {sum_bw:.2f} MHz")

# ==========================================
# TAB 2: SC-QAM + OFDMA 混合計算
# ==========================================
with tab2:
    st.header("SC-QAM 與 OFDMA 總功率混合計算")
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("📥 SC-QAM 設定")
        qam_count = st.number_input("SC-QAM 通道數量", min_value=0, max_value=8, value=8, step=1)
        qam_p = st.number_input("單一 SC-QAM 通道功率 (dBmV)", value=30.50, step=0.1, format="%.2f")
        qam_bw = st.number_input("單一 SC-QAM 佔用頻寬 (MHz)", value=1.60, step=0.1, format="%.2f")
        
        st.subheader("📥 OFDMA 設定")
        ofdma_p = st.number_input("OFDMA 總量測功率 (dBmV)", value=33.00, step=0.1, format="%.2f")
        ofdma_bw = st.number_input("OFDMA 量測總頻寬 (MHz)", value=95.00, step=1.0, format="%.2f")
        
    with col2:
        # TAB2 同步更新 SC-QAM 的頻寬補償邏輯
        if qam_count > 0 and qam_bw > 0:
            total_qam_linear = db_to_linear(qam_p) * (6.4 / qam_bw) * qam_count
        else:
            total_qam_linear = 0
            
        total_ofdma_linear = db_to_linear(ofdma_p)
        total_tcp_linear = total_qam_linear + total_ofdma_linear
        
        total_tcp_dbmv = linear_to_db(total_tcp_linear)
        total_bw = (qam_count * qam_bw) + ofdma_bw
        
        st.metric(label="🔋 混合總輸出功率 (TCP)", value=f"{total_tcp_dbmv:.2f} dBmV")
        st.info(f"📊 SC-QAM 總和功率: {linear_to_db(total_qam_linear):.2f} dBmV | OFDMA 總功率: {ofdma_p:.2f} dBmV")
        st.info(f"🌐 總佔用頻寬: {total_bw:.2f} MHz")
