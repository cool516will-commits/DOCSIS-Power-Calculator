import streamlit as st
import math

# 1. 網頁頁面基礎設定
st.set_page_config(
    page_title="EdisonSu DOCSIS Power Calculator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 基礎 RF 轉換函式
def db_to_linear(db):
    return 10 ** (db / 10)

def linear_to_db(linear):
    if linear <= 0:
        return 0
    return 10 * math.log10(linear)

st.title("📡 EdisonSu DOCSIS Power Calculator")

# 建立全新實用分頁
tab1, tab2, tab3 = st.tabs([
    "📈 多 OFDMA 複合與頻寬換算",
    "📊 SC-QAM + OFDMA 混合加總",
    "🧮 多通道純數值 TCP 加總"
])

# ==========================================
# TAB 1: 多 OFDMA 複合與頻寬換算 (支援多個不同 P/BW 的 OFDMA)
# ==========================================
with tab1:
    st.header("多 OFDMA 區塊複合總功率與等效換算")
    st.markdown("💡 **說明**：當你有多個不同頻寬與功率的 OFDMA 區塊時，此功能會先將其加總為總 Composite Power，再換算至目標頻寬（如 6.5MHz）。")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # 讓使用者自由決定有幾個 OFDMA 區塊
        ofdma_block_num = st.slider("請選擇 OFDMA 區塊數量", min_value=1, max_value=4, value=2, key="t1_ofdma_num")
        
        st.subheader("📥 各 OFDMA 區塊獨立參數輸入")
        ofdma_linears = []
        ofdma_bws = []
        
        for i in range(ofdma_block_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                # 給予不同的初始預設值方便對照
                default_p = 33.00 if i == 0 else 30.00
                p = st.number_input(f"OFDMA 區塊 {i} 總功率 (dBmV)", value=default_p, step=0.1, format="%.2f", key=f"t1_op_{i}")
                ofdma_linears.append(db_to_linear(p))
            with c_lines[1]:
                default_bw = 95.00 if i == 0 else 48.00
                bw = st.number_input(f"OFDMA 區塊 {i} 總頻寬 (MHz)", value=default_bw, step=1.0, format="%.2f", key=f"t1_obw_{i}")
                ofdma_bws.append(bw)
                
        st.subheader("🎯 目標等效換算頻寬")
        bw_target = st.number_input("你想換算成的目標頻寬 (Target Bandwidth, MHz)", value=6.50, step=0.1, format="%.2f", key=f"t1_target_bw")
        
    with col2:
        total_ofdma_linear = sum(ofdma_linears)
        total_ofdma_bw = sum(ofdma_bws)
        total_ofdma_dbmv = linear_to_db(total_ofdma_linear)
        
        st.subheader("📊 1. 複合總合結果 (TCP)")
        st.metric(label="OFDMA 複合總功率 (Total TCP)", value=f"{total_ofdma_dbmv:.2f} dBmV")
        st.info(f"🌐 所有 OFDMA 累積總頻寬: {total_ofdma_bw:.2f} MHz")
        
        st.subheader("🎯 2. 等效目標頻寬換算結果")
        if total_ofdma_bw > 0 and bw_target > 0:
            # 基於多區塊加總後的 TCP 與總頻寬進行 PSD 換算
            p_converted = total_ofdma_dbmv + (10 * math.log10(bw_target / total_ofdma_bw))
            st.metric(label=f"等效在 {bw_target:.2f} MHz 下的功率", value=f"{p_converted:.2f} dBmV")
            st.success(f"公式：{total_ofdma_dbmv:.2f} + 10*log10({bw_target:.2f} / {total_ofdma_bw:.2f})")
        else:
            st.error("頻寬數值必須大於 0")

# ==========================================
# TAB 2: SC-QAM + OFDMA 混合加總 (多通道進階版)
# ==========================================
with tab2:
    st.header("SC-QAM 與多個 OFDMA 總功率混合加總")
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("📥 傳統 SC-QAM 設定")
        qam_count = st.number_input("SC-QAM 通道數量", min_value=0, max_value=32, value=8, step=1, key="t2_qam_count")
        qam_p = st.number_input("單一 SC-QAM 通道功率 (dBmV)", value=30.50, step=0.1, format="%.2f", key="t2_qam_p")
        
        st.subheader("📥 OFDMA 區塊設定")
        mix_ofdma_num = st.slider("OFDMA 區塊數量", min_value=0, max_value=4, value=1, key="t2_ofdma_num")
        mix_ofdma_linears = []
        
        for i in range(mix_ofdma_num):
            p = st.number_input(f"OFDMA 區塊 {i} 功率 (dBmV)", value=33.00, step=0.1, format="%.2f", key=f"t2_op_{i}")
            mix_ofdma_linears.append(db_to_linear(p))
        
    with col2:
        total_qam_linear = db_to_linear(qam_p) * qam_count if qam_count > 0 else 0
        total_mix_ofdma_linear = sum(mix_ofdma_linears)
        
        mix_tcp = linear_to_db(total_qam_linear + total_mix_ofdma_linear)
        st.metric(label="🔋 混合總輸出功率 (TCP)", value=f"{mix_tcp:.2f} dBmV")
        st.info(f"📊 SC-QAM 總功率: {linear_to_db(total_qam_linear):.2f} dBmV")
        st.info(f"📊 OFDMA 總功率: {linear_to_db(total_mix_ofdma_linear):.2f} dBmV")

# ==========================================
# TAB 3: 多通道純數值加總 (輸入多少就線性加多少)
# ==========================================
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
        total_linear_sum = sum([db_to_linear(p) for p in ch_powers])
        tcp_dbmv = linear_to_db(total_linear_sum)
        
        st.metric(label="📊 純公式加總總功率 (TCP)", value=f"{tcp_dbmv:.2f} dBmV")
