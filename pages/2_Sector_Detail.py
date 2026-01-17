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

# --- 🎯 CONFIG: 11 MAIN SECTORS (WHITELIST) ---
MAIN_SECTORS = [
    "Energy", 
    "Basic Materials",           # GICS: Materials
    "Industrials", 
    "Consumer Cyclical",         # GICS: Consumer Discretionary
    "Consumer Defensive",        # GICS: Consumer Staples
    "Healthcare",                # GICS: Health Care
    "Financials", 
    "Technology",                # GICS: Information Technology
    "Communication Services", 
    "Utilities", 
    "Real Estate"
]

# --- 🎨 MODERN UI CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    .modern-card {
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        font-family: 'Inter', sans-serif;
        height: 100%;
    }
    .modern-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    .card-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .model-name {
        font-size: 1.1rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .verdict-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .score-container {
        margin-bottom: 15px;
    }
    .score-label {
        font-size: 0.85rem;
        font-weight: 600;
        opacity: 0.8;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    .score-val-big {
        font-size: 1.4rem;
        font-weight: 800;
        line-height: 1;
    }
    .progress-track {
        width: 100%;
        height: 8px;
        background-color: rgba(0,0,0,0.1);
        border-radius: 4px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 1s ease-in-out;
    }
    .ai-reason-text {
        font-size: 0.95rem;
        line-height: 1.6;
        opacity: 0.95;
        background: rgba(255,255,255,0.4);
        padding: 12px;
        border-radius: 8px;
    }
    @media (prefers-color-scheme: dark) {
        .ai-reason-text { background: rgba(0,0,0,0.05); }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    file_path = 'csv_checkpoint/sector_daily_history_enriched.csv' 
    if not os.path.exists(file_path):
        file_path = 'sector_daily_history_enriched.csv'

    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['Report_Date'] = pd.to_datetime(df['Report_Date'])
            df = df[df['Sector'].isin(MAIN_SECTORS)]
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
    "Qwen": "Qweny ",
    "Llama": "Llamy",
    "Gemma": "Gemmy",
    "DeepSeek": "DeepSeeker 🐳",
    "Mistral": "Misty Wind 🌪️"
}

def create_gauge_chart(score):
    bar_color = '#09ab3b' if score >= 6.5 else ('#ff4b4b' if score <= 3.5 else '#faca2b')
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 10], 'tickwidth': 1}, 
            'bar': {'color': bar_color},
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

# ==========================================
# 4. MAIN UI
# ==========================================
st.title("🔍 Sector Deep Dive")

