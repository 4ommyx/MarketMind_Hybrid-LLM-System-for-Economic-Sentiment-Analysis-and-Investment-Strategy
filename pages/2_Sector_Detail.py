import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# ==========================================
# 1. SETUP & CONFIG
# ==========================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Sector Deep Dive", page_icon="🔍", layout="wide", initial_sidebar_state="collapsed")

try:
    import utils
    utils.navbar()
except:
    pass

# Custom CSS
st.markdown("""
<style>
    .ai-card {
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        height: 100%;
        transition: transform 0.2s;
    }
    .ai-card:hover {
        transform: translateY(-5px);
    }
    .ai-card-header {
        font-size: 1.5rem; 
        font-weight: bold;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        padding-bottom: 10px;
    }
    .ai-emoji-badge {
        font-size: 1.8rem; 
        background: rgba(0,0,0,0.05);
        padding: 2px 8px;
        border-radius: 8px;
        line-height: 1;
    }
    .ai-reason {
        font-size: 1rem;
        opacity: 0.95;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    file_path = 'csv_checkpoint/sector_daily_history_7days.csv'
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['Report_Date'] = pd.to_datetime(df['Report_Date'])
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

CUTE_MODEL_NAMES = {
    "Qwen": "Little Qwen 🐼",
    "Llama": "Mama Llama 🦙",
    "Gemma": "Gemmy Sparkle ✨",
    "DeepSeek": "DeepSeeker 🐳",
    "Mistral": "Misty Wind 🌪️"
}

def create_gauge_chart(score):
    bar_color = '#09ab3b' if score >= 6.5 else ('#ff4b4b' if score <= 3.5 else '#faca2b')
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 10], 'tickwidth': 1}, 'bar': {'color': bar_color},
            'bgcolor': "white", 'borderwidth': 2, 'bordercolor': "gray",
            'steps': [
                {'range': [0, 3.5], 'color': 'rgba(255, 75, 75, 0.2)'}, 
                {'range': [3.5, 6.5], 'color': 'rgba(250, 202, 43, 0.2)'}, 
                {'range': [6.5, 10], 'color': 'rgba(9, 171, 59, 0.2)'}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': score}
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
    return fig

def get_card_style(score):
    if score >= 8.0:
        return { "bg": "rgba(0, 230, 118, 0.15)", "border": "#00e676", "emoji": "🤩" }
    elif score >= 6.0:
        return { "bg": "rgba(76, 175, 80, 0.15)", "border": "#66bb6a", "emoji": "😊" }
    elif score >= 4.0:
        return { "bg": "rgba(255, 235, 59, 0.15)", "border": "#fdd835", "emoji": "😐" }
    elif score >= 2.0:
        return { "bg": "rgba(255, 152, 0, 0.15)", "border": "#ffa726", "emoji": "😰" }
    else:
        return { "bg": "rgba(255, 23, 68, 0.15)", "border": "#ff1744", "emoji": "😱" }

# ==========================================
# 4. MAIN UI
# ==========================================
st.title("🔍 Sector Deep Dive")

if not df.empty:
    # --- A. SELECTOR (แก้ไข Bug เด้งกลับ) ---
    sector_list = sorted(df['Sector'].unique())
    
    # 1. ตรวจสอบว่าค่าใน session state ยัง valid อยู่ไหม (เผื่อ data เปลี่ยน)
    if 'selected_sector' not in st.session_state or st.session_state.selected_sector not in sector_list:
        st.session_state.selected_sector = sector_list[0]

    # 2. ใช้ key="selected_sector" เพื่อผูกกับ session state โดยตรง
    # (ลบ index=... ออก เพราะ key จะจัดการเรื่องเลือกค่าปัจจุบันให้เอง)
    selected_sector = st.selectbox("Select Sector", sector_list, key="selected_sector")

    # Filter Data
    sector_data = df[df['Sector'] == selected_sector].sort_values(by='Report_Date')
    latest_data = sector_data.iloc[-1]
    current_score = latest_data['Final_Daily_Score']
    latest_date_str = latest_data['Report_Date'].strftime('%Y-%m-%d')

    # --- B. CHARTS ROW ---
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader(f"Score: {current_score:.2f}")
        st.caption(f"Outlook: {latest_data['Final_Outlook']} (as of {latest_date_str})")
        st.plotly_chart(create_gauge_chart(current_score), use_container_width=True)

    with col2:
        st.subheader("7-Day Trend")
        fig_line = px.line(
            sector_data, x='Report_Date', y='Final_Daily_Score',
            markers=True, range_y=[0, 10], color_discrete_sequence=['#1f77b4']
        )
        fig_line.add_hrect(y0=6.5, y1=10, fillcolor="green", opacity=0.1, line_width=0)
        fig_line.add_hrect(y0=0, y1=3.5, fillcolor="red", opacity=0.1, line_width=0)
        fig_line.update_layout(height=350)
        st.plotly_chart(fig_line, use_container_width=True)

    # --- C. AI ANALYSIS CARDS ---
    st.divider()
    st.subheader("🤖 AI Analysis Breakdown")
    
    reason_cols = [c for c in df.columns if 'Reason_' in c]
    model_keys = [c.replace('Reason_', '') for c in reason_cols]
    
    if model_keys:
        cols = st.columns(len(model_keys))
        for i, model_key in enumerate(model_keys):
            with cols[i]:
                reason_col = f"Reason_{model_key}"
                score_col = f"Score_{model_key}"
                
                if reason_col in latest_data:
                    m_score = latest_data.get(score_col, 0)
                    reason = latest_data.get(reason_col, "No comment provided.")
                    style = get_card_style(m_score)
                    cute_name = CUTE_MODEL_NAMES.get(model_key, f"{model_key} 🤖")
                    
                    card_html = f"""
                    <div class="ai-card" style="background-color: {style['bg']}; border-left: 6px solid {style['border']};">
                        <div class="ai-card-header" style="color: {style['border']};">
                            <span>{cute_name}</span>
                            <span class="ai-emoji-badge">{style['emoji']}</span>
                        </div>
                        <div class="ai-reason">
                            {reason}
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.warning(f"No data for {model_key}")
    else:
        st.info("No AI detailed analysis available.")

else:
    st.error("❌ Data not found. Please run the analysis script first.")