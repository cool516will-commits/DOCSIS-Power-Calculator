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

# 建立乾淨的分頁
tab1, tab2 = st.tabs([
    "🧮 多通道 TCP 功率計算",
    "📊 SC-QAM + OFDMA 混合加總"
])

# ==========================================
# TAB 1: 多通道 TCP 功率計算 (修正噴出說明文件 bug 版)
# ==========================================
with tab1:
    st.subheader("多通道複合總功率計算 (Total Composite Power)")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # 總頻寬上限限制
        bw_limit = st.number_input("設定一次性系統總頻寬上限限制 (MHz)", value=100.0, step=10.0, format="%.1f")
        
        # 欲計算的總通道數量
        ch_num = st.slider("欲計算的總通道數量", min_value=1, max_value=12, value=2)
        
        st.write("### 📥 各通道實際數據輸入")
        ch_data = []
        
        for i in range(ch_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                default_p = 30.00 if i == 0 else 30.25
                p = st.number_input(f"通道 {i} 功率 (dBmV)", value=default_p, step=0.01, format="%.2f", key=f"t1_p_{i}")
            with c_lines[1]:
                default_bw = 6.40
                bw = st.number_input(f"通道 {i} 頻寬 (MHz)", value=default_bw, step=0.1, format="%.2f", key=f"t1_bw_{i}")
            ch_data.append({"power": p, "bw": bw})
            
    with col2:
        # 計算總線性功率與總頻寬
        total_linear = sum([db_to_linear(ch["power"]) for ch in ch_data])
        tcp_dbmv = linear_to_db(total_linear)
        total_bw = sum([ch["bw"] for ch in ch_data])
        
        st.write("### 📊 Multi-Channel 複合總功率 (TCP)")
        st.metric(label="Total Composite Power", value=f"{tcp_dbmv:.2f} dBmV")
        
        st.write(f"所有通道線性加總功率: {tcp_dbmv:.2f} dBmV")
        st.write(f"目前累積總頻寬: {total_bw:.2f} MHz / 限制上限 {bw_limit:.2f} MHz")
        
        # 頻寬超標檢查 (改用最單純的 st.success / st.error)
        if total_bw <= bw_limit:
            st.success("頻寬檢查正常：在限制範圍內。")
        else:
            st.error(f"警告：目前通道加總頻寬 ({total_bw:.2f} MHz) 已經超標！")

# ==========================================
# TAB 2: SC-QAM + OFDMA 混合加總
# ==========================================
with tab2:
    st.subheader("SC-QAM 與 OFDMA 總功率混合加總")
    col1, col2 = st.columns([1.2, 1])
    with col1:
        qam_count = st.number_input("SC-QAM 通道數量", min_value=0, max_value=32, value=8, step=1)
        qam_p = st.number_input("單一 SC-QAM 通道功率 (dBmV)", value=30.50, step=0.1, format="%.2f")
        mix_ofdma_num = st.slider("OFDMA 區塊數量", min_value=0, max_value=4, value=1)
        mix_ofdma_linears = []
        for i in range(mix_ofdma_num):
            p = st.number_input(f"OFDMA 區塊 {i} 功率 (dBmV)", value=33.00, step=0.1, format="%.2f", key=f"t2_op_{i}")
            mix_ofdma_linears.append(db_to_linear(p))
    with col2:
        total_qam_linear = db_to_linear(qam_p) * qam_count if qam_count > 0 else 0
        mix_tcp = linear_to_db(total_qam_linear + sum(mix_ofdma_linears))
        st.metric(label="混合總輸出功率 (TCP)", value=f"{mix_tcp:.2f} dBmV")
