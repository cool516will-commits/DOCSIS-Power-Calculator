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

# 嚴格區分三頁不同功能的分頁
tab1, tab2, tab3 = st.tabs([
    "📈 第一頁：OFDMA 公式計算 (PSD 換算)",
    "📟 第二頁：SC-QAM 公式計算 (多通道)",
    "📊 第三頁：Multi 通道純數值總和 (TCP)"
])

# ==========================================
# 📈 第一頁：OFDMA 公式計算 (PSD 換算)
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
        total_psd = 0.0
        raw_linear_sum = sum([db_to_linear(d["power"]) for d in ofdma_inputs])
        raw_tcp_dbmv = linear_to_db(raw_linear_sum)
        total_raw_bw = sum([d["bw"] for d in ofdma_inputs])
        
        for d in ofdma_inputs:
            if d["bw"] > 0:
                total_psd += (db_to_linear(d["power"]) / d["bw"])
            
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
# 📟 第二頁：SC-QAM 公式計算 (多通道)
# ==========================================
with tab2:
    st.markdown("### SC-QAM 多通道功率純線性相加計算")
    st.markdown("💡 **說明**：專為單純 SC-QAM 多通道量測設計，將各通道 dBmV 功率直接轉為 mW 後進行純線性疊加。")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        qam_num = st.slider("請選擇 SC-QAM 通道數量", min_value=1, max_value=16, value=8, key="t2_qam_num")
        
        st.markdown("#### 📥 各 SC-QAM 通道獨立參數輸入")
        qam_data = []
        
        for i in range(qam_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                # 預設載入對齊測試的 8 通道經典數據
                if i == 0: default_qp = 29.25
                elif i == 1: default_qp = 32.00
                elif i == 2: default_qp = 32.25
                elif i in [3, 4]: default_qp = 29.75
                elif i in [5, 6]: default_qp = 30.25
                elif i == 7: default_qp = 30.75
                else: default_qp = 30.00
                qp = st.number_input(f"SC-QAM 通道 {i} 功率 (dBmV)", value=default_qp, step=0.01, format="%.2f", key=f"t2_p_{i}")
            with c_lines[1]:
                default_qbw = 1.60
                qbw = st.number_input(f"SC-QAM 通道 {i} 參考頻寬 (MHz)", value=default_qbw, step=0.1, format="%.2f", key=f"t2_bw_{i}")
            qam_data.append({"power": qp, "bw": qbw})
            
    with col2:
        # 純數值線性相加公式
        total_qam_linear = sum([db_to_linear(ch["power"]) for ch in qam_data])
        qam_tcp_dbmv = linear_to_db(total_qam_linear)
        total_qam_bw = sum([ch["bw"] for ch in qam_data])
        
        st.markdown("#### 📊 SC-QAM 複合總功率結果")
        st.metric(label="Total SC-QAM Composite Power", value=f"{qam_tcp_dbmv:.2f} dBmV")
        st.write(f"所有 SC-QAM 通道線性相加功率: {qam_tcp_dbmv:.2f} dBmV")
        st.write(f"累積總頻寬: {total_qam_bw:.2f} MHz")
        st.success("✅ 採純功率線性加總公式，算出來多少就是多少。")


# ==========================================
# 📊 第三頁：Multi 通道純數值總和 (TCP)
# ==========================================
with tab3:
    st.markdown("### Multi 通道純數值複合總功率加總 (無任何頻寬限制限制)")
    st.markdown("💡 **說明**：此頁面不執行任何比例換算與警告，不管是 QAM、OFDMA 還是混合訊號，有幾路加幾路，算最純粹的總合 TCP。")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        multi_num = st.slider("欲加總的總通道/訊號數量", min_value=1, max_value=16, value=2, key="t3_slider")
        st.markdown("#### 📥 各路輸入數據")
        multi_data = []
        
        for i in range(multi_num):
            c_lines = st.columns(2)
            with c_lines[0]:
                default_mp = 41.00 if i == 0 else 42.00
                mp = st.number_input(f"訊號源 {i} 功率 (dBmV)", value=default_mp, step=0.01, format="%.2f", key=f"t3_p_{i}")
            with c_lines[1]:
                default_mbw = 96.00
                mbw = st.number_input(f"訊號源 {i} 頻寬 (MHz)", value=default_mbw, step=0.1, format="%.2f", key=f"t3_bw_{i}")
            multi_data.append({"power": mp, "bw": mbw})
            
    with col2:
        total_multi_linear = sum([db_to_linear(ch["power"]) for ch in multi_data])
        multi_tcp_dbmv = linear_to_db(total_multi_linear)
        total_multi_bw = sum([ch["bw"] for ch in multi_data])
        
        st.markdown("#### 📊 Multi-Channel 複合總功率 (TCP)")
        st.metric(label="Total Composite Power", value=f"{multi_tcp_dbmv:.2f} dBmV")
        st.write(f"所有輸入線性加總功率: {multi_tcp_dbmv:.2f} dBmV")
        st.write(f"累積參考總頻寬: {total_multi_bw:.2f} MHz")
        st.success("✅ 混合/通用多通道純公式加總直出。")
