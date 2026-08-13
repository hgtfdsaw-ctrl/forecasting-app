import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. การตั้งค่าหน้าจอและ CSS ตกแต่งสไตล์ Modern Dashboard ---
st.set_page_config(page_title="ระบบพยากรณ์ยอดใช้ Holt-Winters", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 10px 10px 0 0;
        border: 1px solid #e2e8f0;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-color: #1e293b !important;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #2563eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-title { font-size: 13px; color: #64748b; font-weight: 600; }
    .metric-value { font-size: 26px; color: #0f172a; font-weight: 700; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 ระบบพยากรณ์ยอดใช้วัสดุ (Holt-Winters Forecasting)")
st.caption("คำนวณวิเคราะห์ตามโมเดล Holt-Winters Multiplicative Seasonal Smoothing (ฤดูกาล 12 เดือน)")

# --- 2. ข้อมูลย้อนหลัง 36 เดือน (2566 - 2568) ---
months_base = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
years_base = ["66", "67", "68"]
base_labels = [f"{m} {y}" for y in years_base for m in months_base]

products_data = {
    "carwash": {
        "name": "🚗 น้ำยาล้างรถ",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "history": [20,25,40,50,45,40,20,15,5,10,10,25, 25,30,50,65,55,50,25,15,8,12,15,30, 35,40,60,80,70,65,30,20,10,15,15,40]
    },
    "interior": {
        "name": "✨ น้ำยาเคลือบภายใน",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "history": [14.88,13.44,18.60,19.80,18.60,16.20,3.72,1.86,0.90,2.76,12.60,16.74, 18.60,16.80,22.32,23.40,22.32,19.80,5.58,2.76,1.32,3.72,16.20,20.46, 22.32,20.16,26.04,27.00,26.04,23.40,7.44,3.72,1.80,5.58,19.80,24.18]
    },
    "glass": {
        "name": "🪟 น้ำยาเช็ดกระจก",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "history": [9.92,8.96,12.40,13.20,12.40,10.80,2.48,1.24,0.60,1.84,8.40,11.16, 12.40,11.20,14.88,15.60,14.88,13.20,3.72,1.84,0.88,2.48,10.80,13.64, 14.88,13.44,17.36,18.00,17.36,15.60,4.96,2.48,1.20,3.72,13.20,16.12]
    },
    "wheel": {
        "name": "🛞 น้ำยาลงล้อ",
        "alpha": 0.9, "beta": 0.99, "gamma": 0.99,
        "history": [4.96,4.48,6.20,6.60,6.20,5.40,1.24,0.62,0.30,0.92,4.20,5.58, 6.20,5.60,7.44,7.80,7.44,6.60,1.86,0.92,0.44,1.24,5.40,6.82, 7.44,6.72,8.68,9.00,8.68,7.80,2.48,1.24,0.60,1.86,6.60,8.06]
    }
}

# --- 3. ฟังก์ชันคำนวณ Holt-Winters Multiplicative ---
def run_holt_winters(y, alpha, beta, gamma, L=12):
    n = len(y)
    Level = [np.nan] * n
    Trend = [np.nan] * n
    Season = [np.nan] * (n + L)
    Forecast = [np.nan] * n

    # Initial Values
    init_level = sum(y[:L]) / L
    init_trend = ((sum(y[L:2*L]) / L) - init_level) / L

    for i in range(L):
        Season[i] = y[i] / init_level if init_level != 0 else 1.0

    Level[L-1] = init_level
    Trend[L-1] = init_trend

    for t in range(L, n):
        Forecast[t] = (Level[t-1] + Trend[t-1]) * Season[t-12]
        Level[t] = alpha * (y[t] / Season[t-12]) + (1 - alpha) * (Level[t-1] + Trend[t-1])
        Trend[t] = beta * (Level[t] - Level[t-1]) + (1 - beta) * Trend[t-1]
        Season[t] = gamma * (y[t] / Level[t]) + (1 - gamma) * Season[t-12]

    # พยากรณ์งวดถัดไป
    next_forecast = (Level[-1] + Trend[-1]) * Season[n - 12]
    return Level, Trend, Season[:n], Forecast, next_forecast

# --- 4. สร้าง UI แบบ 4 หน้าต่างหลัก (4 Tabs) ---
tab1, tab2, tab3, tab4 = st.tabs([
    products_data["carwash"]["name"],
    products_data["interior"]["name"],
    products_data["glass"]["name"],
    products_data["wheel"]["name"]
])

tabs_map = [
    (tab1, "carwash"),
    (tab2, "interior"),
    (tab3, "glass"),
    (tab4, "wheel")
]

for tab, p_key in tabs_map:
    with tab:
        p_info = products_data[p_key]
        
        st.subheader(f"คำนวณและพยากรณ์: {p_info['name']}")
        
        # กล่องรับข้อมูลยอดใช้จริงเดือนล่าสุด
        c_input, c_param = st.columns([1, 2])
        
        with c_input:
            st.markdown("### 📥 ป้อนข้อมูลล่าสุด")
            new_val = st.number_input(
                label="กรอกปริมาณการใช้จริงเดือนนี้ (ม.ค. 69) [ลิตร]:",
                min_value=0.0,
                value=float(p_info["history"][-1]),
                step=1.0,
                key=f"input_{p_key}"
            )
            st.info(f"⚙️ ค่าพารามิเตอร์ที่ใช้:  \n**α (Alpha)** = {p_info['alpha']}  \n**β (Beta)** = {p_info['beta']}  \n**γ (Gamma)** = {p_info['gamma']}")

        # เตรียมข้อมูล + เติมค่าใหม่ลงไป
        y_data = p_info["history"] + [new_val]
        labels = base_labels + ["ม.ค. 69"]
        
        # ประมวลผล Holt-Winters
        Level, Trend, Season, Forecast, next_f = run_holt_winters(
            y_data, p_info["alpha"], p_info["beta"], p_info["gamma"]
        )

        with c_param:
            st.markdown("### 📌 สรุปผลการพยากรณ์")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f'<div class="metric-card"><div class="metric-title">ยอดใช้จริง (ม.ค. 69)</div><div class="metric-value">{new_val:.2f} <small style="font-size:14px">ลิตร</small></div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card" style="border-left-color:#16a34a;"><div class="metric-title">คาดการณ์งวดถัดไป (ก.พ. 69)</div><div class="metric-value" style="color:#16a34a;">{next_f:.2f} <small style="font-size:14px">ลิตร</small></div></div>', unsafe_allow_html=True)
            with m3:
                diff = next_f - new_val
                color = "#dc2626" if diff < 0 else "#2563eb"
                st.markdown(f'<div class="metric-card" style="border-left-color:{color};"><div class="metric-title">ส่วนต่างคาดการณ์</div><div class="metric-value" style="color:{color};">{diff:+.2f} <small style="font-size:14px">ลิตร</small></div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # แสดงกราฟเส้น Plotly
        st.subheader("📈 กราฟแนวโน้มยอดใช้จริง vs ผลการพยากรณ์")
        fig = go.Figure()
        
        # เส้นยอดใช้จริง
        fig.add_trace(go.Scatter(
            x=labels, y=y_data,
            mode='lines+markers',
            name='ยอดใช้จริง (Actual)',
            line=dict(color='#0f172a', width=3),
            marker=dict(size=6)
        ))
        
        # เส้น HW-Forecast
        fig.add_trace(go.Scatter(
            x=labels[12:], y=Forecast[12:],
            mode='lines+markers',
            name='HW-Forecast (พยากรณ์)',
            line=dict(color='#2563eb', width=2, dash='dash'),
            marker=dict(size=5)
        ))

        # จุดคาดการณ์อนาคต (ก.พ. 69)
        fig.add_trace(go.Scatter(
            x=["ก.พ. 69"], y=[next_f],
            mode='markers+text',
            name='พยากรณ์ ก.พ. 69',
            marker=dict(color='#16a34a', size=12, symbol='star'),
            text=[f"{next_f:.2f}"],
            textposition="top center"
        ))

        fig.update_layout(
            xaxis_title="เดือน/ปี",
            yaxis_title="ปริมาณการใช้ (ลิตร)",
            hovermode="x unified",
            template="plotly_white",
            height=400,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # ตารางรายละเอียด
        st.subheader("📋 ตารางรายละเอียดคำนวณ (Level, Trend, Seasonality)")
        df = pd.DataFrame({
            "เดือน/ปี": labels,
            "ยอดใช้จริง (Y)": [f"{v:.2f}" for v in y_data],
            "Level (L)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Level],
            "Trend (T)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Trend],
            "Season (S)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Season],
            "HW-Forecast (F)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Forecast]
        })
        st.dataframe(df.style.highlight_max(axis=0, color='#e0f2fe'), use_container_width=True, height=300)
