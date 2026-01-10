import streamlit as st
import pandas as pd
import plotly.express as px
import re
import sys
import os
import time 

# เพิ่ม path ให้หา utils เจอ
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils 

st.set_page_config(page_title="Market Heatmap", page_icon="🏠", layout="wide", initial_sidebar_state="collapsed")
utils.navbar()

# --- HELPER FUNCTIONS ---
def clean_news_content(text):
    if not isinstance(text, str): return ""
    pattern = r"(?s)^.*?(?:\([^\)]+\)\s*-\s*|\s+--\s+)"
    cleaned_text = re.sub(pattern, "", text).strip()
    cleaned_text = cleaned_text.replace("\n", " ")
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text if cleaned_text else text

@st.cache_data
def load_data():
    df_sector = pd.DataFrame()
    df_news = pd.DataFrame()

    # --- 1. LOAD SECTOR DATA ---
    try:
        # โหลดไฟล์ Daily History
        df_sector = pd.read_csv('csv_checkpoint/sector_daily_history_7days.csv', encoding='utf-8')
        
        # ✅ FIX 1: กรองเอาเฉพาะ "วันล่าสุด" มาแสดงใน Heatmap (Snapshot)
        if 'Report_Date' in df_sector.columns:
            df_sector['Report_Date'] = pd.to_datetime(df_sector['Report_Date'])
            latest_date = df_sector['Report_Date'].max()
            df_sector = df_sector[df_sector['Report_Date'] == latest_date]

        # ✅ FIX 2: Map ชื่อคอลัมน์ให้ตรงกับที่กราฟ Treemap ต้องการ
        # CSV มี 'Final_Daily_Score' แต่กราฟเรียกใช้ 'Final_AI_Score'
        if 'Final_Daily_Score' in df_sector.columns:
            df_sector['Final_AI_Score'] = pd.to_numeric(df_sector['Final_Daily_Score'], errors='coerce').fillna(0.0)
        else:
            df_sector['Final_AI_Score'] = 0.0

        # เช็ค News_Volume (เผื่อไฟล์ไม่มี)
        if 'News_Volume' not in df_sector.columns:
            df_sector['News_Volume'] = 10  # Default value

        if 'Final_Outlook' not in df_sector.columns:
            df_sector['Final_Outlook'] = 'Neutral'

    except Exception as e: 
        # print(f"Sector load error: {e}")
        pass
    
    # --- 2. LOAD NEWS DATA ---
    try:
        # พยายามโหลดไฟล์ข่าว (รองรับหลายชื่อ)
        if os.path.exists('csv_checkpoint/sentiment_final.csv'):
            df_news = pd.read_csv('csv_checkpoint/sentiment_final.csv', encoding='utf-8')
        # elif os.path.exists('result.csv'):
        #     df_news = pd.read_csv('result.csv', encoding='utf-8')
        
        if not df_news.empty:
            if 'Date' in df_news.columns: 
                df_news['Date'] = pd.to_datetime(df_news['Date'], errors='coerce')
            
            # จัดการ Score (รองรับหลายโมเดล)
            if 'Score_Qwen2.5-14B-Instruct' in df_news.columns: 
                df_news['Sentiment_Score'] = df_news['Score_Qwen2.5-14B-Instruct'] * 10 
            elif 'Score_finma-7b-full' in df_news.columns: 
                df_news['Sentiment_Score'] = df_news['Score_finma-7b-full'] * 10
            elif 'Sentiment_Score' not in df_news.columns:
                df_news['Sentiment_Score'] = 5.0
                
            # Clean Data
            if 'Combined_Sector' in df_news.columns:
                df_news['Combined_Sector'] = df_news['Combined_Sector'].fillna('General')
            else:
                df_news['Combined_Sector'] = 'General'

            if 'Content' in df_news.columns:
                df_news['Content'] = df_news['Content'].fillna('').apply(lambda x: clean_news_content(str(x)))
            
            if 'Short_Ans' in df_news.columns:
                df_news['Short_Ans'] = df_news['Short_Ans'].fillna('')
            else:
                df_news['Short_Ans'] = ''     
    except Exception as e: 
        # print(f"News load error: {e}")
        pass
        
    return df_sector, df_news

df_sector, df_news = load_data()

