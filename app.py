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

    /* Tabs Styling (สำหรับ 4 สินค้า) */
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

# --- 4. ข้อมูลพารามิเตอร์โมเดลคลังสินค้า พร้อมราคา Lead Time และเหตุผลเชิงวิเคราะห์ ---
inventory_params = {
    "carwash": {
        "policy": "EOQ", "k": 1, "d_avg": 43.07, "h": 1.50, "eoq": 33.89, "ss": 9.35, "rop": 12.94,
        "selected_lot": 40, "poq_cost": 16236.66, "eoq_cost": 13506.66, "fc_cost": 17901.66, "best_cost": 13506.66,
        "lead_time_days": 2.5, "vc": 0.37,
        "tank_prices": {30: 1350, 20: 900},
        "rationale": "**ประหยัดต้นทุนรวมได้สูงสุด** (ลดลง 4,395.00 บาท/ปี เมื่อเทียบกับการสั่งตามพยากรณ์) เนื่องจากเป็นสินค้าที่มีความผันผวนอุปสงค์ต่ำ ($VC = 0.37 \\le 0.5$) การสั่งซื้อตามขนาดประหยัด EOQ ล็อตละ 40 ลิตร ช่วยลดต้นทุนการสั่งซื้อได้อย่างมีประสิทธิภาพที่สุด"
    },
    "interior": {
        "policy": "POQ", "k": 1, "d_avg": 20.03, "h": 1.50, "eoq": 23.11, "ss": 3.71, "rop": 5.38,
        "selected_lot": 30, "poq_cost": 7093.70, "eoq_cost": 11316.20, "fc_cost": 9474.95, "best_cost": 7093.70,
        "lead_time_days": 2.5, "vc": 0.48,
        "tank_prices": {30: 1800, 20: 1200, 10: 600},
        "rationale": "**ประหยัดต้นทุนรวมได้สูงสุด** (ลดลง 4,222.50 บาท/ปี เมื่อเทียบกับ EOQ) เหมาะกับสินค้าที่มีความผันผวนอุปสงค์ปานกลาง ($VC = 0.48$) นโยบาย POQ ($k=1$) ช่วยควบคุมระดับคลังสินค้าไม่ให้สะสมเกินความจำเป็น"
    },
    "glass": {
        "policy": "POQ", "k": 1, "d_avg": 13.35, "h": 2.00, "eoq": 16.34, "ss": 2.21, "rop": 3.32,
        "selected_lot": 20, "poq_cost": 6175.13, "eoq_cost": 10021.13, "fc_cost": 9654.88, "best_cost": 6175.13,
        "lead_time_days": 2.0, "vc": 0.52,
        "tank_prices": {30: 1500, 20: 1000, 10: 500},
        "rationale": "**ประหยัดต้นทุนรวมได้สูงสุด** (ลดลง 3,846.00 บาท/ปี เมื่อเทียบกับ EOQ) เนื่องจากอัตราค่าการถือครองคลังสินค้า ($h=2.00$) สูง นโยบาย POQ ($k=1$) จึงช่วยลดปริมาณสินค้าคลังเฉลี่ยลงได้อย่างมีนัยสำคัญ"
    },
    "wheel": {
        "policy": "POQ", "k": 3, "d_avg": 2.76, "h": 1.50, "eoq": 8.58, "ss": 0.44, "rop": 0.67,
        "selected_lot": 10, "poq_cost": 2066.39, "eoq_cost": 4062.89, "fc_cost": 4062.89, "best_cost": 2066.39,
        "lead_time_days": 3.0, "vc": 0.65,
        "tank_prices": {30: 2400, 20: 1600, 10: 800},
        "rationale": "**ประหยัดต้นทุนรวมได้สูงสุด** (ลดลง 1,996.50 บาท/ปี เมื่อเทียบกับ EOQ) เนื่องจากเป็นสินค้าที่มีปริมาณความต้องการต่ำและผันผวน ($VC = 0.65$) การรวบงวดสั่งซื้อแบบ POQ ($k=3$) ช่วยประหยัดค่าสั่งซื้อได้อย่างคุ้มค่า"
    }
}

