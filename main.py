# 어제의 박스오피스 — KOBIS 일별 박스오피스 API + YouTube 예고편 연동
# Streamlit Cloud의 Settings > Secrets 설정:
#   - KOBIS_KEY = "발급받은_KOBIS_키"
#   - YOUTUBE_KEY = "발급받은_유튜브_API_키" (선택 사항)

import datetime
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from googleapiclient.discovery import build

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 🎨 Bright & Clean Custom CSS (밝은 디자인 스타일링)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 전체 배경을 화사하고 깔끔한 라이트 톤으로 설정 */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    /* 카드 컨테이너 스타일 */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 18px 22px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
    }
    
    /* Metric 라벨 및 값 디자인 */
    div[data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        color: #6c757d !important;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #1e293b !important;
        font-weight: 700;
    }

    /* 표(DataFrame) 스타일링 */
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
</style>
""", unsafe_allow_html=True)

API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)

# 서버 시간대와 관계없이 한국 시간(UTC+9) 기준으로 어제를 계산합니다.
KST = datetime.timezone(datetime.timedelta(hours=9))
today_kst = datetime.datetime.now(KST).date()
yesterday = today_kst - datetime.timedelta(days=1)

st.title("🎬 일별 박스오피스 & 영화 예고편")
st.caption("달력에서 날짜를 선택하세요. 가장 늦게 선택할 수 있는 날짜는 한국 시간 기준 어제입니다.")

selected_date = st.date_input(
    "조회 날짜",
    value=yesterday,
    min_value=datetime.date(2004, 1, 1),
    max_value=yesterday,
    format="YYYY/MM/DD"
)
target_dt = selected_date.strftime("%Y%m%d")
display_date = selected_date.strftime("%Y년 %m월 %d일")

# 인증키는 Streamlit 비밀 금고(Secrets)에서 불러옵니다.
try:
    API_KEY = st.secrets["KOBIS_KEY"]
except Exception:
    st.error("🔐 KOBIS 인증키를 찾을 수 없습니다.")
    st.markdown(
        "Streamlit Cloud의 **Settings → Secrets**에 `KOBIS_KEY`가 등록되어 있는지 확인하세요."
    )
    st.code('KOBIS_KEY = "발급받은_인증키"', language="toml")
    st.stop()


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_boxoffice(date_text, api_key):
    """KOBIS API를 호출해 JSON 응답을 가져옵니다."""
    response = requests.get(
        API_URL,
        params={"key": api_key, "targetDt": date_text},
        timeout=20
    )
    response.
