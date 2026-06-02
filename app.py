import streamlit as st
import math

# 設定網頁標題與主題色
st.set_page_config(
    page_title="EdisonSu DOCSIS Power Calculator",
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
    .result-value { font-size: 42px; font-weight: 700; margin: 10px 0; color: #00f2fe; }
    .sub-text { font-size: 14px; opacity: 0.9; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px; margin-top: 10px;}
    </style>
""", unsafe_allow_html=True)

# 頂部精美 Banner
st.title("📡 EdisonSu DOCSIS Power Calculator")
st.markdown("---")

# 基礎轉換函式
def db_to_linear(db):
    return 10 ** (db / 10)

def linear_to_db(linear):
    if linear <= 0:
        return 0
    return 10 * math.log10(linear)

# 建立分頁
tab1, tab2, tab3 = st.tabs([
    "📊 OFDMA BW Converter", 
    "📈 SC-QAM + OFDMA", 
    "🧮 Multi Channel Sum"
])

# ==========================================
# TAB 1: OFDMA BW Converter
# ==========================================
with tab1:
    st.subheader("OFDMA Power Converter")
    
    # 左右並排版型（左邊輸入、右邊漂亮輸出）
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📥 參數輸入")
        
        # 使用欄位再細分，讓輸入框不要那麼寬
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            p_meas = st.number_input("Measured Power (dBmV)", value=33.00, step=0.1, format="%.2f")
            bw_meas = st.number_input("Measured Bandwidth (MHz)", value=95.00, step=1.0, format="%.2f")
        with sub_col2:
            bw_target = st.number_input("Target Bandwidth (MHz)", value=6.50, step=0.1, format="%.2f")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        # 計算核心邏輯
        if bw_meas > 0 and bw_target > 0:
            # 頻寬功率換算公式
            p_target = p_meas + linear_to_db(bw_target / bw_meas)
            
            # 美化輸出卡片
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
# TAB 2 & 3 預留空間 (你可以依此類推修改)
# ==========================================
with tab2:
    st.info("SC-QAM + OFDMA 混合計算模組開發中...")

with tab3:
    st.info