# --- 🟢🔴 CUSTOM NON-BLOCKING POPUP ---
def show_floating_status(count):
    unique_id = int(time.time() * 1000)
    if count > 0:
        bg_color, border_color, text_color = "#ecfdf5", "#34d399", "#065f46"
        icon, header, msg = "✅", "Search Complete", f"Found <b>{count}</b> news items."
    else:
        bg_color, border_color, text_color = "#fef2f2", "#f87171", "#991b1b"
        icon, header, msg = "❌", "No Results", "Please try different keywords."

    st.markdown(f"""
    <style>
        @keyframes slideDownFade-{unique_id} {{
            0% {{ transform: translate(-50%, -20px); opacity: 0; }}
            10% {{ transform: translate(-50%, 10px); opacity: 1; }}
            80% {{ transform: translate(-50%, 10px); opacity: 1; }}
            100% {{ transform: translate(-50%, -20px); opacity: 0; pointer-events: none; }}
        }}
        .floating-notification-{unique_id} {{
            position: fixed; top: 80px; left: 50%; transform: translateX(-50%);
            background-color: {bg_color}; border: 1px solid {border_color}; border-left: 6px solid {border_color};
            color: {text_color}; padding: 15px 25px; border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15); z-index: 999999;
            display: flex; align-items: center; gap: 15px; min-width: 300px;
            animation: slideDownFade-{unique_id} 4s ease-in-out forwards;
        }}
    </style>
    <div id="note-{unique_id}" class="floating-notification-{unique_id}">
        <div style="font-size: 24px;">{icon}</div>
        <div>
            <div style="font-weight: 700; font-size: 16px;">{header}</div>
            <div style="font-size: 14px; opacity: 0.9;">{msg}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- LAYOUT ---
st.markdown("### 🧠 Real-time Market Sentiment Analysis")

col_map, col_news = st.columns([2, 1]) 

# --------------------------------------------------------
# 🗺️ LEFT COLUMN: SECTOR HEATMAP
# --------------------------------------------------------
with col_map:
    # เช็คว่ามีข้อมูลและมีคอลัมน์ครบถ้วน
    if not df_sector.empty and 'Sector' in df_sector.columns and 'Final_AI_Score' in df_sector.columns:
        
        # Display latest date info
        if 'Report_Date' in df_sector.columns:
            latest_str = df_sector['Report_Date'].dt.strftime('%d %b %Y').iloc[0]
            st.caption(f"Data as of: {latest_str}")

        fig = px.treemap(
            df_sector, 
            path=['Sector'], 
            values='News_Volume', 
            color='Final_AI_Score',
            color_continuous_scale=['#FF4B4B', '#FACA2B', '#09AB3B'], 
            range_color=[0, 10],
            # Custom Data ต้องเรียงตามนี้: [Outlook, Volume, Score]
            custom_data=['Final_Outlook', 'News_Volume', 'Final_AI_Score'] 
        )
        
        fig.update_traces(
            textinfo="label+value", 
            # แสดงค่าจาก customdata[2] คือ Final_AI_Score
            texttemplate="<span style='color:white; font-weight:bold;'>%{label}</span><br><span style='color:white; font-size:18px;'>%{customdata[2]:.2f}</span>",
            textposition="middle center",
            hovertemplate="<b>%{label}</b><br>Score: %{customdata[2]:.2f}/10<br>Vol: %{value}<br>Outlook: %{customdata[0]}<extra></extra>",
            marker=dict(cornerradius=5)
        )
        
        fig.update_layout(
            height=780, 
            margin=dict(t=0, l=0, r=0, b=0), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(family="Inter, sans-serif", size=14),
            coloraxis_showscale=False
        )
        
        event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points", key="treemap_chart")
        
        if len(event["selection"]["points"]) > 0:
            clicked_point = event["selection"]["points"][0]
            selected_sector_name = clicked_point.get("label")
            
            if selected_sector_name:
                st.session_state["selected_sector"] = selected_sector_name
                try:
                    st.switch_page("pages/2_Sector_Detail.py") 
                except Exception as e:
                    st.error(f"Cannot switch page. Please check file path. Error: {e}")

    else: 
        st.error("Sector data not found. Please run the analyst script first or check 'sector_daily_history_7days.csv'.")

# --------------------------------------------------------
# 📰 RIGHT COLUMN: NEWS FEED
# --------------------------------------------------------
with col_news:
    st.subheader("📰 Latest Market Movers")
    if not df_news.empty:
        with st.form("filter_form"):
            c1, c2, c3 = st.columns([2, 2, 1], vertical_alignment="bottom")
            with c1: search_query = st.text_input("Search", placeholder="Keyword...", label_visibility="collapsed")
            with c2: 
                if not df_sector.empty and 'Sector' in df_sector.columns:
                    all_sectors = sorted(df_sector['Sector'].unique().tolist())
                else:
                    all_sectors = []
                selected_sectors = st.multiselect("Sector", options=all_sectors, placeholder="All Sectors", label_visibility="collapsed")
            with c3: search_submitted = st.form_submit_button("🔍")
        
        filtered_df = df_news.copy()
        if search_query: 
            filtered_df = filtered_df[
                filtered_df['Title'].str.contains(search_query, case=False, na=False) | 
                filtered_df['Content'].str.contains(search_query, case=False, na=False)
            ]
        if selected_sectors: 
            filtered_df = filtered_df[filtered_df['Combined_Sector'].str.contains('|'.join(selected_sectors), case=False, na=False)]

        if search_submitted:
            show_floating_status(len(filtered_df))

        if 'Sentiment_Score' in filtered_df.columns:
            bull_news = filtered_df[filtered_df['Sentiment_Score'] >= 6].sort_values(by=['Date'], ascending=False)
            bear_news = filtered_df[filtered_df['Sentiment_Score'] <= 4].sort_values(by=['Date'], ascending=False)
        else:
            bull_news = pd.DataFrame(); bear_news = pd.DataFrame()

        tab_bull, tab_bear = st.tabs([f"🐂 Bullish ({len(bull_news)})", f"🐻 Bearish ({len(bear_news)})"])
        
        st.markdown("""<style>
        .news-card {background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 12px; border: 1px solid #f0f2f6;}
        .news-title {font-weight: 600; color: #1f77b4; text-decoration: none; display: block; margin-bottom: 6px;}
        .news-meta {font-size: 11px; color: #888; margin-bottom: 8px; font-weight: 500; text-transform: uppercase;}
        .sector-tag {background-color: #f8f9fa; color: #31333F; padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 600; margin-right: 4px; border: 1px solid #e9ecef;}
        .ai-summary-home {background-color: #eef2ff; border-left: 3px solid #6366f1; border-radius: 4px; padding: 8px 12px; margin-top: 8px; font-size: 12px; color: #312e81; line-height: 1.4;}
        </style>""", unsafe_allow_html=True)

        def display_cards(news_df):
            if news_df.empty:
                st.info("No news in this category."); return

            for _, row in news_df.head(3).iterrows(): 
                sectors = str(row.get('Combined_Sector', '')).split(',')
                tags_html = "".join([f'<span class="sector-tag">🏷️ {s.strip()}</span>' for s in sectors if s.strip()])
                summary = row.get('Content', '')
                if len(summary) > 120: summary = summary[:120] + "..."
                date_str = row['Date'].strftime('%d %b %H:%M') if pd.notnull(row.get('Date')) else ""
                score = row.get('Sentiment_Score', 5.0)
                color = utils.get_sentiment_color(score)
                ai_summary_html = ""
                if row.get('Short_Ans'): ai_summary_html = f'<div class="ai-summary-home">🤖 {str(row["Short_Ans"])[:150]}...</div>'

                st.markdown(f"""
                <div class="news-card" style="border-left: 6px solid {color};">
                    <div class="news-meta">{row.get('Source', 'Unknown')} • {date_str} • Score: <b>{score:.1f}</b></div>
                    <a href="{row.get('Link', '#')}" target="_blank" class="news-title">{row.get('Title', 'No Title')}</a>
                    <div style="margin-bottom:8px;">{tags_html}</div>
                    <div style="font-size:13px; color:#444;">{summary}</div>
                    {ai_summary_html}
                </div>
                """, unsafe_allow_html=True)

        with tab_bull: display_cards(bull_news)
        with tab_bear: display_cards(bear_news)

        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("View All News in News Center", type="primary", use_container_width=True, key="btn_view_all_news"):
                st.switch_page("pages/3_News_Center.py")
    else: st.info("No news data available.")