import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

# --- 1. การตั้งค่าหน้าจอและ CSS ตกแต่งสำหรับผู้สูงอายุ (ตัวหนังสือใหญ่ ชัดเจน 22px) ---
st.set_page_config(page_title="ระบบพยากรณ์ยอดใช้วัสดุ Holt-Winters", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    /* ตกแต่ง Tab เมนู ผลิตภัณฑ์ ขนาด 22px */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 12px 12px 0 0;
        border: 2px solid #cbd5e1;
        padding: 10px 24px;
        font-weight: 700;
        font-size: 22px !important;
        color: #334155;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-color: #1e293b !important;
    }
    
    /* หัวข้อขนาด 22px */
    .product-header {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #0f172a;
        margin-bottom: 15px;
    }
    
    /* ปรับแต่ง ช่องกรอกตัวเลข ตัวใหญ่ มองเห็นชัดเจน ไร้ปุ่ม + - */
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { 
        -webkit-appearance: none; 
        margin: 0; 
    }
    input[type=number] { 
        -moz-appearance: textfield; 
        font-size: 26px !important;
        font-weight: bold !important;
        height: 60px !important;
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 2px solid #94a3b8 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stNumberInputStepDown"], div[data-testid="stNumberInputStepUp"] {
        display: none !important;
    }
    
    /* ปรับ Label หัวข้อช่องกรอก */
    .large-label {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #1e293b;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    /* กล่องการแสดงผล */
    .card-base {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 14px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 10px;
        min-height: 140px;
    }
    .card-title { font-size: 16px; color: #475569; font-weight: 700; }
    .card-value { font-size: 28px; color: #0f172a; font-weight: 800; margin-top: 4px; }
    
    /* กล่องเน้นพิเศษ ปริมาณแนะนำสั่งซื้อ & จำนวนถัง */
    .card-recommend {
        background-color: #f0fdf4;
        padding: 20px;
        border-radius: 14px;
        border: 3px solid #16a34a;
        box-shadow: 0 4px 10px rgba(22, 163, 74, 0.15);
        margin-bottom: 10px;
        min-height: 160px;
    }
    .card-recommend-title { font-size: 18px; color: #15803d; font-weight: 800; }
    .card-recommend-value { font-size: 34px; color: #15803d; font-weight: 900; margin-top: 5px; }

    .card-tanks {
        background-color: #eff6ff;
        padding: 18px;
        border-radius: 14px;
        border: 3px solid #2563eb;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.15);
        margin-bottom: 10px;
        min-height: 160px;
    }
    .card-tanks-title { font-size: 18px; color: #1d4ed8; font-weight: 800; margin-bottom: 6px; }

    /* ตารางย่อยสำหรับแยกช่องจำนวนถัง */
    .tank-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 5px;
    }
    .tank-table th {
        border-bottom: 2px solid #93c5fd;
        padding: 4px 8px;
        font-size: 16px;
        font-weight: 700;
        color: #1e40af;
        text-align: left;
    }
    .tank-table td {
        padding: 6px 8px;
        font-size: 20px;
        font-weight: 800;
        color: #1e3a8a;
    }
    .tank-table td.qty-col {
        text-align: right;
        color: #2563eb;
        font-size: 22px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 ระบบพยากรณ์และบริหารการสั่งซื้อวัสดุ (Holt-Winters Model)")
st.caption("คำนวณตามสูตร Holt-Winters Multiplicative Seasonal Smoothing (ฤดูกาล 12 เดือน)")

# --- 2. ข้อมูลย้อนหลัง 36 เดือน (ปี 2566 - 2568) ---
months_base = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
years_base = ["66", "67", "68"]
base_labels = [f"{m} {y}" for y in years_base for m in months_base]

products_data = {
    "carwash": {
        "name": "🚗 น้ำยาล้างรถ (22)",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "history": [20.00, 25.00, 40.00, 50.00, 45.00, 40.00, 20.00, 15.00, 5.00, 10.00, 10.00, 25.00,
                    25.00, 30.00, 50.00, 65.00, 55.00, 50.00, 25.00, 15.00, 8.00, 12.00, 15.00, 30.00,
                    35.00, 40.00, 60.00, 80.00, 70.00, 65.00, 30.00, 20.00, 10.00, 15.00, 15.00, 40.00]
    },
    "interior": {
        "name": "✨ น้ำยาเคลือบภายใน (22)",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "history": [14.88, 13.44, 18.60, 19.80, 18.60, 16.20, 3.72, 1.86, 0.90, 2.76, 12.60, 16.74,
                    18.60, 16.80, 22.32, 23.40, 22.32, 19.80, 5.58, 2.76, 1.32, 3.72, 16.20, 20.46,
                    22.32, 20.16, 26.04, 27.00, 26.04, 23.40, 7.44, 3.72, 1.80, 5.58, 19.80, 24.18]
    },
    "glass": {
        "name": "🪟 น้ำยาเช็ดกระจก (22)",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "history": [9.92, 8.96, 12.40, 13.20, 12.40, 10.80, 2.48, 1.24, 0.60, 1.84, 8.40, 11.16,
                    12.40, 11.20, 14.88, 15.60, 14.88, 13.20, 3.72, 1.84, 0.88, 2.48, 10.80, 13.64,
                    14.88, 13.44, 17.36, 18.00, 17.36, 15.60, 4.96, 2.48, 1.20, 3.72, 13.20, 16.12]
    },
    "wheel": {
        "name": "🛞 น้ำยาลงล้อ (22)",
        "alpha": 0.9, "beta": 0.99, "gamma": 0.99,
        "history": [4.96, 4.48, 6.20, 6.60, 6.20, 5.40, 1.24, 0.62, 0.30, 0.92, 4.20, 5.58,
                    6.20, 5.60, 7.44, 7.80, 7.44, 6.60, 1.86, 0.92, 0.44, 1.24, 5.40, 6.82,
                    7.44, 6.72, 8.68, 9.00, 8.68, 7.80, 2.48, 1.24, 0.60, 1.86, 6.60, 8.06]
    }
}

# --- 3. ฟังก์ชันคำนวณ Holt-Winters Multiplicative ---
def run_holt_winters(y, alpha, beta, gamma, L=12):
    n = len(y)
    Level = [np.nan] * n
    Trend = [np.nan] * n
    Season = [np.nan] * (n + L)
    Forecast = [np.nan] * n

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

    next_forecast = (Level[-1] + Trend[-1]) * Season[n - 12]
    return Level, Trend, Season[:n], Forecast, next_forecast

# --- 4. ฟังก์ชันคำนวณแยกช่องย่อยประเภทขนาดถัง ---
def get_tank_rows(product_key, order_qty):
    if order_qty <= 0:
        return []

    if product_key == "carwash":
        best_t30, best_t20 = 0, 0
        min_waste = float('inf')
        min_tanks = float('inf')

        max_30 = math.ceil(order_qty / 30) + 1
        for t30 in range(max_30, -1, -1):
            rem = order_qty - 30 * t30
            t20 = math.ceil(rem / 20) if rem > 0 else 0
            
            total_vol = 30 * t30 + 20 * t20
            waste = total_vol - order_qty
            tanks_count = t30 + t20

            if waste < min_waste or (waste == min_waste and tanks_count < min_tanks):
                min_waste = waste
                min_tanks = tanks_count
                best_t30 = t30
                best_t20 = t20

        rows = []
        if best_t30 > 0:
            rows.append(("ถัง 30 ลิตร", f"{best_t30} ถัง"))
        if best_t20 > 0:
            rows.append(("ถัง 20 ลิตร", f"{best_t20} ถัง"))
        return rows
    else:
        t30 = order_qty // 30
        rem = order_qty % 30
        t20 = rem // 20
        rem = rem % 20
        t10 = rem // 10

        rows = []
        if t30 > 0:
            rows.append(("ถัง 30 ลิตร", f"{t30} ถัง"))
        if t20 > 0:
            rows.append(("ถัง 20 ลิตร", f"{t20} ถัง"))
        if t10 > 0:
            rows.append(("ถัง 10 ลิตร", f"{t10} ถัง"))
        return rows

# --- 5. สร้าง UI หน้าต่างหลัก 4 Tabs ---
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
        
        st.markdown(f'<div class="product-header">📦 ผลิตภัณฑ์: {p_info["name"]}</div>', unsafe_allow_html=True)
        
        # ส่วนป้อนข้อมูล
        c_input, c_results = st.columns([1, 2])
        
        with c_input:
            st.markdown('<div class="large-label">1. ปริมาณการใช้ของเดือนล่าสุด (ลิตร):</div>', unsafe_allow_html=True)
            last_usage = st.number_input(
                label="ปริมาณการใช้เดือนล่าสุด",
                label_visibility="collapsed",
                min_value=0.0,
                value=None,
                placeholder="กรอกตัวเลข...",
                step=1.0,
                key=f"usage_{p_key}"
            )
            
            st.markdown('<div class="large-label">2. ปริมาณยอดคงเหลือ (ลิตร):</div>', unsafe_allow_html=True)
            stock_qty_input = st.number_input(
                label="ปริมาณยอดคงเหลือ",
                label_visibility="collapsed",
                min_value=0.0,
                value=None,
                placeholder="กรอกตัวเลข...",
                step=1.0,
                key=f"stock_{p_key}"
            )
            
            st.info(f"⚙️ ค่าพารามิเตอร์โมเดล:  \n**α (Alpha)** = {p_info['alpha']} | **β (Beta)** = {p_info['beta']} | **γ (Gamma)** = {p_info['gamma']}")

        # ประมวลผลข้อมูล Holt-Winters แบบไดนามิก
        if last_usage is not None:
            y_data = p_info["history"] + [last_usage]
            labels = base_labels + ["เดือนล่าสุด"]
        else:
            y_data = p_info["history"]
            labels = base_labels

        Level, Trend, Season, Forecast, next_f = run_holt_winters(
            y_data, p_info["alpha"], p_info["beta"], p_info["gamma"]
        )

        # 1. การคำนวณความคลาดเคลื่อน 1% (แยกค่า + และ - ชัดเจน)
        error_val = next_f * 0.01

        # 2. การคำนวณปริมาณแนะนำสั่งซื้อ:
        # นำ (ผลพยากรณ์ - ยอดคงเหลือ) หากเหลือ 41 จะปัดขึ้นเป็น 50 ลิตรทันที
        stock_qty = stock_qty_input if stock_qty_input is not None else 0.0
        net_needed = next_f - stock_qty

        if net_needed > 0:
            recommended_qty = math.ceil(net_needed / 10.0) * 10
        else:
            recommended_qty = 0

        # 3. จัดสร้างตารางแยกช่องย่อยจำนวนถัง
        tank_rows = get_tank_rows(p_key, recommended_qty)
        if tank_rows:
            table_html_rows = "".join([
                f"<tr><td>{size}</td><td class='qty-col'>{qty}</td></tr>" 
                for size, qty in tank_rows
            ])
            tanks_display_html = f"""
                <table class="tank-table">
                    <thead>
                        <tr>
                            <th>ขนาดถัง</th>
                            <th style="text-align:right;">จำนวนสั่ง</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_html_rows}
                    </tbody>
                </table>
            """
        else:
            tanks_display_html = "<div style='font-size:22px; font-weight:800; color:#1e40af; margin-top:10px;'>ไม่ต้องสั่งซื้อ</div>"

        # ส่วนการแสดงผล 4 ช่องหลัก
        with c_results:
            st.markdown('<div class="large-label">📌 สรุปผลการคำนวณและการสั่งซื้อ</div>', unsafe_allow_html=True)
            
            r1, r2 = st.columns(2)
            with r1:
                st.markdown(f'''
                    <div class="card-base">
                        <div class="card-title">1. ผลการพยากรณ์ (Forecast)</div>
                        <div class="card-value" style="color:#2563eb;">{next_f:.2f} <small style="font-size:16px">ลิตร</small></div>
                    </div>
                ''', unsafe_allow_html=True)
            with r2:
                st.markdown(f'''
                    <div class="card-base">
                        <div class="card-title">2. ค่าความคลาดเคลื่อน (1%)</div>
                        <div style="font-size: 18px; font-weight: 800; color: #16a34a; margin-top: 4px;">
                            คลาดเคลื่อน (+): +{error_val:.2f} ลิตร
                        </div>
                        <div style="font-size: 18px; font-weight: 800; color: #dc2626; margin-top: 2px;">
                            คลาดเคลื่อน (-): -{error_val:.2f} ลิตร
                        </div>
                    </div>
                ''', unsafe_allow_html=True)

            r3, r4 = st.columns(2)
            with r3:
                st.markdown(f'''
                    <div class="card-recommend">
                        <div class="card-recommend-title">3. ปริมาณการสั่งซื้อที่แนะนำ</div>
                        <div class="card-recommend-value">{recommended_qty} <small style="font-size:18px">ลิตร</small></div>
                        <div style="font-size:13px; color:#15803d; margin-top:4px; font-weight:600;">(ผลพยากรณ์ {next_f:.2f} - คงเหลือ {stock_qty:.0f} ➔ ปัดขึ้นลงท้าย 0)</div>
                    </div>
                ''', unsafe_allow_html=True)
            with r4:
                st.markdown(f'''
                    <div class="card-tanks">
                        <div class="card-tanks-title">4. จำนวนถังที่ต้องสั่งซื้อ</div>
                        {tanks_display_html}
                    </div>
                ''', unsafe_allow_html=True)

        st.markdown("---")

        # กราฟแสดงแนวโน้ม
        st.subheader("📈 กราฟแสดงแนวโน้มการใช้งานย้อนหลังและการพยากรณ์")
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=labels, y=y_data,
            mode='lines+markers',
            name='ยอดใช้จริง (Actual)',
            line=dict(color='#0f172a', width=3),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=labels[12:], y=Forecast[12:],
            mode='lines+markers',
            name='HW-Forecast (พยากรณ์)',
            line=dict(color='#2563eb', width=2, dash='dash'),
            marker=dict(size=5)
        ))

        fig.add_trace(go.Scatter(
            x=["งวดถัดไป"], y=[recommended_qty],
            mode='markers+text',
            name=f'ยอดแนะนำสั่งซื้อ: {recommended_qty} ลิตร',
            marker=dict(color='#16a34a', size=14, symbol='star'),
            text=[f"{recommended_qty} ลิตร"],
            textposition="top center"
        ))

        fig.update_layout(
            xaxis_title="เดือน/ปี",
            yaxis_title="ปริมาณการใช้ (ลิตร)",
            hovermode="x unified",
            template="plotly_white",
            height=380,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # ตารางรายละเอียดคำนวณ
        with st.expander("📋 ดูตารางรายละเอียดการคำนวณ (Level, Trend, Seasonality)"):
            df = pd.DataFrame({
                "งวด/เดือน/ปี": labels,
                "ยอดใช้จริง (Y)": [f"{v:.2f}" for v in y_data],
                "Level (L)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Level],
                "Trend (T)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Trend],
                "Season (S)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Season],
                "HW-Forecast (F)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Forecast]
            })
            st.dataframe(df, use_container_width=True, height=250)
