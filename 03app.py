import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="공영주차장 정보",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 공영주차장 정보")

uploaded_file = st.file_uploader(
    "CSV 또는 Excel 파일 업로드",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

    st.success("업로드 완료!")

    st.subheader("데이터")

    st.dataframe(df)

    # 검색
    if "주차장명" in df.columns:
        keyword = st.text_input("주차장 검색")

        if keyword:
            df = df[df["주차장명"].str.contains(keyword, case=False, na=False)]

    # 요금 정렬
    if "요금" in df.columns:

        option = st.selectbox(
            "요금 정렬",
            ["기본", "낮은순", "높은순"]
        )

        if option == "낮은순":
            df = df.sort_values("요금")

        elif option == "높은순":
            df = df.sort_values("요금", ascending=False)

    st.subheader("정렬 결과")

    st.dataframe(df)

    # 다운로드
    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "정렬된 CSV 다운로드",
        csv,
        "parking_sorted.csv",
        "text/csv"
    )

    # 지도
    if {"위도","경도"}.issubset(df.columns):

        st.subheader("주차장 위치")

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[경도, 위도]',
            get_radius=50,
            get_fill_color=[255,0,0],
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=df["위도"].mean(),
            longitude=df["경도"].mean(),
            zoom=11
        )

        st.pydeck_chart(
            pdk.Deck(
                map_style="road",
                initial_view_state=view_state,
                layers=[layer],
                tooltip={
                    "text":"{주차장명}"
                }
            )
        )

else:
    st.info("데이터 파일을 업로드하세요.")