# --- 5. ค่าตั้งต้นประวัติ 35 เดือน (ม.ค. 66 - พ.ย. 68) ---
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

# --- 8. Sidebar จัดการรีเซ็ตแยกหมวดหมู่ ---
with st.sidebar:
    st.header("⚙️ ระบบควบคุมแอป")
    
    # --- หมวดที่ 1: ปริมาณใช้งาน ---
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

    # --- หมวดที่ 2: ปริมาณคงเหลือ ---
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

    # --- หมวดที่ 3: รีเซ็ตข้อมูลทั้งหมด & รีบูท ---
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

# --- 9. ฟังก์ชันคำนวณ Holt-Winters Multiplicative ---
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

# --- 10. ฟังก์ชันคำนวณแยกประเภทถัง และยอดประมาณการค่าใช้จ่าย ---
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
        
        # --- Badge นโยบาย + Popover ---
        c_badge, c_popover = st.columns([3.5, 1])
        with c_badge:
            policy_desc = f"🎯 นโยบายที่เหมาะสมที่สุด: <strong>{p_inv['policy']}</strong> " + \
                          (f"(สั่งครั้งละ <strong>{p_inv['selected_lot']} ลิตร</strong>)" if p_inv['policy']=='EOQ' else f"(รอบการสั่งซื้อ <strong>k = {p_inv['k']} เดือน</strong>)")
            st.markdown(f'<div class="policy-tag">{policy_desc}</div>', unsafe_allow_html=True)
        with c_popover:
            with st.popover("💡 เหตุผลการเลือกนโยบาย"):
                st.markdown(f"**เหตุผลประกอบการตัดสินใจเชิงวิเคราะห์:**\n\n{p_inv['rationale']}")

        if f"success_msg_{p_key}" in st.session_state:
            st.success(st.session_state[f"success_msg_{p_key}"])
            del st.session_state[f"success_msg_{p_key}"]

        c_input, c_results = st.columns([1.1, 1.9])
        
        with c_input:
            st.markdown(f'<div class="large-label">1. ปริมาณการใช้งานของเดือนปัจจุบันนี้ ({input_month_label}) (ลิตร):</div>', unsafe_allow_html=True)
            last_usage = st.number_input(
                label="ปริมาณการใช้งานของเดือนปัจจุบันนี้",
                label_visibility="collapsed",
                min_value=0.0,
                value=None,
                step=1.0,
                key=f"usage_{p_key}"
            )
            
            st.markdown('<div class="large-label">2. ปริมาณคงเหลือ ณ ปัจจุบัน (ลิตร):</div>', unsafe_allow_html=True)
            stock_qty_input = st.number_input(
                label="ปริมาณคงเหลือ ณ ปัจจุบัน",
                label_visibility="collapsed",
                min_value=0.0,
                value=None,
                step=1.0,
                key=f"stock_{p_key}"
            )

        # คำนวณเมื่อกรอกข้อมูลครบ
        if last_usage is not None and stock_qty_input is not None:
            
            y_data = p_info["history"] + [last_usage]
            current_labels = p_info["labels"] + [input_month_label]

            Level, Trend, Season, Forecast, next_f = run_holt_winters(
                y_data, p_info["alpha"], p_info["beta"], p_info["gamma"]
            )

            error_val = next_f * 0.01

            # คำนวณปริมาณสั่งซื้อตามนโยบาย
            if p_inv["policy"] == "EOQ":
                if stock_qty_input <= p_inv["rop"]:
                    recommended_qty = p_inv["selected_lot"]
                else:
                    recommended_qty = 0
            else:
                needed_for_k_months = next_f * p_inv["k"]
                net_needed = needed_for_k_months - stock_qty_input
                if net_needed > 0:
                    recommended_qty = math.ceil(net_needed / 10.0) * 10
                else:
                    recommended_qty = 0

            # แสดงการแจ้งเตือน ROP & Safety Stock พร้อมระบุยอดพยากรณ์
            lead_days = p_inv["lead_time_days"]
            expected_arrival = datetime.now() + timedelta(days=lead_days)
            arrival_str = expected_arrival.strftime("%d/%m/%Y")
            
            fc_info_msg = f"\n\n📊 **ยอดพยากรณ์การใช้ ({forecast_month_label}):** {next_f:.2f} ลิตร"
            lead_info_msg = f"\n⏱️ **ระยะเวลาจัดส่งโดยประมาณ:** {lead_days} วัน (คาดว่าจะได้รับสินค้าภายในวันที่ **{arrival_str}**)"

            with c_input:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                if stock_qty_input <= p_inv["ss"]:
                    st.error(f"🚨 **สถานะวิกฤต (Below Safety Stock):** สต็อกคงเหลือ ({stock_qty_input:.2f} ลิตร) ต่ำกว่าระดับความปลอดภัย SS ({p_inv['ss']} ลิตร) เสี่ยงสินค้าขาดมือ!{fc_info_msg}{lead_info_msg}")
                elif stock_qty_input <= p_inv["rop"]:
                    st.warning(f"⚠️ **เตือนจุดสั่งซื้อ (Reorder Point):** สต็อกคงเหลือ ({stock_qty_input:.2f} ลิตร) แตะจุดสั่งซื้อ ROP ({p_inv['rop']} ลิตร) แล้ว ควรเริ่มดำเนินสั่งซื้อ!{fc_info_msg}{lead_info_msg}")
                else:
                    st.success(f"✅ **สถานะปกติ:** สต็อกคงเหลือ ({stock_qty_input:.2f} ลิตร) สูงกว่าจุดสั่งซื้อ ROP ({p_inv['rop']} ลิตร) เพียงพอสำหรับใช้งาน{fc_info_msg}{lead_info_msg}")

            # คำนวณถังและยอดประมาณการค่าใช้จ่าย
            tank_rows, est_cost = get_tank_rows_and_cost(p_key, recommended_qty)
            if tank_rows:
                table_html_rows = "".join([
                    f"<tr><td>{size}</td><td class='qty-col'>{qty}</td></tr>" 
                    for size, qty in tank_rows
                ])
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

            # แสดงผลการคำนวณฝั่งขวา
            with c_results:
                # Banner สรุปยอดพยากรณ์ชัดเจน
                st.info(f"💡 **สรุปผลพยากรณ์:** คาดการณ์ปริมาณการใช้น้ำยาในเดือน **{forecast_month_label}** เท่ากับ **{next_f:.2f} ลิตร** " + 
                        (f"(แนะนำสั่งซื้อ **{recommended_qty} ลิตร**)" if recommended_qty > 0 else f"(สต็อกคงเหลือ {stock_qty_input:.2f} ลิตร ยังเพียงพอ จึงแนะนำ **สั่งซื้อ 0 ลิตร**)"))

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
                    key=f"btn_save_{p_key}", 
                    type="primary", 
                    use_container_width=True,
                    on_click=cb_save_data,
                    args=(p_key, last_usage, input_month_label)
                )

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
                st.markdown(f'<div style="background-color: #fefce8; border: 2px dashed #eab308; border-radius: 14px; padding: 35px 20px; text-align: center; margin-top: 10px;"><div style="font-size: 45px; margin-bottom: 10px;">📝</div><div style="font-size: 24px; font-weight: 800; color: #854d0e;">กรุณากรอกข้อมูลให้ครบทั้ง 2 ช่อง</div><div style="font-size: 19px; color: #a16207; margin-top: 10px; line-height: 1.6;">1. ปริมาณการใช้งานของเดือนปัจจุบันนี้ <strong>({input_month_label})</strong><br>2. ปริมาณคงเหลือ ณ ปัจจุบัน<br><br><strong style="color: #854d0e;">⚡ เมื่อกรอกครบแล้ว ระบบจะคำนวณผลพยากรณ์สำหรับเดือน ({forecast_month_label}) ให้ทันที</strong></div></div>', unsafe_allow_html=True)

