import streamlit as st

def navbar():
    """
    Navbar แบบ Native Streamlit
    Layout: [ ชื่อ App ใหญ่ๆ ] ------ [ Dashboard ] [ Sector ] [ News ]
    """
    # CSS ซ่อน Sidebar และตกแต่ง Navbar
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        div[data-testid="stPageLink-NavLink"] { justify-content: center; }
        
        /* ปรับแต่งชื่อ App ใน Navbar */
        .nav-app-name {
            font-weight: 700;
            font-size: 26px;  /* <--- ปรับให้ใหญ่ขึ้นตรงนี้ (เดิม 20px) */
            color: #333333;   /* <--- เปลี่ยนเป็นสีดำเข้ม (Black) */
            display: flex;
            align-items: center;
            height: 100%;
            font-family: 'Inter', sans-serif;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        # ปรับสัดส่วน: ชื่อ App (2) | ว่าง (1) | เมนู (3 ส่วน)
        col_brand, col_space, col1, col2, col3 = st.columns([2.5, 0.5, 1, 1, 1]) 

        with col_brand:
            # ใส่ชื่อ App
            st.markdown('<div class="nav-app-name">🧠 AI Market Psychologist</div>', unsafe_allow_html=True)

        with col1:
            st.page_link("Home.py", label="Dashboard", icon="🏠", use_container_width=True)
        
        with col2:
            st.page_link("pages/2_Sector_Detail.py", label="Sector Dive", icon="🔍", use_container_width=True)
        
        with col3:
            st.page_link("pages/3_News_Center.py", label="News Center", icon="📰", use_container_width=True)
            
        st.divider()
# --- ฟังก์ชันคำนวณเฉดสี (Gradient) ---
# --- [UPDATED] ฟังก์ชันคำนวณเฉดสี (รองรับค่าติดลบ -10 ถึง 10) ---
def get_sentiment_color(score):
    """
    แปลงคะแนน -10 ถึง 10 ให้เป็นรหัสสี Hex:
    -10 (แดงจัด) -> 0 (เหลือง) -> 10 (เขียวจัด)
    """
    RED = (255, 75, 75)     # #FF4B4B
    YELLOW = (250, 202, 43) # #FACA2B
    GREEN = (9, 171, 59)    # #09AB3B

    def interpolate(start, end, factor):
        return int(start + (end - start) * factor)

    # ปรับช่วงคะแนน (Normalize) จาก [-10, 10] ให้เป็น [0, 1] เพื่อคำนวณ
    # แต่เราแบ่งครึ่งที่ 0 (เหลือง)
    
    if score < 0:
        # ช่วง -10 ถึง 0 (แดง -> เหลือง)
        # ถ้า score = -10 -> factor = 0 (แดง)
        # ถ้า score = 0   -> factor = 1 (เหลือง)
        factor = (score + 10) / 10.0
        # กันเหนียว: เผื่อคะแนนต่ำกว่า -10
        factor = max(0.0, min(1.0, factor)) 
        
        r = interpolate(RED[0], YELLOW[0], factor)
        g = interpolate(RED[1], YELLOW[1], factor)
        b = interpolate(RED[2], YELLOW[2], factor)
    else:
        # ช่วง 0 ถึง 10 (เหลือง -> เขียว)
        # ถ้า score = 0  -> factor = 0 (เหลือง)
        # ถ้า score = 10 -> factor = 1 (เขียว)
        factor = score / 10.0
        # กันเหนียว: เผื่อคะแนนเกิน 10
        factor = max(0.0, min(1.0, factor))
        
        r = interpolate(YELLOW[0], GREEN[0], factor)
        g = interpolate(YELLOW[1], GREEN[1], factor)
        b = interpolate(YELLOW[2], GREEN[2], factor)
        
    return f"#{r:02x}{g:02x}{b:02x}"
