import streamlit as st
import math

st.set_page_config(
    page_title="EdisonSu DOCSIS Power Calculator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📡 EdisonSu DOCSIS Power Calculator (Excel 邏輯版)")

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 1. OFDMA 頻寬等效換算",
    "📈 2. 多 OFDMA 區塊 PSD 疊加",
    "📟 3. SC-QAM 多通道計算 (個別 BW)",
    "📊 4. 多通道複合總功率 TCP 計算"
])

# 共用邏輯函式
def calc_total_pwr(channels):
    # channels 需為列表，每個元素為 {"p": power, "bw": bw}
    if not channels: return 0.0
    # 步驟 1 & 2: 計算 PSD 線性值
    linear_psds = [10 ** ((ch["p"] - 10 * math.log10(ch["bw"])) / 10) for ch in channels if ch["bw"] > 0]
    # 步驟 3: 平均 PSD
    avg_psd = sum(linear_psds) / len(linear_psds)
    # 步驟 4: 總頻寬
    total_bw = sum([ch["bw"] for ch in channels])
    # 總功率
    return 10 * math.log10(avg_psd * total_bw) if (avg_psd * total_bw) > 0 else 0.0

# 1. OFDMA
with tab1:
    st.markdown("## OFDMA Power & Bandwidth Converter")
    p = st.number_input("量測總功率 (dBmV)", value=33.00, key="t1_p")
    bw_meas = st.number_input("量測頻寬 (MHz)", value=95.00, key="t1_bw_m")
    bw_target = st.number_input("目標頻寬 (MHz)", value=6.50, key="t1_bw_t")
    if bw_meas > 0:
        res = p + 10 * math.log10(bw_target / bw_meas)
        st.title(f"{res:.2f} dBmV")

# 2. 多 OFDMA 區塊
with tab2:
    st.markdown("## 多 OFDMA 區塊 PSD 疊加")
    num = st.slider("數量", 1, 4, 2, key="t2_num")
    blocks = []
    for i in range(num):
        c = st.columns(2)
        p = c[0].number_input(f"區塊 {i} 功率", value=41.00, key=f"t2_p_{i}")
        bw = c[1].number_input(f"區塊 {i} 頻寬", value=96.00, key=f"t2_bw_{i}")
        blocks.append({"p": p, "bw": bw})
    target_bw = st.number_input("目標頻寬", value=96.00, key="t2_target")
    # 使用 PSD 加權法
    psd_linear = sum([10**((b["p"] - 10*math.log10(b["bw"]))/10) for b in blocks]) / len(blocks)
    res = 10 * math.log10(psd_linear * target_bw)
    st.metric("複合總功率", f"{res:.2f} dBmV")

# 3. SC-QAM (對齊 Excel)
with tab3:
    st.markdown("## SC-QAM 多通道計算 (對齊 Excel)")
    num = st.slider("通道數量", 1, 16, 8, key="t3_num")
    chans = []
    for i in range(num):
        c = st.columns(2)
        p = c[0].number_input(f"通道 {i} 功率", value=30.00, key=f"t3_p_{i}")
        bw = c[1].number_input(f"通道 {i} 頻寬", value=1.60, key=f"t3_bw_{i}")
        chans.append({"p": p, "bw": bw})
    res = calc_total_pwr(chans)
    st.title(f"{res:.2f} dBmV")

# 4. 多通道 TCP 計算
with tab4:
    st.markdown("## 多通道複合總功率計算")
    num = st.slider("數量", 1, 16, 2, key="t4_num")
    chans = []
    for i in range(num):
        c = st.columns(2)
        p = c[0].number_input(f"通道 {i} 功率", value=30.00, key=f"t4_p_{i}")
        bw = c[1].number_input(f"通道 {i} 頻寬", value=6.40, key=f"t4_bw_{i}")
        chans.append({"p": p, "bw": bw})
    res = calc_total_pwr(chans)
    st.title(f"{res:.2f} dBmV")
