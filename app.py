import streamlit as st
import sqlite3
import json
from datetime import datetime
import rules_v38
import ai_engine
from validator import calculate_final_score

if "ADMIN_PASSWORD" not in st.secrets:
    st.error("🚨 LỖI BẢO MẬT: Chưa cấu hình ADMIN_PASSWORD trong Secrets.")
    st.stop()
ADMIN_PASS = st.secrets["ADMIN_PASSWORD"]

st.set_page_config(page_title="Đánh giá Prompt", page_icon="✨", layout="centered")

# Ép nền sáng, chữ đen, khung kính mờ
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%) !important;
    }
    h1, h2, h3, p, span, div, label {
        color: #0f172a !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        margin-bottom: 15px !important;
    }
    div[data-baseweb="textarea"] {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
    }
    div[data-baseweb="textarea"] textarea {
        color: #0f172a !important;
        background-color: white !important;
    }
    .stButton>button {
        width: 100% !important;
        background: linear-gradient(90deg, #ec4899 0%, #3b82f6 100%) !important;
        color: white !important;
        border-radius: 999px !important;
        font-weight: bold !important;
        padding: 10px !important;
        border: none !important;
    }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #ec4899 0%, #3b82f6 100%) !important;
    }
    .score-text {
        font-size: 60px !important;
        font-weight: 900 !important;
        background: -webkit-linear-gradient(45deg, #ec4899, #3b82f6) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, timestamp TEXT, prompt TEXT, type TEXT, score REAL, details TEXT)''')
    conn.commit()
    return conn

st.title("✨ Hệ thống Đánh giá Prompt")
tab1, tab2 = st.tabs(["User", "Admin"])

with tab1:
    with st.container():
        prompt_input = st.text_area("Nhập prompt cần đánh giá:", height=150, placeholder="Ví dụ: viết bài văn so sánh 2 bài thơ...")
        btn_eval = st.button("Đánh giá ngay")

    if btn_eval:
        if not prompt_input.strip():
            st.warning("Vui lòng nhập prompt!")
        else:
            content_type = rules_v38.classify_prompt(prompt_input)
            if content_type == rules_v38.TYPE_EMPTY:
                st.warning("Prompt trống.")
            elif content_type == rules_v38.TYPE_IMAGE:
                st.info("Chưa hỗ trợ chấm điểm ảnh (IMAGE).")
            else:
                with st.spinner(f"AI đang phân tích dạng {content_type}..."):
                    try:
                        ai_data = ai_engine.get_ai_evaluation(prompt_input, content_type)
                        final_score = calculate_final_score(ai_data["scores"], content_type)
                        
                        with st.container():
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.markdown(f'<p style="font-size:14px; font-weight:bold; color:#64748b !important; margin-bottom:0;">ĐIỂM TỔNG</p><span class="score-text">{final_score}</span><span style="font-size:20px; color:#94a3b8 !important; font-weight:bold;"> / 10</span>', unsafe_allow_html=True)
                            with col2:
                                st.markdown(f'<div style="text-align:right;"><p style="font-size:14px; font-weight:bold; color:#64748b !important; margin-bottom:8px;">PHÂN LOẠI</p><span style="background: linear-gradient(90deg, #ec4899, #3b82f6); color:white !important; padding:8px 16px; border-radius:999px; font-weight:bold;">{content_type}</span></div>', unsafe_allow_html=True)
                        
                        st.markdown("### Điểm từng tiêu chí")
                        with st.container():
                            criteria = rules_v38.get_criteria_by_type(content_type)
                            colA, colB = st.columns(2)
                            items = list(criteria.items())
                            for i, (crit_id, info) in enumerate(items):
                                score = ai_data["scores"][crit_id]
                                target_col = colA if i % 2 == 0 else colB
                                with target_col:
                                    st.write(f"**{info['name']}**: {score}/10")
                                    st.progress(score / 10)
                        
                        st.markdown("### Bản sửa (11 mục)")
                        with st.container():
                            for sec in rules_v38.REQUIRED_REWRITE_SECTIONS:
                                st.markdown(f"**{sec}:** {ai_data['rewrite'][sec]}")
                        
                        conn = init_db()
                        conn.execute("INSERT INTO history (timestamp, prompt, type, score, details) VALUES (?, ?, ?, ?, ?)",
                                     (datetime.now().isoformat(), prompt_input, content_type, final_score, json.dumps(ai_data['scores'])))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        st.error(f"Lỗi: {str(e)}")

with tab2:
    with st.container():
        pwd = st.text_input("Mật khẩu Admin:", type="password")
        if pwd == ADMIN_PASS:
            st.success("Đăng nhập thành công!")
            conn = init_db()
            rows = conn.execute("SELECT * FROM history ORDER BY id DESC LIMIT 10").fetchall()
            conn.close()
            if rows:
                for row in rows:
                    st.info(f"**{row[1]}** | Loại: {row[3]} | Điểm: {row[4]} | Prompt: {row[2]}")
            else:
                st.write("Chưa có lịch sử.")
        elif pwd:
            st.error("Sai mật khẩu.")