# --- 12. ส่วนสรุปเปรียบเทียบต้นทุนรวม ---
st.markdown("<br><hr style='border: 2px solid #cbd5e1;'><br>", unsafe_allow_html=True)
st.markdown('<div class="product-header">📊 ตารางสรุปการเปรียบเทียบต้นทุนรวมการจัดการสินค้าคงคลัง</div>', unsafe_allow_html=True)
st.caption("การเปรียบเทียบต้นทุนรวม (Total Inventory Cost) 3 วิธี เพื่อเลือกใช้นโยบายที่เหมาะสมที่สุด (Hybrid Policy)")

summary_data = []
for k_p, v_info in default_products.items():
    inv = inventory_params[k_p]
    summary_data.append({
        "รายการสินค้า": v_info["name"],
        "ความต้องการเฉลี่ย (D)": f"{inv['d_avg']:.2f}",
        "จุดสั่งซื้อใหม่ (ROP)": f"{inv['rop']:.2f}",
        "สินค้าคงคลังสำรอง (SS)": f"{inv['ss']:.2f}",
        "นโยบาย POQ (บาท)": f"{inv['poq_cost']:,.2f}",
        "แนวทางปฏิบัติ EOQ (บาท)": f"{inv['eoq_cost']:,.2f}",
        "สั่งตามพยากรณ์ (บาท)": f"{inv['fc_cost']:,.2f}",
        "นโยบายที่เลือกใช้": f"<b>{inv['policy']}</b> (สั่งซื้อครั้งละ {inv['selected_lot']} ลิตร)" if inv['policy']=='EOQ' else f"<b>{inv['policy']}</b> (k={inv['k']})",
        "ต้นทุนรวมต่ำสุด (บาท)": f"<b>{inv['best_cost']:,.2f}</b>"
    })

