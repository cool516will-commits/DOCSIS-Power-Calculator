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

# 建立原本對應的三個 Tab 分頁
tab1, tab2, tab3 = st.tabs([
    "📈 OFDMA BW Converter",
    "📊 SC-QAM + OFDMA 混合計算",
    "🧮 Multi Channel Sum"
])

# ==========================================
# TAB 1: OFDMA 功率與頻寬換算 (修正後的鋼鐵公式)
# ==========================================
with tab1:
    st.header("OFDMA Power & Bandwidth Converter")
    st.markdown("💡 **說明**：當你量到一段大頻寬的 OFDMA 總功率時，可以用此功能換算成目標小頻寬（如 6.5MHz）下的等效功率。")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        p_measured = st.number_input("1. 輸入量測到的總功率 (Measured Power, dBmV)", value=33.00, step=0.1, format="%.2f")
        bw_measured = st.number_input("2. 量測訊號的總頻寬 (Measured Bandwidth, MHz)", value=95.00, step=1.0, format="%.2f")
        bw_target = st.number_input("3. 你想換算成的目標頻寬 (Target Bandwidth, MHz)", value=6.50, step=0.1, format="%.2f")
        
    with col2:
        if bw_measured > 0 and bw_target > 0:
            # 正確的 PSD 頻寬轉換公式
            p_converted = p_measured + (10 * math.log10(bw_target / bw_measured))
            
            st.metric(label="等效換算後的功率 (Converted Power)", value=f"{p_converted:.2f} dBmV")
            
            # 顯示清楚的文字對照區塊
            st.info(f"📋 原始條件: {p_measured:.2f} dBmV @ {bw_measured:.2f} MHz")
            st.success(f"🎯 等效換算: 相當於在 {bw_target:.2f} MHz 頻寬下分配到 {p_converted:.2f} dBmV 的功率。")
        else:
            st.error("頻寬數值必須大於 0")

# ==========================================
# TAB 2: SC-QAM + OFDMA 混合計算
# ==========================================
with tab2:
    st.header("SC-QAM 與 OFDMA 總功率混合計算")
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        qam_count = st.number_input("SC-QAM 通道數量", min_value=0, max_value=32, value=8, step=1)
        qam_p = st.number_input("單一 SC-QAM 通道功率 (dBmV)", value=30.50, step=0.1, format="%.2f")
        ofdma_p = st.number_input("OFDMA 總量測功率 (dBmV)", value=33.00, step=0.1, format="%.2f")
        
    with col2:
        total_qam_linear = db_to_linear(qam_p) * qam_count if qam_count > 0 else 0
        total_ofdma_linear = db_to_linear(ofdma_p)
        
        mix_tcp = linear_to_db(total_qam_linear + total_ofdma_linear)
        st.metric(label="🔋 混合總輸出功率 (TCP)", value=f"{mix_tcp:.2f} dBmV")

# ==========================================
# TAB 3: 多通道純數值加總 (輸入多少就線性加多少)
# ==========================================
with tab3:
    st.header("多通道純數值複合總功率計算")
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        ch_num = st.slider("欲計算的總通道數量", min_value=1, max_value=32, value=8, key="tab3_slider")
        ch_powers = []
        for i in range(ch_num):
            p = st.number_input(f"通道 {i} 功率 (dBmV)", value=30.00, step=0.01, format="%.2f", key=f"t3_p_{i}")
            ch_powers.append(p)
            
    with col2:
        total_linear_sum = sum([db_to_linear(p) for p in ch_powers])
        tcp_dbmv = linear_to_db(total_linear_sum)
        
        st.metric(label="📊 純公式加總總功率 (TCP)", value=f"{tcp_dbmv:.2f} dBmV")
