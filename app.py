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
    "🧮 多通道 TCP 功率計算 (純數值純公式版)",
    "📈 SC-QAM + OFDMA 混合計算"
])

# ==========================================
# TAB 1: 多通道 TCP 功率計算 (輸入多少就直接算多少)
# ==========================================
with tab1:
    st.header("多通道複合總功率計算 (Total Composite Power)")
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        ch_num = st.slider("欲計算的總通道數量", min_value=1, max_value=12, value=2)
        
        st.subheader("📥 各通道實際數據輸入")
        ch_powers = []
        ch_bws = []
        
        for i in range(ch_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                p = st.number_input(f"通道 {i} 功率 (dBmV)", value=45.0, step=0.5, format="%.2f", key=f"p_{i}")
                ch_powers.append(p)
            with c_lines[1]:
                bw = st.number_input(f"通道 {i} 頻寬 (MHz)", value=96.0, step=1.0, format="%.2f", key=f"bw_{i}")
                ch_bws.append(bw)
                
    with col2:
        # 完全沒有任何 bw_factor 的純數值線性相加公式
        total_linear_sum = sum([db_to_linear(p) for p in ch_powers])
        tcp_dbmv = linear_to_db(total_linear_sum)
        sum_bw = sum(ch_bws)
        
        st.metric(label="🔋 複合總輸出功率 (Total Composite Power)", value=f"{tcp_dbmv:.2f} dBmV")
        st.success(f"📊 採純功率線性加總公式，算出來多少就是多少")
        st.info(f"🌐 目前通道累積總頻寬: {sum_bw:.2f} MHz")

# ==========================================
# TAB 2: SC-QAM + OFDMA 混合計算 (同步改為純數值加總)
# ==========================================
with tab2:
    st.header("SC-QAM 與 OFDMA 總功率混合計算")
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("📥 傳統 SC-QAM 設定")
        qam_count = st.number_input("SC-QAM 通道數量", min_value=0, max_value=8, value=8, step=1)
        qam_p = st.number_input("單一 SC-QAM 通道功率 (dBmV)", value=30.50, step=0.1, format="%.2f")
        qam_bw = st.number_input("單一 SC-QAM 佔用頻寬 (MHz)", value=1.60, step=0.1, format="%.2f")
        
        st.subheader("📥 新式 OFDMA 設定")
        ofdma_p = st.number_input("OFDMA 總量測功率 (dBmV)", value=33.00, step=0.1, format="%.2f")
        ofdma_bw = st.number_input("OFDMA 量測總頻寬 (MHz)", value=95.00, step=1.0, format="%.2f")
        
    with col2:
        # 同步拔除所有頻寬權重，純粹看通道數量與輸入數值
        total_qam_linear = db_to_linear(qam_p) * qam_count if qam_count > 0 else 0
        total_ofdma_linear = db_to_linear(ofdma_p)
        total_tcp_linear = total_qam_linear + total_ofdma_linear
        
        total_tcp_dbmv = linear_to_db(total_tcp_linear)
        total_bw = (qam_count * qam_bw) + ofdma_bw
        
        st.metric(label="🔋 混合總輸出功率 (TCP)", value=f"{total_tcp_dbmv:.2f} dBmV")
        st.info(f"📊 SC-QAM 總和功率: {linear_to_db(total_qam_linear):.2f} dBmV | OFDMA 總功率: {ofdma_p:.2f} dBmV")
        st.info(f"🌐 總佔用頻寬: {total_bw:.2f} MHz")
