import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(
    page_title="Global Top10 Market Cap Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("🌍 Global Market Cap TOP10 Stocks")
st.markdown("### 최근 1년간 글로벌 시가총액 TOP10 기업 주가 비교")

# 글로벌 시가총액 Top10 (2025 기준)
companies = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Saudi Aramco": "2222.SR",
    "Broadcom": "AVGO",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-B"
}

selected = st.multiselect(
    "기업 선택",
    list(companies.keys()),
    default=list(companies.keys())
)

if len(selected) == 0:
    st.warning("기업을 선택하세요.")
    st.stop()

tickers = [companies[c] for c in selected]

@st.cache_data(ttl=3600)
def load_data(tickers):
    data = yf.download(
        tickers=tickers,
        period="1y",
        auto_adjust=True,
        progress=False
    )

    close = data["Close"]

    if isinstance(close, pd.Series):
        close = close.to_frame()

    return close

prices = load_data(tickers)

# 컬럼명을 회사명으로 변경
rename_dict = {}
for name, ticker in companies.items():
    if ticker in prices.columns:
        rename_dict[ticker] = name

prices.rename(columns=rename_dict, inplace=True)

# 누적수익률 계산
returns = prices / prices.iloc[0] * 100

tab1, tab2 = st.tabs(["📈 Stock Price", "📊 Cumulative Return"])

with tab1:

    fig = px.line(
        prices,
        x=prices.index,
        y=prices.columns,
        labels={
            "value":"Price",
            "variable":"Company"
        },
        title="Stock Price (1 Year)"
    )

    fig.update_layout(
        height=650,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:

    fig2 = px.line(
        returns,
        x=returns.index,
        y=returns.columns,
        labels={
            "value":"Return Index",
            "variable":"Company"
        },
        title="Cumulative Return (%)"
    )

    fig2.update_layout(
        height=650,
        hovermode="x unified"
    )

    st.plotly_chart(fig2, use_container_width=True)

st.divider()

latest = pd.DataFrame({
    "Latest Price": prices.iloc[-1],
    "Return (%)": ((prices.iloc[-1]/prices.iloc[0])-1)*100
})

latest = latest.sort_values(
    "Return (%)",
    ascending=False
)

latest["Latest Price"] = latest["Latest Price"].round(2)
latest["Return (%)"] = latest["Return (%)"].round(2)

st.subheader("📋 Performance Summary")

st.dataframe(
    latest,
    use_container_width=True
)

st.bar_chart(latest["Return (%)"])

st.caption("Data Source : Yahoo Finance")
