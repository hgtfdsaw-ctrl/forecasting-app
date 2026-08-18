import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
import copy
from datetime import datetime, timedelta

# --- 1. การตั้งค่าหน้าจอและ CSS ตกแต่ง ---
st.set_page_config(
    page_title="ระบบพยากรณ์และบริหารการสั่งซื้อผลิตภัณฑ์", 
    page_icon="📈", 
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    /* Header & Icon Style */
    .header-container {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
        padding-bottom: 10px;
    }
    .header-icon-box {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        padding: 14px;
        border-radius: 18px;
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .header-title-text {
        font-size: 30px !important;
        font-weight: 800 !important;
        color: #0f172a;
        margin: 0;
        line-height: 1.2;
    }
    .header-subtitle-text {
        font-size: 16px !important;
        color: #64748b;
        margin-top: 4px;
        margin-bottom: 0;
    }
    
    /* Sidebar Styling & Font Sizes */
    .reset-category-header {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #1e293b;
        margin-top: 14px;
        margin-bottom: 6px;
        padding-bottom: 4px;
        border-bottom: 2px solid #cbd5e1;
    }
    
    section[data-testid="stSidebar"] button {
        font-size: 14px !important;
        font-weight: 700 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        padding: 6px 12px !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 12px 12px 0 0;
        border: 2px solid #cbd5e1;
        padding: 10px 24px;
        font-weight: 700;
        font-size: 20px !important;
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
        min-height: 160px;
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
        font-size: 15px;
        font-weight: 700;
        color: #1e40af;
        text-align: left;
    }
    .tank-table td {
        padding: 4px 8px;
        font-size: 18px;
        font-weight: 800;
        color: #1e3a8a;
    }
    .tank-table td.qty-col {
        text-align: right;
        color: #2563eb;
        font-size: 20px;
    }

    .policy-tag {
        display: inline-block;
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 15px;
        margin-bottom: 12px;
        border: 1px solid #7dd3fc;
    }

    /* Product Cost Card Style */
    .prod-cost-card {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .prod-cost-title {
        font-size: 20px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 12px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 8px;
    }
    .cost-box {
        padding: 12px 14px;
        border-radius: 10px;
        text-align: center;
    }
    .cost-box-title { font-size: 13px; font-weight: 700; color: #64748b; }
    .cost-box-val { font-size: 20px; font-weight: 800; margin-top: 4px; }
    .cost-winner {
        background-color: #f0fdf4;
        border: 2px solid #16a34a;
    }
    .cost-winner .cost-box-title { color: #15803d; }
    .cost-winner .cost-box-val { color: #15803d; }
    .cost-normal {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
    }
    .cost-normal .cost-box-val { color: #334155; }
    </style>
""", unsafe_allow_html=True)

# --- 2. หัวข้อหลักพร้อมไอคอน SVG ---
st.markdown("""
    <div class="header-container">
        <div class="header-icon-box">
            <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
                <path d="M3 3l7 7 4-4 7 7"></path>
                <polyline points="14 6 21 6 21 13"></polyline>
            </svg>
        </div>
        <div>
            <h1 class="header-title-text">ระบบพยากรณ์และบริหารการสั่งซื้อผลิตภัณฑ์ (Hybrid Policy Engine)</h1>
            <p class="header-subtitle-text">วิเคราะห์การพยากรณ์ Holt-Winters โครงสร้างแบบจำลองคลังสินค้า EOQ / POQ / ROP / SS</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. ฟังก์ชันช่วยคำนวณชื่อเดือนถัดไปอัตโนมัติ ---
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

# --- 4. ข้อมูลพารามิเตอร์โมเดลคลังสินค้า ---
inventory_params = {
    "carwash": {
        "policy": "EOQ", "k": 1, "d_avg": 43.07, "h": 1.50, "eoq": 33.89, "ss": 9.35, "rop": 12.94,
        "selected_lot": 40, "poq_cost": 16236.66, "eoq_cost": 13506.66, "fc_cost": 17901.66, "best_cost": 13506.66,
        "lead_time_days": 2.5, "vc": 0.37,
        "price_per_liter": 30,
        "tank_prices": {30: 900, 20: 600},
        "rationale": "**ประหยัดกว่าวิธีอื่นยังไง:** เนื่องจากเป็นสินค้าที่มีอุปสงค์สูงและสม่ำเสมอ ($VC = 0.37 \\le 0.5$) การสั่งซื้อด้วยขนาดล็อตประหยัด **EOQ (ครั้งละ 40 ลิตร)** จะลดความถี่การสั่งซื้อลงได้มาก โดยไม่ทำให้เกิดค่าเก็บรักษาคลังสินค้าที่สูงเกินไป ประหยัดกว่าการสั่งตามพยากรณ์ถึง **4,395.00 บาท/ปี**"
    },
    "interior": {
        "policy": "POQ", "k": 1, "d_avg": 20.03, "h": 1.50, "eoq": 23.11, "ss": 3.71, "rop": 5.38,
        "selected_lot": 30, "poq_cost": 7093.70, "eoq_cost": 11316.20, "fc_cost": 9474.95, "best_cost": 7093.70,
        "lead_time_days": 2.5, "vc": 0.48,
        "price_per_liter": 30,
        "tank_prices": {30: 900, 20: 600, 10: 300},
        "rationale": "**ประหยัดกว่าวิธีอื่นยังไง:** มีความผันผวนของอุปสงค์ระดับปานกลาง ($VC = 0.48$) การใช้ **POQ ($k=1$)** รวบคำสั่งซื้อรายเดือน จะช่วยปรับปริมาณสั่งซื้อให้พอดีกับความต้องการแต่ละช่วง ป้องกันไม่ให้สต็อกเหลือค้างคลัง ประหยัดกว่าวิธี EOQ ถึง **4,222.50 บาท/ปี**"
    },
    "glass": {
        "policy": "POQ", "k": 1, "d_avg": 13.35, "h": 2.00, "eoq": 16.34, "ss": 2.21, "rop": 3.32,
        "selected_lot": 20, "poq_cost": 6175.13, "eoq_cost": 10021.13, "fc_cost": 9654.88, "best_cost": 6175.13,
        "lead_time_days": 2.0, "vc": 0.52,
        "price_per_liter": 40,
        "tank_prices": {30: 1200, 20: 800, 10: 400},
        "rationale": "**ประหยัดกว่าวิธีอื่นยังไง:** เป็นสินค้าที่มีราคาสูงกว่ากลุ่ม (40 บาท/ลิตร) และค่าถือครองสูง ($h=2.00$) การใช้ **POQ ($k=1$)** ช่วยให้ไม่ต้องสั่งล็อตใหญ่มาดองไว้ในคลัง ลดต้นทุนการเก็บรักษาได้อย่างมหาศาล ประหยัดกว่าวิธี EOQ ถึง **3,846.00 บาท/ปี**"
    },
    "wheel": {
        "policy": "POQ", "k": 3, "d_avg": 2.76, "h": 1.50, "eoq": 8.58, "ss": 0.44, "rop": 0.67,
        "selected_lot": 10, "poq_cost": 2066.39, "eoq_cost": 4062.89, "fc_cost": 4062.89, "best_cost": 2066.39,
        "lead_time_days": 3.0, "vc": 0.65,
        "price_per_liter": 30,
        "tank_prices": {30: 900, 20: 600, 10: 300},
        "rationale": "**ประหยัดกว่าวิธีอื่นยังไง:** สินค้ามีการใช้น้อยและผันผวนสูงมาก ($VC = 0.65$) การใช้นโยบาย **POQ ($k=3$)** คือการรวบงวดสั่งซื้อทุกๆ 3 เดือน ตัดค่าใช้จ่ายในการสั่งซื้อบ่อยๆ ออกไป ประหยัดกว่าวิธี EOQ และแบบพยากรณ์ถึง **1,996.50 บาท/ปี**"
    }
}

# --- 5. ค่าตั้งต้นประวัติ 35 เดือน ---
base_labels_35 = [f"{m} 66" for m in months_base] + \
                 [f"{m} 67" for m in months_base] + \
                 [f"{m} 68" for m in months_base[:11]]

default_products = {
    "carwash": {
        "name": "🚗 น้ำยาล้างรถ",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "history": [20.00, 25.00, 40.00, 50.00, 45.00, 40.00, 20.00, 15.00, 5.00, 10.00, 10.00, 25.00,
                    25.00, 30.00, 50.00, 65.00, 55.00, 50.00, 25.00, 15.00, 8.00, 12.00, 15.00, 30.00,
                    35.00, 40.00, 60.00, 80.00, 70.00, 65.00, 30.00, 20.00, 10.00, 15.00, 15.00],
        "labels": base_labels_35.copy()
    },
    "interior": {
        "name": "✨ น้ำยาเคลือบภายใน",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "history": [14.88, 13.44, 18.60, 19.80, 18.60, 16.20, 3.72, 1.86, 0.90, 2.76, 12.60, 16.74,
                    18.60, 16.80, 22.32, 23.40, 22.32, 19.80, 5.58, 2.76, 1.32, 3.72, 16.20, 20.46,
                    22.32, 20.16, 26.04, 27.00, 26.04, 23.40, 7.44, 3.72, 1.80, 5.58, 19.80],
        "labels": base_labels_35.copy()
    },
    "glass": {
        "name": "🪟 น้ำยาเช็ดกระจก",
        "alpha": 0.5, "beta": 0.01, "gamma": 0.99,
        "history": [9.92, 8.96, 12.40, 13.20, 12.40, 10.80, 2.48, 1.24, 0.60, 1.84, 8.40, 11.16,
                    12.40, 11.20, 14.88, 15.60, 14.88, 13.20, 3.72, 1.84, 0.88, 2.48, 10.80, 13.64,
                    14.88, 13.44, 17.36, 18.00, 17.36, 15.60, 4.96, 2.48, 1.20, 3.72, 13.20],
        "labels": base_labels_35.copy()
    },
    "wheel": {
        "name": "🛞 น้ำยาลงล้อ",
        "alpha": 0.9, "beta": 0.99, "gamma": 0.99,
        "history": [4.96, 4.48, 6.20, 6.60, 6.20, 5.40, 1.24, 0.62, 0.30, 0.92, 4.20, 5.58,
                    6.20, 5.60, 7.44, 7.80, 7.44, 6.60, 1.86, 0.92, 0.44, 1.24, 5.40, 6.82,
                    7.44, 6.72, 8.68, 9.00, 8.68, 7.80, 2.48, 1.24, 0.60, 1.86, 6.60],
        "labels": base_labels_35.copy()
    }
}

# --- 6. สร้าง Session State ---
if "product_store" not in st.session_state:
    st.session_state.product_store = copy.deepcopy(default_products)

# --- 7. Callback Function บันทึกข้อมูล ---
def cb_save_data(p_key, usage_val, label_val):
    st.session_state.product_store[p_key]["history"].append(usage_val)
    st.session_state.product_store[p_key]["labels"].append(label_val)
    st.session_state[f"usage_{p_key}"] = None
    st.session_state[f"stock_{p_key}"] = None
    st.session_state[f"success_msg_{p_key}"] = f"✅ บันทึกยอดใช้จริงของเดือน {label_val} เรียบร้อยแล้ว! ระบบร่นไปงวดถัดไปแล้วครับ"

# --- 8. Sidebar จัดการรีเซ็ต ---
with st.sidebar:
    st.header("⚙️ ระบบควบคุมแอป")
    st.markdown('<div class="reset-category-header">📊 ปริมาณใช้งาน</div>', unsafe_allow_html=True)
    if st.button("↩️ รีเซ็ตปริมาณใช้งานเดือนก่อน", type="secondary", use_container_width=True):
        for p_key in st.session_state.product_store:
            if len(st.session_state.product_store[p_key]["history"]) > 35:
                st.session_state.product_store[p_key]["history"].pop()
                st.session_state.product_store[p_key]["labels"].pop()
            if f"usage_{p_key}" in st.session_state:
                st.session_state[f"usage_{p_key}"] = None
        st.rerun()
        
    if st.button("🗑️ รีเซ็ตปริมาณใช้งานทั้งหมด", type="secondary", use_container_width=True):
        for p_key in st.session_state.product_store:
            st.session_state.product_store[p_key]["history"] = copy.deepcopy(default_products[p_key]["history"])
            st.session_state.product_store[p_key]["labels"] = copy.deepcopy(default_products[p_key]["labels"])
            if f"usage_{p_key}" in st.session_state:
                st.session_state[f"usage_{p_key}"] = None
        st.rerun()

    st.markdown('<div class="reset-category-header">📦 ปริมาณคงเหลือ</div>', unsafe_allow_html=True)
    if st.button("↩️ รีเซ็ตปริมาณคงเหลือเดือนก่อน", type="secondary", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith("stock_"):
                st.session_state[k] = None
        st.rerun()
        
    if st.button("🗑️ รีเซ็ตปริมาณคงเหลือทั้งหมด", type="secondary", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith("stock_"):
                st.session_state[k] = None
        st.rerun()

    st.markdown('<div class="reset-category-header">🚨 รีเซ็ตระบบทั้งหมด</div>', unsafe_allow_html=True)
    if st.button("🔄 รีเซ็ตข้อมูลทั้งหมด", type="secondary", use_container_width=True):
        st.session_state.product_store = copy.deepcopy(default_products)
        for k in list(st.session_state.keys()):
            if k.startswith("usage_") or k.startswith("stock_") or k.startswith("success_msg_"):
                del st.session_state[k]
        st.rerun()

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    if st.button("⚡ รีบูทแอปพลิเคชัน (Reboot)", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 9. ฟังก์ชันคำนวณ Holt-Winters ---
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

# --- 10. ฟังก์ชันคำนวณถังและยอดเงิน ---
def get_tank_rows_and_cost(product_key, order_qty):
    if order_qty <= 0:
        return [], 0.0

    prices = inventory_params[product_key]["tank_prices"]

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
        total_cost = (best_t30 * prices[30]) + (best_t20 * prices[20])
        if best_t30 > 0:
            rows.append(("ถัง 30 ลิตร", f"{best_t30} ถัง"))
        if best_t20 > 0:
            rows.append(("ถัง 20 ลิตร", f"{best_t20} ถัง"))
        return rows, total_cost
    else:
        t30 = order_qty // 30
        rem = order_qty % 30
        t20 = rem // 20
        rem = rem % 20
        t10 = rem // 10

        rows = []
        total_cost = (t30 * prices[30]) + (t20 * prices[20]) + (t10 * prices[10])
        if t30 > 0:
            rows.append(("ถัง 30 ลิตร", f"{t30} ถัง"))
        if t20 > 0:
            rows.append(("ถัง 20 ลิตร", f"{t20} ถัง"))
        if t10 > 0:
            rows.append(("ถัง 10 ลิตร", f"{t10} ถัง"))
        return rows, total_cost

# --- 11. แสดง 4 แท็บผลิตภัณฑ์หลัก ---
tabs = st.tabs([p["name"] for p in st.session_state.product_store.values()])
keys_list = list(st.session_state.product_store.keys())

for tab, p_key in zip(tabs, keys_list):
    with tab:
        p_info = st.session_state.product_store[p_key]
        p_inv = inventory_params[p_key]
        
        last_recorded_month = p_info["labels"][-1]
        input_month_label = get_next_month_label(last_recorded_month)
        forecast_month_label = get_next_month_label(input_month_label)

        st.markdown(f'<div class="product-header">📦 ผลิตภัณฑ์: {p_info["name"]}</div>', unsafe_allow_html=True)
        
        c_badge, c_popover = st.columns([3.5, 1])
        with c_badge:
            policy_desc = f"🎯 นโยบายที่เหมาะสมที่สุด: <strong>{p_inv['policy']}</strong> " + \
                          (f"(สั่งครั้งละ <strong>{p_inv['selected_lot']} ลิตร</strong>)" if p_inv['policy']=='EOQ' else f"(รอบการสั่งซื้อ <strong>k = {p_inv['k']} เดือน</strong>)")
            st.markdown(f'<div class="policy-tag">{policy_desc}</div>', unsafe_allow_html=True)
        with c_popover:
            with st.popover("💡 เหตุผลการเลือกนโยบาย"):
                st.markdown(f"{p_inv['rationale']}")

        if f"success_msg_{p_key}" in st.session_state:
            st.success(st.session_state[f"success_msg_{p_key}"])
            del st.session_state[f"success_msg_{p_key}"]

        c_input, c_results = st.columns([1.1, 1.9])
        
        with c_input:
            st.markdown(f'<div class="large-label">1. ปริมาณการใช้งานของเดือนปัจจุบันนี้ ({input_month_label}) (ลิตร):</div>', unsafe_allow_html=True)
            last_usage = st.number_input(
                label="ปริมาณการใช้งานของเดือนปัจจุบันนี้",
                label_visibility="collapsed", min_value=0.0, value=None, step=1.0, key=f"usage_{p_key}"
            )
            
            st.markdown('<div class="large-label">2. ปริมาณคงเหลือ ณ ปัจจุบัน (ลิตร):</div>', unsafe_allow_html=True)
            stock_qty_input = st.number_input(
                label="ปริมาณคงเหลือ ณ ปัจจุบัน",
                label_visibility="collapsed", min_value=0.0, value=None, step=1.0, key=f"stock_{p_key}"
            )

        if last_usage is not None and stock_qty_input is not None:
            y_data = p_info["history"] + [last_usage]
            current_labels = p_info["labels"] + [input_month_label]

            Level, Trend, Season, Forecast, next_f = run_holt_winters(
                y_data, p_info["alpha"], p_info["beta"], p_info["gamma"]
            )

            error_val = next_f * 0.01

            if p_inv["policy"] == "EOQ":
                recommended_qty = p_inv["selected_lot"] if stock_qty_input <= p_inv["rop"] else 0
            else:
                needed_for_k_months = next_f * p_inv["k"]
                net_needed = needed_for_k_months - stock_qty_input
                recommended_qty = math.ceil(net_needed / 10.0) * 10 if net_needed > 0 else 0

            lead_days = p_inv["lead_time_days"]
            expected_arrival = datetime.now() + timedelta(days=lead_days)
            arrival_str = expected_arrival.strftime("%d/%m/%Y")
            
            fc_info_msg = f"\n\n📊 **ยอดพยากรณ์การใช้ ({forecast_month_label}):** {next_f:.2f} ลิตร"
            lead_info_msg = f"\n⏱️ **ระยะเวลาจัดส่งโดยประมาณ:** {lead_days} วัน (คาดว่าจะได้รับสินค้าภายในวันที่ **{arrival_str}**)"

            with c_input:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                if stock_qty_input <= p_inv["ss"]:
                    st.error(f"🚨 **สถานะวิกฤต (Below Safety Stock):** สต็อกคงเหลือ ({stock_qty_input:.2f} ลิตร) ต่ำกว่าระดับความปลอดภัย SS ({p_inv['ss']} ลิตร){fc_info_msg}{lead_info_msg}")
                elif stock_qty_input <= p_inv["rop"]:
                    st.warning(f"⚠️ **เตือนจุดสั่งซื้อ (Reorder Point):** สต็อกคงเหลือ ({stock_qty_input:.2f} ลิตร) แตะจุดสั่งซื้อ ROP ({p_inv['rop']} ลิตร) แล้ว{fc_info_msg}{lead_info_msg}")
                else:
                    st.success(f"✅ **สถานะปกติ:** สต็อกคงเหลือ ({stock_qty_input:.2f} ลิตร) สูงกว่าจุดสั่งซื้อ ROP ({p_inv['rop']} ลิตร){fc_info_msg}{lead_info_msg}")

            tank_rows, est_cost = get_tank_rows_and_cost(p_key, recommended_qty)
            if tank_rows:
                table_html_rows = "".join([f"<tr><td>{size}</td><td class='qty-col'>{qty}</td></tr>" for size, qty in tank_rows])
                tanks_display_html = f"""
                <table class="tank-table">
                    <thead><tr><th>ขนาดถัง</th><th style="text-align:right;">จำนวนสั่ง</th></tr></thead>
                    <tbody>{table_html_rows}</tbody>
                </table>
                <div style="margin-top: 10px; padding-top: 6px; border-top: 2px dashed #93c5fd; font-size: 15px; font-weight: 800; color: #1e3a8a;">
                    💳 รวมประมาณการค่าใช้จ่าย: <span style="color:#16a34a; font-size:19px;">{est_cost:,.2f}</span> บาท
                </div>
                """
            else:
                tanks_display_html = f"""
                <div style='font-size:20px; font-weight:800; color:#1e40af; margin-top:6px;'>ไม่ต้องสั่งซื้อ</div>
                <div style='font-size:14px; font-weight:600; color:#1e3a8a; margin-top:8px; background:#dbeafe; padding:6px 10px; border-radius:8px;'>
                    📈 ยอดพยากรณ์การใช้ ({forecast_month_label}): <b>{next_f:.2f} ลิตร</b>
                </div>
                """

            with c_results:
                st.info(f"💡 **สรุปผลพยากรณ์:** คาดการณ์ปริมาณการใช้น้ำยาในเดือน **{forecast_month_label}** เท่ากับ **{next_f:.2f} ลิตร** " + 
                        (f"(แนะนำสั่งซื้อ **{recommended_qty} ลิตร**)" if recommended_qty > 0 else f"(แนะนำ **สั่งซื้อ 0 ลิตร**)"))

                st.markdown(f'<div class="large-label">📌 สรุปผลพยากรณ์ประจำเดือน: <span style="color:#2563eb;">{forecast_month_label}</span></div>', unsafe_allow_html=True)
                
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown(f'<div class="card-recommend"><div class="card-recommend-title">1. ปริมาณสั่งซื้อแนะนำ ({p_inv["policy"]})</div><div class="card-recommend-value">{recommended_qty} <small style="font-size:18px">ลิตร</small></div></div>', unsafe_allow_html=True)
                with r2:
                    st.markdown(f'<div class="card-tanks"><div class="card-tanks-title">2. จำนวนถังที่ต้องสั่งซื้อ</div>{tanks_display_html}</div>', unsafe_allow_html=True)

                r3, r4 = st.columns(2)
                with r3:
                    st.markdown(f'<div class="card-base"><div class="card-title">3. ผลการพยากรณ์ ({forecast_month_label})</div><div class="card-value" style="color:#2563eb;">{next_f:.2f} <small style="font-size:16px">ลิตร</small></div></div>', unsafe_allow_html=True)
                with r4:
                    st.markdown(f'<div class="card-base"><div class="card-title">4. ค่าความคลาดเคลื่อน</div><div style="font-size: 17px; font-weight: 800; color: #16a34a; margin-top: 4px;">คลาดเคลื่อน (+): +{error_val:.2f} ลิตร</div><div style="font-size: 17px; font-weight: 800; color: #dc2626; margin-top: 2px;">คลาดเคลื่อน (-): -{error_val:.2f} ลิตร</div></div>', unsafe_allow_html=True)

                st.markdown("---")
                st.button(
                    f"🟢 บันทึกยอด {input_month_label} และร่นไปคำนวณเดือน {forecast_month_label} ➔", 
                    key=f"btn_save_{p_key}", type="primary", use_container_width=True,
                    on_click=cb_save_data, args=(p_key, last_usage, input_month_label)
                )

        st.markdown("---")
        if last_usage is not None and stock_qty_input is not None:
            st.subheader(f"📈 กราฟแสดงแนวโน้มประวัติการใช้งานและการพยากรณ์ ({forecast_month_label})")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=current_labels, y=y_data, mode='lines+markers', name='ยอดใช้จริง (Actual)', line=dict(color='#0f172a', width=3)))
            fig.add_trace(go.Scatter(x=current_labels[12:], y=Forecast[12:], mode='lines+markers', name='HW-Forecast', line=dict(color='#2563eb', width=2, dash='dash')))
            fig.add_trace(go.Scatter(x=[forecast_month_label], y=[next_f], mode='markers+text', name=f'พยากรณ์ {next_f:.2f}L', marker=dict(color='#16a34a', size=14, symbol='star'), text=[f"{next_f:.2f} ลิตร"], textposition="top center"))
            fig.update_layout(xaxis_title="เดือน/ปี", yaxis_title="ปริมาณการใช้ (ลิตร)", hovermode="x unified", template="plotly_white", height=380, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)


# --- 12. ส่วนสรุปการเปรียบเทียบต้นทุนแยกรายน้ำยา (ตามคำขอใหม่) ---
st.markdown("<br><hr style='border: 2px solid #cbd5e1;'><br>", unsafe_allow_html=True)
st.markdown('<div class="product-header">📊 สรุปการเปรียบเทียบต้นทุนแยกตามชนิดน้ำยา (Individual Product Cost Analysis)</div>', unsafe_allow_html=True)
st.caption("เปรียบเทียบต้นทุนรวมของการจัดการสินค้าคงคลังทั้ง 3 วิธีแยกตามชนิดน้ำยา พร้อมวิเคราะห์ความประหยัดของนโยบายที่เลือก")

# สร้าง Card แสดงแยกแต่ละผลิตภัณฑ์
for p_key, p_info in default_products.items():
    inv = inventory_params[p_key]
    
    # คำนวณค่านิยมประหยัดเมื่อเทียบกับ EOQ หรือ Forecast
    poq_cls = "cost-winner" if inv["policy"] == "POQ" else "cost-normal"
    eoq_cls = "cost-winner" if inv["policy"] == "EOQ" else "cost-normal"
    fc_cls = "cost-normal"
    
    st.markdown(f"""
        <div class="prod-cost-card">
            <div class="prod-cost-title">{p_info['name']} <span style="font-size:15px; font-weight:600; color:#64748b;">(ราคา {inv['price_per_liter']} บาท/ลิตร | ความต้องการเฉลี่ย {inv['d_avg']:.2f} ลิตร/เดือน)</span></div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 12px;">
                <div class="cost-box {poq_cls}">
                    <div class="cost-box-title">นโยบาย POQ {'🏆 (เลือกใช้)' if inv['policy']=='POQ' else ''}</div>
                    <div class="cost-box-val">{inv['poq_cost']:,.2f} บาท</div>
                </div>
                <div class="cost-box {eoq_cls}">
                    <div class="cost-box-title">นโยบาย EOQ {'🏆 (เลือกใช้)' if inv['policy']=='EOQ' else ''}</div>
                    <div class="cost-box-val">{inv['eoq_cost']:,.2f} บาท</div>
                </div>
                <div class="cost-box {fc_cls}">
                    <div class="cost-box-title">สั่งตามพยากรณ์ (Forecast)</div>
                    <div class="cost-box-val">{inv['fc_cost']:,.2f} บาท</div>
                </div>
            </div>
            <div style="background-color: #f1f5f9; padding: 12px 16px; border-radius: 10px; font-size: 15px; color: #334155;">
                {inv['rationale']}
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 13. ช่องสรุปภาพรวมคำตอบ (Summary Highlight Box) ---
total_eoq_all = sum(v["eoq_cost"] for v in inventory_params.values())
total_hybrid_best = sum(v["best_cost"] for v in inventory_params.values())
total_savings = total_eoq_all - total_hybrid_best

st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a); color: #ffffff; padding: 25px; border-radius: 18px; margin-top: 10px;">
        <h3 style="color: #38bdf8; margin-top:0; font-size:22px; font-weight:800;">📌 ช่องสรุปเปรียบเทียบ: ทำไมการเลือกใช้ Hybrid Policy ถึงถูกที่สุด?</h3>
        <p style="font-size: 16px; line-height: 1.7; color: #e2e8f0;">
            จากการวิเคราะห์ลักษณะอุปสงค์และค่าใช้จ่ายของน้ำยาแต่ละชนิด การใช้ <strong>นโยบายผสม (Hybrid Policy)</strong> โดยเลือกใช้ 
            <span style="color:#4ade80; font-weight:bold;">EOQ สำหรับน้ำยาล้างรถ</span> และใช้ 
            <span style="color:#38bdf8; font-weight:bold;">POQ สำหรับน้ำยาเคลือบภายใน, น้ำยาเช็ดกระจก และน้ำยาลงล้อ</span> 
            ให้ผลลัพธ์การประหยัดต้นทุนรวมดีที่สุดด้วยเหตุผลดังนี้:
        </p>
        <ul style="font-size: 15px; line-height: 1.8; color: #cbd5e1; margin-left: -10px;">
            <li><strong>น้ำยาล้างรถ (ใช้ EOQ):</strong> เป็นสินค้าที่ใช้เยอะต่อเนื่อง สั่งล็อตใหญ่ทีเดียวคุ้มค่าสั่งซื้อ ประหยัดกว่าการสั่งตามพยากรณ์รายเดือน <strong>4,395 บาท</strong></li>
            <li><strong>น้ำยาเคลือบภายใน & น้ำยาเช็ดกระจก (ใช้ POQ k=1):</strong> เป็นสินค้าที่มีความผันผวนและราคาสูง การสั่งรวบรายเดือนช่วยลดการถือครองคลังสินค้า ประหยัดกว่า EOQ ถึง <strong>4,222.50 บาท และ 3,846 บาท</strong> ตามลำดับ</li>
            <li><strong>น้ำยาลงล้อ (ใช้ POQ k=3):</strong> เป็นสินค้าที่ใช้น้อย นานๆ สั่งที การสั่งรวบทุก 3 เดือนช่วยประหยัดค่าดำเนินการจัดสั่งซื้อ ประหยัดกว่า EOQ ถึง <strong>1,996.50 บาท</strong></li>
        </ul>
        <div style="display: flex; gap: 20px; margin-top: 20px; border-top: 1px solid #334155; padding-top: 15px;">
            <div>
                <span style="font-size: 14px; color: #94a3b8;">ต้นทุนรวมนโยบาย Hybrid:</span><br>
                <span style="font-size: 28px; font-weight: 900; color: #4ade80;">""" + f"{total_hybrid_best:,.2f}" + """ บาท</span>
            </div>
            <div style="border-left: 1px solid #334155; padding-left: 20px;">
                <span style="font-size: 14px; color: #94a3b8;">ประหยัดได้รวมทั้งหมด (เมื่อเทียบกับ EOQ):</span><br>
                <span style="font-size: 28px; font-weight: 900; color: #38bdf8;">""" + f"ประหยัดได้ {total_savings:,.2f}" + """ บาท</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