if not df.empty:
    # --- A. SELECTOR ---
    sector_list = sorted(df['Sector'].unique())
    if 'selected_sector' not in st.session_state:
        st.session_state.selected_sector = sector_list[0]
    elif st.session_state.selected_sector not in sector_list:
        st.session_state.selected_sector = sector_list[0]

    selected_sector = st.selectbox("Select Sector", sector_list, key="selected_sector")

    # Filter Data
    sector_data = df[df['Sector'] == selected_sector].sort_values(by='Report_Date')
    
    if not sector_data.empty:
        latest_data = sector_data.iloc[-1]
        current_score = latest_data['Final_Daily_Score']
        latest_date_str = latest_data['Report_Date'].strftime('%Y-%m-%d')

        # --- B. CHARTS ROW ---
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader(f"Health Score: {current_score:.2f}")
            st.caption(f"Outlook: {latest_data['Final_Outlook']} (as of {latest_date_str})")
            st.plotly_chart(create_gauge_chart(current_score), use_container_width=True)

        with col2:
            st.subheader("30-Day Trend")
            fig_line = px.line(
                sector_data, x='Report_Date', y='Final_Daily_Score',
                markers=True, range_y=[0, 10], color_discrete_sequence=['#1f77b4']
            )
            fig_line.add_hrect(y0=6.5, y1=10, fillcolor="green", opacity=0.1, line_width=0)
            fig_line.add_hrect(y0=0, y1=3.5, fillcolor="red", opacity=0.1, line_width=0)
            fig_line.update_layout(height=350)
            st.plotly_chart(fig_line, use_container_width=True)

        # --- C. AI INVESTMENT STRATEGY ---
        st.divider()
        
        FULL_MODEL_NAMES = {
            "Qwen": "Suggested by Qwen/Qwen2.5-14B-Instruct",
            "Llama": "Suggested by meta-llama/Meta-Llama-3.1-8B-Instruct",
            "Gemma": "Suggested by google/gemma-3-12b-it",
            "DeepSeek": "Suggested by deepseek-ai/DeepSeek-R1",
            "Mistral": "Suggested by mistralai/Mistral-7B-Instruct-v0.3"
        }

        # 1. PRE-CALCULATE DATA
        reason_cols = [c for c in df.columns if 'Invest_Reason_' in c]
        model_keys = [c.replace('Invest_Reason_', '') for c in reason_cols]
        models_data = []

        if model_keys:
            for model_key in model_keys:
                reason_col = f"Invest_Reason_{model_key}"
                score_col = f"Invest_Score_{model_key}"
                
                if reason_col in latest_data:
                    m_score = latest_data.get(score_col, 0)
                    
                    # Fix NaN
                    raw_reason = latest_data.get(reason_col)
                    if pd.isna(raw_reason) or str(raw_reason).lower() == 'nan' or str(raw_reason).strip() == '':
                        reason = "⚠️ No analysis provided by this model."
                    else:
                        reason = str(raw_reason)
                    
                    # Style Logic
                    if m_score >= 8.0:
                        style = {"gradient": "linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)", "accent": "#1b5e20", "bar_bg": "#2e7d32", "emoji": "🚀", "verdict": "STRONG BUY"}
                    elif m_score >= 6.5:
                        style = {"gradient": "linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%)", "accent": "#33691e", "bar_bg": "#558b2f", "emoji": "✅", "verdict": "BUY"}
                    elif m_score >= 4.0:
                        style = {"gradient": "linear-gradient(135deg, #fffde7 0%, #fff9c4 100%)", "accent": "#bf8d0a", "bar_bg": "#f9a825", "emoji": "✋", "verdict": "HOLD"}
                    elif m_score >= 2.0:
                        style = {"gradient": "linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)", "accent": "#e65100", "bar_bg": "#ef6c00", "emoji": "🔻", "verdict": "SELL"}
                    else:
                        style = {"gradient": "linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)", "accent": "#b71c1c", "bar_bg": "#c62828", "emoji": "💀", "verdict": "STRONG SELL"}

                    models_data.append({
                        "key": model_key,
                        "cute_name": CUTE_MODEL_NAMES.get(model_key, model_key),
                        "full_name": FULL_MODEL_NAMES.get(model_key, f"Suggested by {model_key}"),
                        "score": m_score,
                        "reason": reason,
                        "style": style
                    })

        # 2. RENDER HEADER ROW
        c_title, c_bar = st.columns([1, 1], vertical_alignment="center")
        
        with c_title:
            st.subheader("🤖 AI Investment Strategy")
            
        with c_bar:
            if models_data:
                segments_html = ""
                for m in models_data:
                    # สร้าง string HTML แบบบรรทัดเดียว หรือชิดซ้ายสุด เพื่อป้องกันการตีความเป็น code block
                    segments_html += f"""<div style="flex: 1; background-color: {m['style']['bar_bg']}; display: flex; flex-direction: column; align-items: center; justify-content: center; border-right: 1px solid rgba(255,255,255,0.2);"><div style="font-size: 0.7rem; font-weight: 600; opacity: 0.9; line-height: 1;">{m['cute_name']}</div><div style="font-size: 0.8rem; font-weight: 800; line-height: 1;">{m['style']['verdict']}</div></div>"""
                
                # HTML ต้องชิดซ้ายสุดใน F-string นี้
                summary_bar_html = f"""
<div style="width: 100%; display: flex; justify-content: flex-end;">
<div style="width: 100%; max-width: 500px; height: 40px; display: flex; border-radius: 8px; overflow: hidden; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); font-family: 'Inter', sans-serif;">
{segments_html}
</div>
</div>
"""
                st.markdown(summary_bar_html, unsafe_allow_html=True)

        # 3. RENDER CARDS
        if models_data:
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            
            cols = st.columns(len(models_data))
            for i, data in enumerate(models_data):
                with cols[i]:
                    style = data['style']
                    width_pct = min(100, max(0, data['score'] * 10))
                    
                    # 🔥 FIXED INDENTATION HERE: HTML ชิดซ้ายสุด
                    card_html = f"""
<div class="modern-card" style="background: {style['gradient']}; border-left: 5px solid {style['accent']};">
<div class="card-header-row">
<div class="model-name" style="color: {style['accent']};">
{style['emoji']} {data['cute_name']}
</div>
<div class="verdict-badge" style="background: {style['accent']}; color: white;">
{style['verdict']}
</div>
</div>
<div class="score-container">
<div class="score-label" style="color: {style['accent']};">
<span style="font-size: 0.75rem; opacity: 0.8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 70%;">{data['full_name']}</span>
<span class="score-val-big"></span>
</div>
<div class="progress-track">
<div class="progress-fill" style="width: {width_pct}%; background-color: {style['accent']};"></div>
</div>
</div>
<div class="ai-reason-text" style="color: {style['accent']}; border: 1px solid {style['accent']}20;">
{data['reason']}
</div>
</div>
"""
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("No AI Investment Strategy available. Please ensure data is enriched.")
    else:
        st.error(f"No data available for {selected_sector}")

else:
    st.error("❌ Data not found. Please run the analysis script first.")