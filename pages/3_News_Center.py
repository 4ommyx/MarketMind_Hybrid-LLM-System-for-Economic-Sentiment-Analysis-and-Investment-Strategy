import streamlit as st
import pandas as pd
import re
import sys
import os

# เพิ่ม path ให้หา utils เจอ
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Config
st.set_page_config(page_title="News Center", page_icon="📰", layout="wide", initial_sidebar_state="collapsed")
utils.navbar()

# CSS Styling
st.markdown("""
<style>
    .news-card {
        background-color: white; 
        padding: 20px; 
        border-radius: 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        margin-bottom: 20px; /* เพิ่มระยะห่างระหว่างบรรทัดหน่อย */
        border: 1px solid #f0f2f6; 
        transition: transform 0.2s;
        height: 100%; /* ให้การ์ดสูงเต็มพื้นที่ column */
        display: flex;
        flex-direction: column;
    }
    .news-card:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
    }
    .news-title {
        font-weight: 600; 
        font-size: 18px; 
        color: #1f77b4; 
        text-decoration: none; 
        display: block; 
        margin-bottom: 8px;
    }
    .news-meta {
        font-size: 12px; 
        color: #888; 
        margin-bottom: 10px; 
        font-weight: 500; 
        text-transform: uppercase;
    }
    .sector-tag {
        background-color: #f0f2f6; 
        color: #31333F; 
        padding: 3px 8px; 
        border-radius: 4px; 
        font-size: 11px; 
        font-weight: 600; 
        margin-right: 5px; 
        border: 1px solid #e0e0e0;
    }
    
    /* กล่อง AI Summary (ย้ายไปด้านล่าง) */
    .ai-summary-box {
        background-color: #eef2ff; 
        border-left: 4px solid #6366f1; 
        border-radius: 4px;
        padding: 10px 15px;
        margin-top: 15px; /* เว้นระยะห่างจากเนื้อหาข้างบน */
        font-size: 13px;
        color: #312e81; 
        line-height: 1.5;
    }
    
    /* เนื้อหาข่าวปกติ */
    .original-content {
        font-size: 13px; 
        color: #555; 
        line-height: 1.5;
        margin-top: 8px;
        flex-grow: 1; /* ดันเนื้อหาส่วนนี้ให้เต็มพื้นที่ */
    }
</style>
""", unsafe_allow_html=True)

def clean_news_content(text):
    if not isinstance(text, str): return ""
    
    # 1. ลบพวก Prefix สำนักข่าว (Pattern เดิม)
    pattern = r"(?s)^.*?(?:\([^\)]+\)\s*-\s*|\s+--\s+)"
    cleaned_text = re.sub(pattern, "", text).strip()
    
    # 2. [สำคัญ] เปลี่ยนการขึ้นบรรทัดใหม่ (\n) เป็นช่องว่างธรรมดา
    cleaned_text = cleaned_text.replace("\n", " ")
    
    # 3. ลบช่องว่างซ้ำๆ ให้เหลือช่องเดียว
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text if cleaned_text else text

@st.cache_data
def load_data():
    try:
        df_news = pd.read_csv('csv_checkpoint/news_summary.csv')
        if 'Date' in df_news.columns: df_news['Date'] = pd.to_datetime(df_news['Date'], errors='coerce')
        score_col = 'Score_Qwen2.5-14B-Instruct' 
        if score_col in df_news.columns: df_news['Sentiment_Score'] = df_news['Score_Qwen2.5-14B-Instruct'] * 10 
        elif 'Score_finma-7b-full' in df_news.columns: df_news['Sentiment_Score'] = df_news['Score_finma-7b-full'] * 10
        else: df_news['Sentiment_Score'] = 5.0
        
        df_news['Combined_Sector'] = df_news['Combined_Sector'].fillna('General')
        df_news['Content'] = df_news['Content'].fillna('')
        df_news['Content'] = df_news['Content'].apply(lambda x: clean_news_content(str(x)))
        
        if 'Short_Ans' in df_news.columns:
            df_news['Short_Ans'] = df_news['Short_Ans'].fillna('')
        else:
            df_news['Short_Ans'] = ''
            
        return df_news
    except: return pd.DataFrame()

