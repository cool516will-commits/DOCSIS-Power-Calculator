這張圖是典型的 Cable Modem (CM) 終端機（如同 Broadcom 晶片組常見的 show cable modem upstream 相關指令輸出）。

從圖中我們可以看到有 8 個活躍的上行通道（txid 0 到 7），它們的 symbols/sec 都是 5,120,000 (5.12 Msps)，這代表它們全部都是標準的 SC-QAM 通道（每個通道佔用頻寬通常約為 6.4 MHz），目前圖中還沒有看到 OFDMA 通道的資訊。

不過沒關係！為了讓你的計算機具有完整的實用性，我幫你把 Tab 2 (SC-QAM + OFDMA) 和 Tab 3 (Multi Channel Sum) 的計算邏輯與介面全部補齊，並且加入讓你自行輸入頻寬限制的功能。

以下是全面升級的 app.py 完整程式碼：

Python
import streamlit as st
import math

# 設定網頁標題與主題色
st.set_page_config(
    page_title="EdisonSu DOCSIS Power Calculator Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 注入自訂 CSS，讓介面更有科技感、卡片化排版
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 6px solid #007bff;
        margin-bottom: 20px;
    }
    .result-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .result-title { font-size: 16px; opacity: 0.8; font-weight: 500; }
    .result-value { font-size: 36px; font-weight: 700; margin: 10px 0; color: #00f2fe; }
    .sub-text { font-size: 14px; opacity: 0.9; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px; margin-top: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("📡 EdisonSu DOCSIS Power Calculator (Broadcom 專業版)")
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
    "📊 OFDMA BW Converter", 
    "📈 SC-QAM + OFDMA 混合計算", 
    "🧮 Multi-Channel TCP Power"
])

# ==========================================
# TAB 1: OFDMA BW Converter
# ==========================================
with tab1:
    st.subheader("OFDMA Power Converter")
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📥 參數輸入")
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            p_meas = st.number_input("Measured Power (dBmV)", value=33.00, step=0.1, format="%.2f", key="t1_p")
            bw_meas = st.number_input("Measured Bandwidth (MHz)", value=95.00, step=1.0, format="%.2f", key="t1_bw1")
        with sub_col2:
            bw_target = st.number_input("Target Bandwidth (MHz)", value=6.50, step=0.1, format="%.2f", key="t1_bw2")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        if bw_meas > 0 and bw_target > 0:
            p_target = p_meas + linear_to_db(bw_target / bw_meas)
            st.markdown(f"""
                <div class="result-box">
                    <div class="result-title">Converted Power (dBmV)</div>
                    <div class="result-value">{p_target:.2f} <span style="font-size:20px;">dBmV</span></div>
                    <div class="sub-text">
                        📍 <b>原始條件:</b> {p_meas:.2f} dBmV @ {bw_meas:.2f} MHz<br>
                        🔄 <b>等效換算:</b> 相當於在 {bw_target:.2f} MHz 頻寬下的功率
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
    st.markdown("當晶片同時跑傳統單載波 QAM 與新式 OFDMA 時，計算整體的總輸出功率。")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📥 SC-QAM 設定")
        qam_count = st.number_input("SC-QAM 通道數量", min_value=0, max_value=8, value=8, step=1)
        qam_p = st.number_input("單一 SC-QAM 通道功率 (dBmV)", value=30.50, step=0.1, format="%.2f")
        qam_bw = st.number_input("單一 SC-QAM 佔用頻寬 (MHz)", value=6.40, step=0.1, format="%.2f")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📥 OFDMA 設定")
        ofdma_p = st.number_input("OFDMA 總量測功率 (dBmV)", value=33.00, step=0.1, format="%.2f")
        ofdma_bw = st.number_input("OFDMA 量測頻寬 (MHz)", value=95.00, step=1.0, format="%.2f")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        # 計算總功率 (需轉為線性 mw/線性功率比再相加)
        total_qam_linear = db_to_linear(qam_p) * qam_count if qam_count > 0 else 0
        total_ofdma_linear = db_to_linear(ofdma_p)
        total_tcp_linear = total_qam_linear + total_ofdma_linear
        
        total_tcp_dbmv = linear_to_db(total_tcp_linear)
        total_bw = (qam_count * qam_bw) + ofdma_bw
        
        st.markdown(f"""
            <div class="result-box" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <div class="result-title">混合總輸出功率 (Total Composite Power)</div>
                <div class="result-value">{total_tcp_dbmv:.2f} <span style="font-size:20px;">dBmV</span></div>
                <div class="sub-text">
                    📊 <b>SC-QAM 總功率:</b> {linear_to_db(total_qam_linear):.2f} dBmV ({qam_count} 載波)<br>
                    📶 <b>OFDMA 功率:</b> {ofdma_p:.2f} dBmV<br>
                    🌐 <b>估算總使用頻寬:</b> {total_bw:.2f} MHz
                </div>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 3: Multi-Channel TCP Power (靈活自訂多通道)
# ==========================================
with tab3:
    st.subheader("多通道複合總功率計算 (Total Composite Power)")
    st.markdown("依據你在 Broadcom 介面看到的數據，自行輸入各個通道的實際功率與自訂頻寬限制。")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ 系統與頻寬限制設定")
        ch_num = st.slider("欲計算的總通道數", min_value=1, max_value=12, value=8)
        
        # 讓用戶自訂頻寬限制
        bw_limit = st.number_input("自訂系統最高總頻寬限制 (MHz)", value=100.0, step=5.0, format="%.1f")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 動態產生通道輸入框
        st.markdown('### 📥 各通道數據輸入')
        ch_powers = []
        ch_bws = []
        
        # 畫面排版：用欄位讓輸入框並排，比較美觀
        for i in range(ch_num):
            c_lines = st.columns(3)
            with c_lines[0]:
                p = st.number_input(f"通道 {i} 功率 (dBmV)", value=30.0 + (i % 3)*0.25, step=0.05, format="%.2f", key=f"p_{i}")
                ch_powers.append(p)
            with c_lines[1]:
                bw = st.number_input(f"通道 {i} 頻寬 (MHz)", value=6.4, step=0.1, format="%.2f", key=f"bw_{i}")
                ch_bws.append(bw)
            with c_lines[2]:
                st.markdown("<br><p style='color:gray;font-size:12px;'>SC-QAM / OFDMA</p>", unsafe_allow_html=True)
                
    with col2:
        # 計算 TCP
        total_linear_sum = sum([db_to_linear(p) for p in ch_powers])
        tcp_dbmv = linear_to_db(total_linear_sum)
        sum_bw = sum(ch_bws)
        
        st.markdown(f"""
            <div class="result-box" style="background: linear-gradient(135deg, #6441a5 0%, #2a0845 100%);">
                <div class="result-title">Multi-Channel TCP</div>
                <div class="result-value">{tcp_dbmv:.2f} <span style="font-size:20px;">dBmV</span></div>
                <div class="sub-text">
                    📈 <b>通道加總總功率:</b> {tcp_dbmv:.2f} dBmV<br>
                    ⚠️ <b>目前加總頻寬:</b> {sum_bw:.2f} MHz / 限制 {bw_limit:.2f} MHz
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 檢查頻寬是否超標
        if sum_bw > bw_limit:
            st.error(f"🚨 警告：目前加總頻寬 ({sum_bw:.2f} MHz) 已經超過你設定的限制 ({bw_limit:.2f} MHz)！")
        else:
            st.success(f"✅ 頻寬檢查正常：未超過系統頻寬限制。")

# 頁尾
st.markdown