df_summary = pd.DataFrame(summary_data)
st.write(df_summary.to_html(escape=False, index=False), unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

total_eoq_all = sum(v["eoq_cost"] for v in inventory_params.values())
total_hybrid_best = sum(v["best_cost"] for v in inventory_params.values())
total_savings = total_eoq_all - total_hybrid_best

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown(f"""
        <div style="background-color: #f0fdf4; border: 2px solid #16a34a; padding: 20px; border-radius: 14px;">
            <div style="font-size: 18px; color: #15803d; font-weight: 800;">💰 ต้นทุนรวมนโยบายแบบ Hybrid (เลือกวิธีที่ดีที่สุด)</div>
            <div style="font-size: 32px; color: #16a34a; font-weight: 900; margin-top: 5px;">{total_hybrid_best:,.2f} บาท</div>
        </div>
    """, unsafe_allow_html=True)
with col_s2:
    st.markdown(f"""
        <div style="background-color: #eff6ff; border: 2px solid #2563eb; padding: 20px; border-radius: 14px;">
            <div style="font-size: 18px; color: #1d4ed8; font-weight: 800;">🎉 ยอดประหยัดได้รวม (เมื่อเทียบกับ EOQ ทั้งหมด)</div>
            <div style="font-size: 32px; color: #2563eb; font-weight: 900; margin-top: 5px;">ประหยัดได้ {total_savings:,.2f} บาท</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📈 กราฟเปรียบเทียบต้นทุนรวมของทั้ง 3 นโยบาย")

categories = [v["name"] for v in default_products.values()]
poq_costs = [v["poq_cost"] for v in inventory_params.values()]
eoq_costs = [v["eoq_cost"] for v in inventory_params.values()]
fc_costs = [v["fc_cost"] for v in inventory_params.values()]

fig_cost = go.Figure()
fig_cost.add_trace(go.Bar(x=categories, y=poq_costs, name='นโยบาย POQ', marker_color='#3b82f6'))
fig_cost.add_trace(go.Bar(x=categories, y=eoq_costs, name='นโยบาย EOQ', marker_color='#f59e0b'))
fig_cost.add_trace(go.Bar(x=categories, y=fc_costs, name='สั่งตามพยากรณ์', marker_color='#ef4444'))

fig_cost.update_layout(
    barmode='group',
    xaxis_title="รายการสินค้า",
    yaxis_title="ต้นทุนรวม (บาท)",
    template="plotly_white",
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_cost, use_container_width=True)
