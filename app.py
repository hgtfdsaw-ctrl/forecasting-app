import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
import copy

# --- 1. การตั้งค่าหน้าจอและ CSS ตกแต่ง ---
st.set_page_config(page_title="ระบบพยากรณ์และบริหารการสั่งซื้อวัสดุ Holt-Winters", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    /* บังคับไอคอนและข้อความในปุ่มกดของ Sidebar ทั้งหมดให้ชิดซ้าย 100% */
    section[data-testid="stSidebar"] button {
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
        text-align: left !important;
        padding-left: 16px !important;
    }
    section[data-testid="stSidebar"] button div, 
    section[data-testid="stSidebar"] button div p, 
    section[data-testid="stSidebar"] button p {
        justify-content: flex-start !important;
        text-align: left !important;
        width: 100% !important;
    }

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
    
    .product-header {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #0f172a;
        margin-bottom: 15px;
    }
    
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
    
    .large-label {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #1e3a8a;
        margin-top: 10px;
        margin-bottom: 5px;
    }

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

st.title("📊 ระบบพยากรณ์และบริหารการสั่งซื้อวัสดุต่อเนื่อง (Holt-Winters Model)")
st.caption("คำนวณและเก็บบันทึกประวัติเพื่อพยากรณ์ต่อเนื่องทุกเดือนอัตโนมัติ")

# --- 2. ฟังก์ชันช่วยคำนวณชื่อเดือนถัดไปอัตโนมัติ ---
months_base = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]

def get_next_month_label(last_label):
    parts = last_label.split(" ")
    m_name = parts[0]
    y_num = int(parts[1])
    m_idx = months_base.index(m_name)
    
    if m_idx == 11:
        return f"ม.ค. {y_num + 1}"
    else:
        return f"{months_base[m_idx + 1]} {y_num}"

# --- 3. ค่าตั้งต้นประวัติ 35 เดือน (ม.ค. 66 - พ.ย. 68) ---
base_labels_35 = [f"{m} 66" for m in months_base] + \
                 [f"{m} 67" for m in months_base] + \
                 [f"{m} 68" for m in months_base[:11]]

default_products = {
    "carwash": {
        "name": "🚗 น้ำยาล้างรถ (22)",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "default_last": 40.00,
        "history": [20.00, 25.00, 40.00, 50.00, 45.00, 40.00, 20.00, 15.00, 5.00, 10.00, 10.00, 25.00,
                    25.00, 30.00, 50.00, 65.00, 55.00, 50.00, 25.00, 15.00, 8.00, 12.00, 15.00, 30.00,
                    35.00, 40.00, 60.00, 80.00, 70.00, 65.00, 30.00, 20.00, 10.00, 15.00, 15.00],
        "labels": base_labels_35.copy()
    },
    "interior": {
        "name": "✨ น้ำยาเคลือบภายใน (22)",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "default_last": 24.18,
        "history": [14.88, 13.44, 18.60, 19.80, 18.60, 16.20, 3.72, 1.86, 0.90, 2.76, 12.60, 16.74,
                    18.60, 16.80, 22.32, 23.40, 22.32, 19.80, 5.58, 2.76, 1.32, 3.72, 16.20, 20.46,
                    22.32, 20.16, 26.04, 27.00, 26.04, 23.40, 7.44, 3.72, 1.80, 5.58, 19.80],
        "labels": base_labels_35.copy()
    },
    "glass": {
        "name": "🪟 น้ำยาเช็ดกระจก (22)",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "default_last": 16.12,
        "history": [9.92, 8.96, 12.40, 13.20, 12.40, 10.80, 2.48, 1.24, 0.60, 1.84, 8.40, 11.16,
                    12.40, 11.20, 14.88, 15.60, 14.88, 13.20, 3.72, 1.84, 0.88, 2.48, 10.80, 13.64,
                    14.88, 13.44, 17.36, 18.00, 17.36, 15.60, 4.96, 2.48, 1.20, 3.72, 13.20],
        "labels": base_labels_35.copy()
    },
    "wheel": {
        "name": "🛞 น้ำยาลงล้อ (22)",
        "alpha": 0.9, "beta": 0.99, "gamma": 0.99,
        "default_last": 8.06,
        "history": [4.96, 4.48, 6.20, 6.60, 6.20, 5.40, 1.24, 0.62, 0.30, 0.92, 4.20, 5.58,
                    6.20, 5.60, 7.44, 7.80, 7.44, 6.60, 1.86, 0.92, 0.44, 1.24, 5.40, 6.82,
                    7.44, 6.72, 8.68, 9.00, 8.68, 7.80, 2.48, 1.24, 0.60, 1.86, 6.60],
        "labels": base_labels_35.copy()
    }
}

