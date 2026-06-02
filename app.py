import streamlit as st
import math

# 設定網頁標題與主題色
st.set_page_config(
    page_title="EdisonSu DOCSIS Power Calculator Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 注入自訂 CSS，美化卡片和漸層外觀
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .custom-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-top: 4px solid #007bff;
        margin-bottom: 15px;
    }
    .result-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .result-box-tab2 {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .result-box-tab3 {
        background: linear-gradient(135deg, #6441a5 0%, #2a0845 100%);
        color: white;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .result-title { font-size: 15px; opacity: 0.8; font-weight: 500; }
    .result-value { font-size: 38px; font-weight: 700; margin: 5px 0; color: #00f2fe; }
    .sub-text { font-size: 13px; opacity: 0.9; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 8px; margin-top: 8px;}
    </style>
""", unsafe_allow_html=True)

st.title("📡 EdisonSu DOCSIS Power Calculator")
st.markdown("---")

# ==========================================
# 基礎 RF 轉換函式
# ==========================================
def db_to_linear(db):
    return 10 ** (db / 10)

def linear_to_db(linear):
    if linear <= 0:
        return 0
    return 10 * math.log10(linear)

# 建立分頁
tab1, tab2, tab3 = st.tabs([
    "📊 OFDMA 頻寬等效換算 (Bandwidth Converter)", 
    "📈 SC-QAM + OFDMA 總功率混合計算", 
    "🧮 多通道 TCP 功率計算 (Broadcom 數據對照)"
])

# ==========================================
# TAB 1: OFDMA BW Converter
# ==========================================
with tab1:
    st.subheader("OFDMA 功率與頻寬換算")
    st.info("💡 說明：當你量到一整段很大的 OFDMA 總功率時，可以用這個功能換算成單一載波（如 6.5MHz）的等效功率。")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        p_meas = st.number_input("1. 輸入量測到的總功率 (Measured Power, dBmV)", value=33.00, step=0.1, format="%.2f", key="t1_p")
        bw_meas = st.number_input("2. 畫面上這段 OFDMA 的總頻寬 (MHz)", value=95.00, step=1.0, format="%.2f", key="t1_bw1")
        bw_target = st.number_input("3. 你想換算成多寬的頻寬來檢視 (Target BW, MHz)", value=6.50, step=0.1, format="%.2f", key="t1_bw2")
        
    with col2:
        if bw_meas > 0 and bw_target > 0:
            p_target = p_meas + linear_to_db(bw_target / bw_meas)
            st.markdown(f"""
                <div class="result-box">
                    <div class="result-title">等效換算後的功率 (Converted Power)</div>
                    <div class="result-value">{p_target:.2f} <span style="font-size:18px;">dBmV</span></div>
                    <div class="sub-text">
                        📍 <b>原始輸入:</b> {p_meas:.2f} dBmV @ {bw_meas:.2f} MHz<br>
                        🔄 <b>換算結果:</b> 相當於在 {bw_target:.2f} MHz 頻寬下所分配到的功率
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("頻寬數值必須大於 0")

# ==========================================
# TAB 2: SC-QAM + OFDMA 混合計算
# ==========================================
with tab2:
    st.subheader("SC-QAM 與 OFDMA 總功率混合計算")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("##### 📥 傳統 SC-QAM 設定")
        qam_count = st.number_input("SC-QAM 通道數量 (例如圖中的 8 個)", min_value=0, max_value=8, value=8, step=1)
        qam_p = st.number_input("單一 SC-QAM 通道功率 (dBmV)", value=30.50, step=0.1, format="%.2f")
        qam_bw = st.number_input("單一 SC-QAM 佔用頻寬 (MHz)", value=6.40, step=0.1, format="%.2f")
        
        st.markdown("---")
        st.markdown("##### 📥 新式 OFDMA 設定")
        ofdma_p = st.number_input("OFDMA 總量測功率 (dBmV)", value=33.00, step=0.1, format="%.2f")
        ofdma_bw = st.number_input("OFDMA 量測總頻寬 (MHz)", value=95.00, step=1.0, format="%.2f")
        
    with col2:
        total_qam_linear = db_to_linear(qam_p) * qam_count if qam_count > 0 else 0
        total_ofdma_linear = db_to_linear(ofdma_p)
        total_tcp_linear = total_qam_linear + total_ofdma_linear
        
        total_tcp_dbmv = linear_to_db(total_tcp_linear)
        total_bw = (qam_count * qam_bw) + ofdma_bw
        
        st.markdown(f"""
            <div class="result-box_tab2" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color:white; padding:25px; border-radius:8px;">
                <div class="result-title">混合總輸出功率 (Total Composite Power)</div>
                <div class="result-value">{total_tcp_dbmv:.2f} <span style="font-size:18px;">dBmV</span></div>
                <div class="sub-text">
                    📊 <b>SC-QAM 總和功率:</b> {linear_to_db(total_qam_linear):.2f} dBmV ({qam_count} 載波)<br>
                    📶 <b>OFDMA 總功率:</b> {ofdma_p:.2f} dBmV<br>
                    🌐 <b>總佔用頻寬:</b> {total_bw:.2f} MHz
                </div>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 3: Multi-Channel TCP Power
# ==========================================
with tab3:
    st.subheader("多通道複合總功率計算 (Total Composite Power)")
    st.markdown("對照你的 Broadcom 終端機數據，手動輸入各通道功率，直接加總出 TCP。")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        ch_num = st.slider("欲計算的總通道數量", min_value=1, max_value=12, value=8)
        bw_limit = st.number_input("自訂系統最高總頻寬限制上限 (MHz)", value=100.0, step=5.0, format="%.1f")
        
        st.markdown("##### 📥 各通道實際數據輸入")
        ch_powers = []
        ch_bws = []
        
        for i in range(ch_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                p = st.number_input(f"通道 {i} 功率 (dBmV)", value=30.0 + (i % 3)*0.25, step=0.05, format="%.2f", key=f"p_{i}")
                ch_powers.append(p)
            with c_lines[1]:
                bw = st.number_input(f"通道 {i} 頻寬 (MHz)", value=6.4, step=0.1, format="%.2f", key=f"bw_{i}")
                ch_bws.append(bw)
                
    with col2:
        total_linear_sum = sum([db_to_linear(p) for p in ch_powers])
        tcp_dbmv = linear_to_db(total_linear_sum)
        sum_bw = sum(ch_bws)
        
        st.markdown(f"""
            <div class="result-box-tab3">
                <div class="result-title">Multi-Channel 複合總功率 (TCP)</div>
                <div class="result-value">{tcp_dbmv:.2f} <span style="font-size:18px;">dBmV</span></div>
                <div class="sub-text">
                    📈 <b>所有通道線性加總功率:</b> {tcp_dbmv:.2f} dBmV<br>
                    ⚠️ <b>目前累積頻寬:</b> {sum_bw:.2f} MHz / 限制上限 {bw_limit:.2f} MHz
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if sum_bw > bw_limit:
            st.error(f"🚨 警告：目前通道加總頻寬 ({sum_bw:.2f} MHz) 已經超標！")
        else:
            st.success(f"✅ 頻寬檢查正常：在限制範圍內。")

st.markdown
