import requests
import streamlit as st
from openai import OpenAI

# -------------------------
# 설정
# -------------------------
st.set_page_config(
    page_title="AI 여행 코스 추천",
    page_icon="🧳",
    layout="wide"
)

TOUR_API_KEY = st.secrets["TOUR_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# 지역 코드
AREA_CODES = {
    "서울": 1,
    "인천": 2,
    "대전": 3,
    "대구": 4,
    "광주": 5,
    "부산": 6,
    "울산": 7,
    "세종": 8,
    "경기": 31,
    "강원": 32,
    "충북": 33,
    "충남": 34,
    "경북": 35,
    "경남": 36,
    "전북": 37,
    "전남": 38,
    "제주": 39
}


# -------------------------
# TourAPI
# -------------------------
@st.cache_data
def get_places(area_code):
    url = "https://apis.data.go.kr/B551011/KorService1/areaBasedList1"

    params = {
        "serviceKey": TOUR_API_KEY,
        "MobileOS": "ETC",
        "MobileApp": "TravelAI",
        "_type": "json",
        "numOfRows": 10,
        "pageNo": 1,
        "contentTypeId": 12,
        "areaCode": area_code
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        items = (
            data["response"]["body"]["items"].get("item", [])
        )

        if isinstance(items, dict):
            items = [items]

        return items

    except Exception as e:
        st.error(e)
        return []


# -------------------------
# AI 일정 생성
# -------------------------
def make_plan(style, days, places):

    place_names = ", ".join(
        p["title"] for p in places
    )

    prompt = f"""
    여행 스타일 : {style}

    여행기간 : {days}일

    관광지 :
    {place_names}

    위 관광지를 이용하여
    Day1 ~ Day{days} 일정으로
    추천해줘.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "너는 대한민국 최고의 여행 플래너이다."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# -------------------------
# UI
# -------------------------

st.title("🧳 AI 맞춤 여행 코스 추천")

col1, col2, col3 = st.columns(3)

with col1:
    area = st.selectbox(
        "지역",
        AREA_CODES.keys()
    )

with col2:
    days = st.slider(
        "여행 기간",
        1,
        7,
        2
    )

with col3:
    style = st.selectbox(
        "여행 스타일",
        [
            "혼자",
            "커플",
            "가족",
            "맛집",
            "힐링",
            "액티비티"
        ]
    )


if st.button("여행 코스 생성"):

    with st.spinner("관광지 검색 중..."):

        places = get_places(
            AREA_CODES[area]
        )

    if len(places) == 0:
        st.warning("관광지를 찾지 못했습니다.")
        st.stop()

    st.success(f"{len(places)}개의 관광지를 찾았습니다.")

    st.subheader("추천 관광지")

    for p in places:

        with st.container():

            c1, c2 = st.columns([1, 3])

            with c1:

                if p.get("firstimage"):
                    st.image(
                        p["firstimage"],
                        width=150
                    )

            with c2:

                st.markdown(f"### {p['title']}")

                st.write(
                    p.get(
                        "addr1",
                        "주소 없음"
                    )
                )

    with st.spinner("AI가 여행 일정을 만드는 중..."):

        plan = make_plan(
            style,
            days,
            places
        )

    st.divider()

    st.subheader("🤖 AI 추천 일정")

    st.markdown(plan)