# --- 4. สร้าง Session State สำหรับบันทึกประวัติยาวนาน ---
if "product_store" not in st.session_state:
    st.session_state.product_store = copy.deepcopy(default_products)

# --- 5. เมนูควบคุมการรีเซ็ตข้อมูล (Sidebar ชิดซ้าย ไม่มี Expander) ---
with st.sidebar:
    st.header("⚙️ เมนูรีเซ็ตข้อมูล")
    st.markdown("เลือกประเภทการรีเซ็ตที่ต้องการ:")

    if st.button("🔴 รีเซ็ตข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.product_store = copy.deepcopy(default_products)
        for key in list(st.session_state.keys()):
            if key.startswith("usage_") or key.startswith("stock_"):
                del st.session_state[key]
        st.success("✅ รีเซ็ตข้อมูลทั้งหมดกลับค่าเริ่มต้นเรียบร้อยแล้ว!")
        st.rerun()

    if st.button("📊 รีเซ็ตปริมาณการใช้งานทั้งหมด", use_container_width=True):
        for p_key in st.session_state.product_store:
            st.session_state.product_store[p_key]["history"] = copy.deepcopy(default_products[p_key]["history"])
            st.session_state.product_store[p_key]["labels"] = copy.deepcopy(default_products[p_key]["labels"])
        for key in list(st.session_state.keys()):
            if key.startswith("usage_"):
                del st.session_state[key]
        st.success("✅ รีเซ็ตประวัติยอดใช้งานทั้งหมดเรียบร้อยแล้ว!")
        st.rerun()

    if st.button("↩️ รีเซ็ตการใช้งานของเดือนก่อน", use_container_width=True):
        undo_success = False
        for p_key in st.session_state.product_store:
            if len(st.session_state.product_store[p_key]["history"]) > 35:
                st.session_state.product_store[p_key]["history"].pop()
                st.session_state.product_store[p_key]["labels"].pop()
                undo_success = True
        if undo_success:
            for key in list(st.session_state.keys()):
                if key.startswith("usage_"):
                    del st.session_state[key]
            st.success("✅ ย้อนกลับการบันทึกของเดือนก่อนเรียบร้อยแล้ว!")
            st.rerun()
        else:
            st.warning("⚠️ ไม่พบข้อมูลเดือนที่เพิ่มเข้ามา (อยู่ที่ประวัติเริ่มต้นแล้ว)")

    if st.button("📦 รีเซ็ตยอดคงเหลือทั้งหมด", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("stock_"):
                del st.session_state[key]
        st.success("✅ ล้างยอดคงเหลือของทุกสินค้าเรียบร้อยแล้ว!")
        st.rerun()

    if st.button("⏪ รีเซ็ตยอดคงเหลือของเดือนก่อน", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("stock_"):
                del st.session_state[key]
        st.success("✅ ล้างช่องยอดคงเหลือของงวดนี้เรียบร้อยแล้ว!")
        st.rerun()

# --- 6. ฟังก์ชันคำนวณ Holt-Winters Multiplicative ---
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

# --- 7. ฟังก์ชันคำนวณแยกประเภทถัง ---
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

# --- 8. สร้าง UI หน้าต่างหลัก ---
tabs = st.tabs([p["name"] for p in st.session_state.product_store.values()])
keys_list = list(st.session_state.product_store.keys())

for tab, p_key in zip(tabs, keys_list):
    with tab:
        p_info = st.session_state.product_store[p_key]
        
        last_recorded_month = p_info["labels"][-1]
        input_month_label = get_next_month_label(last_recorded_month)
        forecast_month_label = get_next_month_label(input_month_label)

        st.markdown(f'<div class="product-header">📦 ผลิตภัณฑ์: {p_info["name"]}</div>', unsafe_allow_html=True)
        
        c_input, c_results = st.columns([1.1, 1.9])
        
        with c_input:
            st.markdown(f'<div class="large-label">1. ปริมาณการใช้ของเดือนล่าสุด ({input_month_label}) (ลิตร):</div>', unsafe_allow_html=True)
            last_usage = st.number_input(
                label="ปริมาณการใช้เดือนล่าสุด",
                label_visibility="collapsed",
                min_value=0.0,
                value=None,
                placeholder=f"ตัวอย่าง: {p_info['default_last']}",
                step=1.0,
                key=f"usage_{p_key}"
            )
            
            st.markdown('<div class="large-label">2. ปริมาณยอดคงเหลือปัจจุบัน (ลิตร):</div>', unsafe_allow_html=True)
            stock_qty_input = st.number_input(
                label="ปริมาณยอดคงเหลือ",
                label_visibility="collapsed",
                min_value=0.0,
                value=None,
                placeholder="กรอกตัวเลขยอดคงเหลือ...",
                step=1.0,
                key=f"stock_{p_key}"
            )
            
            st.info(f"⚙️ ค่าพารามิเตอร์โมเดล:  \n**α (Alpha)** = {p_info['alpha']} | **β (Beta)** = {p_info['beta']} | **γ (Gamma)** = {p_info['gamma']}")

        # --- คำนวณเมื่อกรอกข้อมูลครบ ---
        if last_usage is not None and stock_qty_input is not None:
            
            y_data = p_info["history"] + [last_usage]
            current_labels = p_info["labels"] + [input_month_label]

            Level, Trend, Season, Forecast, next_f = run_holt_winters(
                y_data, p_info["alpha"], p_info["beta"], p_info["gamma"]
            )

            error_val = next_f * 0.01
            net_needed = next_f - stock_qty_input

            if net_needed > 0:
                recommended_qty = math.ceil(net_needed / 10.0) * 10
            else:
                recommended_qty = 0

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
                tanks_display_html = "<div style='font-size:20px; font-weight:800; color:#1e40af; margin-top:10px;'>ไม่ต้องสั่งซื้อ</div>"

            # แสดงผลการคำนวณ
            with c_results:
                st.markdown(f'<div class="large-label">📌 สรุปผลพยากรณ์ประจำเดือน: <span style="color:#2563eb;">{forecast_month_label}</span></div>', unsafe_allow_html=True)
                
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown(f'''
                        <div class="card-base">
                            <div class="card-title">1. ผลการพยากรณ์ ({forecast_month_label})</div>
                            <div class="card-value" style="color:#2563eb;">{next_f:.2f} <small style="font-size:16px">ลิตร</small></div>
                        </div>
                    ''', unsafe_allow_html=True)
                with r2:
                    st.markdown(f'''
                        <div class="card-base">
                            <div class="card-title">2. ค่าความคลาดเคลื่อน (1%)</div>
                            <div style="font-size: 17px; font-weight: 800; color: #16a34a; margin-top: 4px;">
                                คลาดเคลื่อน (+): +{error_val:.2f} ลิตร
                            </div>
                            <div style="font-size: 17px; font-weight: 800; color: #dc2626; margin-top: 2px;">
                                คลาดเคลื่อน (-): -{error_val:.2f} ลิตร
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)

                r3, r4 = st.columns(2)
                with r3:
                    st.markdown(f'''
                        <div class="card-recommend">
                            <div class="card-recommend-title">3. ปริมาณสั่งซื้อแนะนำ</div>
                            <div class="card-recommend-value">{recommended_qty} <small style="font-size:18px">ลิตร</small></div>
                            <div style="font-size:13px; color:#15803d; margin-top:4px; font-weight:600;">(พยากรณ์ {next_f:.2f} - คงเหลือ {stock_qty_input:.0f} ➔ ปัดขึ้นลงท้าย 0)</div>
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
                if st.button(f"🟢 บันทึกยอด {input_month_label} และร่นไปคำนวณเดือน {forecast_month_label} ➔", key=f"btn_save_{p_key}", type="primary", use_container_width=True):
                    st.session_state.product_store[p_key]["history"].append(last_usage)
                    st.session_state.product_store[p_key]["labels"].append(input_month_label)
                    
                    if f"usage_{p_key}" in st.session_state:
                        del st.session_state[f"usage_{p_key}"]
                    if f"stock_{p_key}" in st.session_state:
                        del st.session_state[f"stock_{p_key}"]

                    st.success(f"✅ บันทึกยอดใช้จริงของเดือน {input_month_label} เรียบร้อยแล้ว! ระบบร่นไปงวดถัดไปแล้วครับ")
                    st.rerun()

        st.markdown("---")

        if last_usage is not None and stock_qty_input is not None:
            st.subheader(f"📈 กราฟแสดงแนวโน้มประวัติการใช้งานและการพยากรณ์ ({forecast_month_label})")
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=current_labels, y=y_data,
                mode='lines+markers',
                name='ยอดใช้จริง (Actual)',
                line=dict(color='#0f172a', width=3),
                marker=dict(size=6)
            ))
            
            fig.add_trace(go.Scatter(
                x=current_labels[12:], y=Forecast[12:],
                mode='lines+markers',
                name='HW-Forecast (พยากรณ์)',
                line=dict(color='#2563eb', width=2, dash='dash'),
                marker=dict(size=5)
            ))

            fig.add_trace(go.Scatter(
                x=[forecast_month_label], y=[next_f],
                mode='markers+text',
                name=f'พยากรณ์ {forecast_month_label}: {next_f:.2f} ลิตร',
                marker=dict(color='#16a34a', size=14, symbol='star'),
                text=[f"{next_f:.2f} ลิตร"],
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

            with st.expander("📋 ดูตารางรายละเอียดประวัติและการคำนวณทั้งหมด"):
                df = pd.DataFrame({
                    "งวด/เดือน/ปี": current_labels,
                    "ยอดใช้จริง (Y)": [f"{v:.2f}" for v in y_data],
                    "Level (L)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Level],
                    "Trend (T)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Trend],
                    "Season (S)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Season],
                    "HW-Forecast (F)": [f"{v:.2f}" if not np.isnan(v) else "-" for v in Forecast]
                })
                st.dataframe(df, use_container_width=True, height=250)
        else:
            with c_results:
                st.markdown(f'''
                    <div style="background-color: #fefce8; border: 2px dashed #eab308; border-radius: 14px; padding: 35px 20px; text-align: center; margin-top: 10px;">
                        <div style="font-size: 45px; margin-bottom: 10px;">📝</div>
                        <div style="font-size: 24px; font-weight: 800; color: #854d0e;">กรุณากรอกข้อมูลให้ครบทั้ง 2 ช่อง</div>
                        <div style="font-size: 19px; color: #a16207; margin-top: 10px; line-height: 1.6;">
                            1. ปริมาณการใช้ของเดือนล่าสุด <strong>({input_month_label})</strong><br>
                            2. ปริมาณยอดคงเหลือปัจจุบัน<br><br>
                            <strong style="color: #854d0e;">⚡ เมื่อกรอกครบแล้ว ระบบจะคำนวณผลพยากรณ์สำหรับเดือน ({forecast_month_label}) ให้ทันที</strong>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
        
