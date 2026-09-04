import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
import copy
from datetime import datetime, timedelta

# --- 1. การตั้งค่าหน้าจอและ CSS ตกแต่งสไตล์ Gen Z Pastel Aesthetic ---
st.set_page_config(
    page_title="ระบบพยากรณ์และบริหารการสั่งซื้อสุดคิวท์ ✨", 
    page_icon="🎀", 
    layout="wide"
)

st.markdown("""
    <style>
    /* Google Fonts - Cute & Modern Thai Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@400;600;700;800&family=Mali:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Prompt', 'Mali', sans-serif;
    }
    
    /* Background พาสเทลละมุนตา */
    .main { 
        background: linear-gradient(135deg, #fff5f8 0%, #f3e8ff 50%, #e0f2fe 100%); 
    }
    
    /* Gen Z Hero Banner Header Style */
    .hero-banner {
        background: linear-gradient(135deg, #ff85a1 0%, #a855f7 50%, #6366f1 100%);
        border-radius: 28px;
        padding: 24px 30px;
        color: #ffffff;
        box-shadow: 0 12px 30px -6px rgba(236, 72, 153, 0.35);
        margin-bottom: 22px;
        position: relative;
        overflow: hidden;
        border: 3px solid #ffffff;
    }
    .hero-container {
        display: flex;
        align-items: center;
        gap: 18px;
    }
    .hero-icon-box {
        background: #ffffff;
        padding: 14px;
        border-radius: 24px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        flex-shrink: 0;
    }
    .hero-title {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #ffffff;
        margin: 0;
        line-height: 1.25;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .hero-subtitle {
        font-size: 14px !important;
        color: #f3e8ff;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(8px);
        color: #ffffff;
        border: 1.5px solid rgba(255, 255, 255, 0.5);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Input Container Card คิวท์ๆ */
    .input-card-container {
        background: #ffffff;
        border-radius: 24px;
        padding: 22px;
        border: 3px solid #fbcfe8;
        box-shadow: 0 8px 20px rgba(244, 114, 182, 0.08);
        margin-bottom: 16px;
    }
    .input-card-header {
        font-size: 18px;
        font-weight: 800;
        color: #831843;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 2px dashed #fbcfe8;
        padding-bottom: 10px;
    }

    /* Tabs Styling สไตล์ปุ่มแคปซูลพาสเทล */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 10px; 
        overflow-x: auto;
        padding-bottom: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 52px;
        white-space: nowrap;
        background-color: #ffffff;
        border-radius: 20px;
        border: 2px solid #e9d5ff;
        padding: 8px 22px;
        font-weight: 700;
        font-size: 16px !important;
        color: #6b21a8;
        box-shadow: 0 4px 10px rgba(168, 85, 247, 0.05);
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #c084fc 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        border-color: #a855f7 !important;
        box-shadow: 0 6px 18px rgba(168, 85, 247, 0.35) !important;
    }

    .product-header {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #4c1d95;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Number Input Styling ละมุนน่าพิมพ์ */
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { 
        -webkit-appearance: none; 
        margin: 0; 
    }
    input[type=number] { 
        -moz-appearance: textfield; 
        font-size: 22px !important;
        font-weight: bold !important;
        height: 52px !important;
        color: #4c1d95 !important;
        background-color: #fcf6ff !important;
        border: 2px solid #d8b4fe !important;
        border-radius: 16px !important;
        transition: all 0.2s ease;
    }
    input[type=number]:focus {
        border-color: #a855f7 !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 0 4px rgba(168, 85, 247, 0.15) !important;
    }
    div[data-testid="stNumberInputStepDown"], div[data-testid="stNumberInputStepUp"] {
        display: none !important;
    }
    
    .large-label {
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #581c87;
        margin-top: 8px;
        margin-bottom: 6px;
    }

    /* Cards Status สไตล์แคนดี้พาสเทล */
    .card-base {
        background: #ffffff;
        padding: 18px;
        border-radius: 20px;
        border: 2px solid #e9d5ff;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.03);
        margin-bottom: 12px;
        min-height: 135px;
    }
    .card-title { font-size: 14px; color: #7e22ce; font-weight: 700; display: flex; align-items: center; gap: 6px; }
    .card-value { font-size: 26px; color: #581c87; font-weight: 800; margin-top: 6px; }
    
    .card-recommend {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        padding: 20px;
        border-radius: 20px;
        border: 2.5px solid #4ade80;
        box-shadow: 0 8px 20px rgba(74, 222, 128, 0.2);
        margin-bottom: 12px;
        min-height: 135px;
    }
    .card-recommend-title { font-size: 15px; color: #14532d; font-weight: 800; display: flex; align-items: center; gap: 6px; }
    .card-recommend-value { font-size: 32px; color: #15803d; font-weight: 900; margin-top: 4px; }

    .card-tanks {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        padding: 18px;
        border-radius: 20px;
        border: 2.5px solid #38bdf8;
        box-shadow: 0 8px 20px rgba(56, 189, 248, 0.2);
        margin-bottom: 12px;
        min-height: 135px;
    }
    .card-tanks-title { font-size: 15px; color: #0c4a6e; font-weight: 800; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }

    .tank-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 5px;
    }
    .tank-table th {
        border-bottom: 2px solid #7dd3fc;
        padding: 4px 6px;
        font-size: 13px;
        font-weight: 700;
        color: #0369a1;
        text-align: left;
    }
    .tank-table td {
        padding: 4px 6px;
        font-size: 15px;
        font-weight: 800;
        color: #0c4a6e;
    }
    .tank-table td.qty-col {
        text-align: right;
        color: #0284c7;
        font-size: 17px;
    }

    .policy-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, #fbcfe8 0%, #f472b6 100%);
        color: #831843;
        padding: 8px 18px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 14px;
        border: 2px solid #ffffff;
        box-shadow: 0 4px 12px rgba(244, 114, 182, 0.25);
    }

    /* Yellow Notice Empty State Card กรอบเหลืองครีมน่ารัก */
    .empty-state-card {
        background: linear-gradient(135deg, #fef9c3 0%, #fef08a 100%);
        border: 3px dashed #facc15;
        border-radius: 24px;
        padding: 30px 20px;
        text-align: center;
        margin-top: 4px;
        box-shadow: 0 8px 25px rgba(250, 204, 21, 0.15);
    }
    .empty-state-icon {
        font-size: 46px;
        margin-bottom: 6px;
    }
    .empty-state-title {
        font-size: 20px;
        font-weight: 800;
        color: #713f12;
        margin-bottom: 8px;
    }
    .empty-state-desc {
        font-size: 15px;
        font-weight: 700;
        color: #854d0e;
        line-height: 1.7;
    }
    .empty-state-highlight {
        margin-top: 14px;
        font-size: 14px;
        font-weight: 800;
        color: #a16207;
        background: #ffffff;
        padding: 8px 18px;
        border-radius: 20px;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    }

    /* Product Cost Card Inside Tab */
    .prod-cost-card {
        background: #ffffff;
        border: 2px solid #f3e8ff;
        border-radius: 24px;
        padding: 22px;
        margin-top: 24px;
        margin-bottom: 15px;
        box-shadow: 0 8px 20px rgba(168, 85, 247, 0.05);
    }
    .prod-cost-title {
        font-size: 18px;
        font-weight: 800;
        color: #581c87;
        margin-bottom: 14px;
        border-bottom: 2px dashed #e9d5ff;
        padding-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .cost-box {
        padding: 14px;
        border-radius: 18px;
        text-align: center;
    }
    .cost-box-title { font-size: 13px; font-weight: 700; color: #6b21a8; }
    .cost-box-val { font-size: 20px; font-weight: 800; margin-top: 4px; }
    
    .cost-winner {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border: 2px solid #22c55e;
        box-shadow: 0 6px 15px rgba(34, 197, 94, 0.18);
    }
    .cost-winner .cost-box-title { color: #14532d; }
    .cost-winner .cost-box-val { color: #15803d; }
    
    .cost-normal {
        background-color: #faf5ff;
        border: 1.5px solid #e9d5ff;
    }
    .cost-normal .cost-box-val { color: #581c87; }

    /* ปุ่มพาสเทลน่ากด */
    .stButton>button {
        border-radius: 18px !important;
        font-weight: 800 !important;
        transition: all 0.2s ease !important;
    }

    /* 📱 MOBILE RESPONSIVE FIXES */
    @media (max-width: 768px) {
        .hero-banner {
            padding: 18px 16px !important;
            border-radius: 20px !important;
        }
        .hero-container {
            gap: 12px !important;
        }
        .hero-icon-box {
            padding: 10px !important;
            border-radius: 16px !important;
            font-size: 24px !important;
        }
        .hero-title {
            font-size: 18px !important;
        }
        .hero-subtitle {
            font-size: 12px !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 44px !important;
            padding: 6px 12px !important;
            font-size: 14px !important;
            border-radius: 14px !important;
        }

        .product-header {
            font-size: 18px !important;
        }

        .policy-tag {
            font-size: 12px !important;
            padding: 6px 14px !important;
            display: block !important;
            width: 100 !important;
            text-align: center !important;
            box-sizing: border-box !important;
        }

        input[type=number] {
            font-size: 18px !important;
            height: 46px !important;
        }
        
        .empty-state-card {
            padding: 20px 14px !important;
            border-radius: 18px !important;
        }
        .empty-state-title { font-size: 17px !important; }
        .empty-state-desc { font-size: 13px !important; }

        .cost-grid-mobile {
            grid-template-columns: 1fr !important;
            gap: 8px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. Gen Z Hero Banner Header ---
st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">✨ HYBRID INVENTORY & FORECAST ENGINE 💖</div>
        <div class="hero-container">
            <div class="hero-icon-box">🧋</div>
            <div>
                <h1 class="hero-title">ระบบพยากรณ์และบริหารการสั่งซื้อสุดคิวท์</h1>
                <p class="hero-subtitle">คำนวณแม่นยำด้วย Holt-Winters + โมเดล EOQ / POQ / ROP / SS น้าา 🌸</p>
            </div>
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
        "rationale": "<b>ทำไม EOQ ถึงประหยัดที่สุด? ✨</b> เนื่องจากน้ำยาล้างรถมีอุปสงค์สูงและค่อนข้างสม่ำเสมอ (VC = 0.37 ≤ 0.5) การสั่งซื้อแบบล็อตประหยัดขนาดคงที่ <b>EOQ (ครั้งละ 40 ลิตร)</b> จะช่วยถัวเฉลี่ยค่าสั่งซื้อและค่าถือครองคลังสินค้าได้สมดุลที่สุด <b>ประหยัดกว่าการสั่งตามพยากรณ์ 4,395.00 บาท/ปี</b> และ<b>ถูกกว่าวิธี POQ ถึง 2,730.00 บาท/ปี</b>"
    },
    "interior": {
        "policy": "POQ", "k": 1, "d_avg": 20.03, "h": 1.50, "eoq": 23.11, "ss": 3.71, "rop": 5.38,
        "selected_lot": 30, "poq_cost": 7093.70, "eoq_cost": 11316.20, "fc_cost": 9474.95, "best_cost": 7093.70,
        "lead_time_days": 2.5, "vc": 0.48,
        "price_per_liter": 30,
        "tank_prices": {30: 900, 20: 600, 10: 300},
        "rationale": "<b>ทำไม POQ (k=1) ถึงประหยัดที่สุด? ✨</b> สินค้ามีความผันผวนระดับปานกลาง (VC = 0.48) การใช้นโยบายรอบเวลาสั่งซื้อรายเดือน <b>POQ (k=1)</b> จะสั่งซื้อตามปริมาณที่คาดว่าต้องใช้จริงในแต่ละงวด ป้องกันไม่ให้มีสต็อกเหลือค้างคลังเกินจำเป็น <b>ประหยัดกว่าวิธี EOQ ถึง 4,222.50 บาท/ปี</b> และ<b>ถูกกว่าวิธีพยากรณ์ 2,381.25 บาท/ปี</b>"
    },
    "glass": {
        "policy": "POQ", "k": 1, "d_avg": 13.35, "h": 2.00, "eoq": 16.34, "ss": 2.21, "rop": 3.32,
        "selected_lot": 20, "poq_cost": 6175.13, "eoq_cost": 10021.13, "fc_cost": 9654.88, "best_cost": 6175.13,
        "lead_time_days": 2.0, "vc": 0.52,
        "price_per_liter": 40,
        "tank_prices": {30: 1200, 20: 800, 10: 400},
        "rationale": "<b>ทำไม POQ (k=1) ถึงประหยัดที่สุด? ✨</b> น้ำยาเช็ดกระจกมีราคาต่อหน่วยสูงกว่ากลุ่ม (40 บาท/ลิตร) และมีค่าถือครองสูง (h = 2.00 บาท) การใช้ <b>POQ (k=1)</b> ช่วยดึงระดับสต็อกเฉลี่ยลงมาให้ต่ำที่สุด จึงตัดค่าเก็บรักษาที่ไม่จำเป็นออกไปได้มหาศาล <b>ประหยัดกว่าวิธี EOQ ถึง 3,846.00 บาท/ปี</b> และ<b>ถูกกว่าวิธีพยากรณ์ 3,479.75 บาท/ปี</b>"
    },
    "wheel": {
        "policy": "POQ", "k": 3, "d_avg": 2.76, "h": 1.50, "eoq": 8.58, "ss": 0.44, "rop": 0.67,
        "selected_lot": 10, "poq_cost": 2066.39, "eoq_cost": 4062.89, "fc_cost": 4062.89, "best_cost": 2066.39,
        "lead_time_days": 3.0, "vc": 0.65,
        "price_per_liter": 30,
        "tank_prices": {30: 900, 20: 600, 10: 300},
        "rationale": "<b>ทำไม POQ (k=3) ถึงประหยัดที่สุด? ✨</b> สินค้ามีการใช้น้อยและผันผวนสูงมาก (VC = 0.65) การใช้นโยบาย <b>POQ (k=3)</b> หรือการรวบคำสั่งซื้อทุกๆ 3 เดือน ช่วยลดความถี่และต้นทุนในการออกคำสั่งซื้อบ่อยๆ ได้อย่างมีประสิทธิภาพ <b>ประหยัดกว่าทั้งวิธี EOQ และวิธีสั่งตามพยากรณ์ถึง 1,996.50 บาท/ปี</b>"
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
    st.session_state[f"success_msg_{p_key}"] = f"🎉 บันทึกยอดใช้จริงของเดือน {label_val} เรียบร้อยแล้ว! ระบบร่นไปงวดถัดไปแล้วน้าา"

# --- 8. Sidebar จัดการรีเซ็ต ---
with st.sidebar:
    st.header("⚙️ ระบบควบคุมแอป 🎀")
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
        
        col_policy, col_expander = st.columns([2.5, 1.2])
        with col_policy:
            policy_desc = f"✨ นโยบายที่แนะนำ: <strong>{p_inv['policy']}</strong> " + \
                          (f"(สั่งครั้งละ <strong>{p_inv['selected_lot']} ลิตร</strong>)" if p_inv['policy']=='EOQ' else f"(รอบสั่งซื้อ <strong>k = {p_inv['k']} เดือน</strong>)")
            st.markdown(f'<div class="policy-tag">{policy_desc}</div>', unsafe_allow_html=True)
        
        with col_expander:
            with st.expander("💡 เหตุผลการเลือกนโยบาย"):
                st.markdown(f"{p_inv['rationale']}", unsafe_allow_html=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if f"success_msg_{p_key}" in st.session_state:
            st.success(st.session_state[f"success_msg_{p_key}"])
            del st.session_state[f"success_msg_{p_key}"]

        c_input, c_results = st.columns([1.1, 1.9])
        
        with c_input:
            st.markdown(f"""
                <div class="input-card-container">
                    <div class="input-card-header">💖 กรอกข้อมูลประจำงวด ({input_month_label})</div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<div class="large-label">1. ปริมาณใช้งานเดือนนี้ ({input_month_label}) (ลิตร):</div>', unsafe_allow_html=True)
            last_usage = st.number_input(
                label="ปริมาณการใช้งานของเดือนปัจจุบันนี้",
                label_visibility="collapsed", min_value=0.0, value=None, step=1.0, key=f"usage_{p_key}"
            )
            
            st.markdown('<div class="large-label">2. ปริมาณคงเหลือ ณ ปัจจุบัน (ลิตร):</div>', unsafe_allow_html=True)
            stock_qty_input = st.number_input(
                label="ปริมาณคงเหลือ ณ ปัจจุบัน",
                label_visibility="collapsed", min_value=0.0, value=None, step=1.0, key=f"stock_{p_key}"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)

        # 🟢 กรณีที่ 1: กรอกข้อมูลครบถ้วน -> แสดงผลคำนวณ + กราฟ
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
                <div style="margin-top: 8px; padding-top: 6px; border-top: 2px dashed #7dd3fc; font-size: 13px; font-weight: 800; color: #0c4a6e;">
                    💳 รวมประมาณการค่าใช้จ่าย: <span style="color:#15803d; font-size:17px;">{est_cost:,.2f}</span> บาท
                </div>
                """
            else:
                tanks_display_html = f"""
                <div style='font-size:17px; font-weight:800; color:#0284c7; margin-top:4px;'>ไม่ต้องสั่งซื้อเพิ่มเติม ✨</div>
                <div style='font-size:12px; font-weight:600; color:#0369a1; margin-top:6px; background:#e0f2fe; padding:4px 8px; border-radius:8px;'>
                    📈 ยอดพยากรณ์ ({forecast_month_label}): <b>{next_f:.2f} ลิตร</b>
                </div>
                """

            with c_results:
                st.info(f"💡 **สรุปผลพยากรณ์:** คาดการณ์ปริมาณการใช้น้ำยาในเดือน **{forecast_month_label}** เท่ากับ **{next_f:.2f} ลิตร** " + 
                        (f"(แนะนำสั่งซื้อ **{recommended_qty} ลิตร**)" if recommended_qty > 0 else f"(แนะนำ **สั่งซื้อ 0 ลิตร**)"))

                st.markdown(f'<div class="large-label">📌 สรุปผลพยากรณ์ประจำเดือน: <span style="color:#a855f7;">{forecast_month_label}</span></div>', unsafe_allow_html=True)
                
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown(f'<div class="card-recommend"><div class="card-recommend-title">🎯 1. ปริมาณสั่งซื้อแนะนำ ({p_inv["policy"]})</div><div class="card-recommend-value">{recommended_qty} <small style="font-size:16px">ลิตร</small></div></div>', unsafe_allow_html=True)
                with r2:
                    st.markdown(f'<div class="card-tanks"><div class="card-tanks-title">📦 2. จำนวนถังที่ต้องสั่งซื้อ</div>{tanks_display_html}</div>', unsafe_allow_html=True)

                r3, r4 = st.columns(2)
                with r3:
                    st.markdown(f'<div class="card-base"><div class="card-title">📊 3. ผลการพยากรณ์ ({forecast_month_label})</div><div class="card-value" style="color:#a855f7;">{next_f:.2f} <small style="font-size:15px">ลิตร</small></div></div>', unsafe_allow_html=True)
                with r4:
                    st.markdown(f'<div class="card-base"><div class="card-title">⚖️ 4. ค่าความคลาดเคลื่อน</div><div style="font-size: 14px; font-weight: 800; color: #16a34a; margin-top: 4px;">คลาดเคลื่อน (+): +{error_val:.2f} ลิตร</div><div style="font-size: 14px; font-weight: 800; color: #dc2626; margin-top: 2px;">คลาดเคลื่อน (-): -{error_val:.2f} ลิตร</div></div>', unsafe_allow_html=True)

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                st.button(
                    f"💖 บันทึกยอด {input_month_label} และร่นไปคำนวณเดือน {forecast_month_label} ➔", 
                    key=f"btn_save_{p_key}", type="primary", use_container_width=True,
                    on_click=cb_save_data, args=(p_key, last_usage, input_month_label)
                )

        # 🟡 กรณีที่ 2: ข้อมูลยังไม่ครบ -> กรอบเหลืองนวลสุดคิวท์
        else:
            with c_results:
                st.markdown(f"""
                    <div class="empty-state-card">
                        <div class="empty-state-icon">📝✨</div>
                        <div class="empty-state-title">กรอกข้อมูลให้ครบทั้ง 2 ช่องน้าา 💖</div>
                        <div class="empty-state-desc">
                            1️⃣ ปริมาณใช้งานจริงเดือนปัจจุบัน (<b>{input_month_label}</b>)<br>
                            2️⃣ ปริมาณคงเหลือ ณ ปัจจุบันในคลัง
                        </div>
                        <div class="empty-state-highlight">
                            ⚡ กรอกครบแล้ว ระบบจะป๊อปอัปคำนวณผลลัพธ์เดือน (<b>{forecast_month_label}</b>) ให้ทันทีเลย!
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # แสดงกราฟเมื่อมีข้อมูล
        if last_usage is not None and stock_qty_input is not None:
            st.subheader(f"📈 กราฟแสดงแนวโน้มการใช้จริง & พยากรณ์ ({forecast_month_label})")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=current_labels, y=y_data, mode='lines+markers', name='ยอดใช้จริง (Actual)', line=dict(color='#831843', width=3)))
            fig.add_trace(go.Scatter(x=current_labels[12:], y=Forecast[12:], mode='lines+markers', name='HW-Forecast', line=dict(color='#a855f7', width=2, dash='dash')))
            fig.add_trace(go.Scatter(x=[forecast_month_label], y=[next_f], mode='markers+text', name=f'พยากรณ์ {next_f:.2f}L', marker=dict(color='#16a34a', size=14, symbol='star'), text=[f"{next_f:.2f} ลิตร"], textposition="top center"))
            fig.update_layout(xaxis_title="เดือน/ปี", yaxis_title="ปริมาณการใช้ (ลิตร)", hovermode="x unified", template="plotly_white", height=350, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

        # --- 12. ส่วนการเปรียบเทียบต้นทุนของน้ำยาแต่ละชนิด ---
        poq_cls = "cost-winner" if p_inv["policy"] == "POQ" else "cost-normal"
        eoq_cls = "cost-winner" if p_inv["policy"] == "EOQ" else "cost-normal"
        fc_cls = "cost-normal"

        st.markdown(f"""
            <div class="prod-cost-card">
                <div class="prod-cost-title">💰 ตารางเปรียบเทียบต้นทุนทั้ง 3 วิธีของ {p_info['name']}</div>
                <div class="cost-grid-mobile" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px;">
                    <div class="cost-box {poq_cls}">
                        <div class="cost-box-title">1. นโยบาย POQ {'🏆 (ประหยัดสุด)' if p_inv['policy']=='POQ' else ''}</div>
                        <div class="cost-box-val">{p_inv['poq_cost']:,.2f} บาท</div>
                    </div>
                    <div class="cost-box {eoq_cls}">
                        <div class="cost-box-title">2. นโยบาย EOQ {'🏆 (ประหยัดสุด)' if p_inv['policy']=='EOQ' else ''}</div>
                        <div class="cost-box-val">{p_inv['eoq_cost']:,.2f} บาท</div>
                    </div>
                    <div class="cost-box {fc_cls}">
                        <div class="cost-box-title">3. สั่งตามพยากรณ์ (Forecast)</div>
                        <div class="cost-box-val">{p_inv['fc_cost']:,.2f} บาท</div>
                    </div>
                </div>
                <div style="background-color: #fcf6ff; padding: 12px 15px; border-radius: 14px; font-size: 14px; color: #581c87; line-height: 1.6; border-left: 4px solid #a855f7;">
                    {p_inv['rationale']}
                </div>
            </div>
        """, unsafe_allow_html=True)


# --- 13. ช่องสรุปภาพรวมคำตอบท้ายสุด (Overall Hybrid Policy Summary Banner) ---
total_eoq_all = sum(v["eoq_cost"] for v in inventory_params.values())
total_hybrid_best = sum(v["best_cost"] for v in inventory_params.values())
total_savings = total_eoq_all - total_hybrid_best

st.markdown("<br><hr style='border: 0; height: 2px; background: #e9d5ff;'><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="background: linear-gradient(135deg, #2e1065 0%, #581c87 100%); color: #ffffff; padding: 24px; border-radius: 24px; box-shadow: 0 12px 30px rgba(88, 28, 135, 0.25); border: 2px solid #c084fc;">
        <h3 style="color: #f0abfc; margin-top:0; font-size:20px; font-weight:800; display:flex; align-items:center; gap:8px;">
            🏆 ช่องสรุปภาพรวม: การบริหารจัดการด้วย Hybrid Policy ✨
        </h3>
        <p style="font-size: 15px; line-height: 1.6; color: #e9d5ff;">
            เมื่อเลือกใช้นโยบายที่เหมาะสมที่สุดกับน้ำยาแต่ละชนิด (<strong>EOQ สำหรับน้ำยาล้างรถ</strong> และ <strong>POQ สำหรับน้ำยาเคลือบภายใน, น้ำยาเช็ดกระจก, น้ำยาลงล้อ</strong>) 
            จะได้ต้นทุนรวมทั้งระบบที่ต่ำที่สุดเมื่อเทียบกับการใช้วิธีเดียวกับทุกสินค้า
        </p>
        <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px; border-top: 1px dashed #7e22ce; padding-top: 14px;">
            <div style="flex: 1; min-width: 200px;">
                <span style="font-size: 13px; color: #d8b4fe;">ต้นทุนรวมนโยบายผสม (Hybrid Policy):</span><br>
                <span style="font-size: 26px; font-weight: 900; color: #4ade80;">""" + f"{total_hybrid_best:,.2f}" + """ บาท</span>
            </div>
            <div style="flex: 1; min-width: 200px;">
                <span style="font-size: 13px; color: #d8b4fe;">ยอดประหยัดได้รวมทั้งหมด (เทียบกับ EOQ):</span><br>
                <span style="font-size: 26px; font-weight: 900; color: #38bdf8;">""" + f"ประหยัดได้ {total_savings:,.2f}" + """ บาท</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