df_news = load_data()

if not df_news.empty:
    with st.expander("🔍 Search & Filter Options", expanded=True):
        with st.form("news_filter_form"):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1: search_query = st.text_input("Search Keyword", placeholder="Type to search headlines or content...")
            with c2: 
                all_sectors = set()
                for sectors in df_news['Combined_Sector'].dropna(): all_sectors.update([s.strip() for s in sectors.split(',')])
                selected_sectors = st.multiselect("Filter by Sector", options=sorted(list(all_sectors)))
            with c3: sentiment_filter = st.selectbox("Sentiment Type", ["All", "Bullish Only", "Bearish Only", "Neutral"])
            st.form_submit_button("Apply Filters")

    filtered_df = df_news.copy()
    if search_query: filtered_df = filtered_df[filtered_df['Title'].str.contains(search_query, case=False, na=False) | filtered_df['Content'].str.contains(search_query, case=False, na=False)]
    if selected_sectors: filtered_df = filtered_df[filtered_df['Combined_Sector'].str.contains('|'.join(selected_sectors), case=False, na=False)]
    if sentiment_filter == "Bullish Only": filtered_df = filtered_df[filtered_df['Sentiment_Score'] >= 6]
    elif sentiment_filter == "Bearish Only": filtered_df = filtered_df[filtered_df['Sentiment_Score'] <= 4]
    elif sentiment_filter == "Neutral": filtered_df = filtered_df[(filtered_df['Sentiment_Score'] > 4) & (filtered_df['Sentiment_Score'] < 6)]

    filtered_df = filtered_df.sort_values(by=['Date'], ascending=False)
    
    st.subheader(f"Latest News ({len(filtered_df)} items)")

    # --- [ส่วนที่แก้ไข] สร้าง Layout 2 Columns ---
    cols = st.columns(2) 

    # ใช้ enumerate เพื่อสลับ column ซ้าย/ขวา
    for i, (index, row) in enumerate(filtered_df.head(50).iterrows()):
        
        # เลือก column: ถ้า i เป็นเลขคู่ลง column 0 (ซ้าย), เลขคี่ลง column 1 (ขวา)
        current_col = cols[i % 2]
        
        with current_col:
            sectors = str(row['Combined_Sector']).split(',')
            tags_html = "".join([f'<span class="sector-tag">🏷️ {s.strip()}</span>' for s in sectors if s.strip()])
            date_str = row['Date'].strftime('%d %b %Y %H:%M') if pd.notnull(row['Date']) else ""
            
            score = row['Sentiment_Score']
            color = utils.get_sentiment_color(score)

            # เตรียม AI Summary (แต่ยังไม่ใส่)
            ai_summary_html = ""
            if row['Short_Ans'] and str(row['Short_Ans']).strip() != "":
                ai_summary_html = f'<div class="ai-summary-box"><strong>🤖 AI Summary:</strong> {row["Short_Ans"]}</div>'

            # เตรียมเนื้อหาข่าว (Original)
            original_text = row['Content']
            if len(original_text) > 200: 
                original_text = original_text[:200] + "..."
            
            # สร้าง HTML: เอา Original Content ขึ้นก่อน -> ตามด้วย AI Summary ด้านล่างสุด
            card_html = f"""
<div class="news-card" style="border-left: 6px solid {color};">
<div class="news-meta">{row['Source']} • {date_str} • Score: <b>{score:.1f}</b></div>
<a href="{row['Link']}" target="_blank" class="news-title">{row['Title']}</a>
<div style="margin-bottom:5px;">{tags_html}</div>
<div class="original-content">{original_text}</div>
{ai_summary_html}
</div>
"""
            st.markdown(card_html, unsafe_allow_html=True)

else: st.error("No news data found.")