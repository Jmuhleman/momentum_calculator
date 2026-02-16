import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Momentum Comparator", layout="wide")

st.title("📊 Multi-Asset Momentum Comparator")

# ==========================================
# Sidebar
# ==========================================
tickers_input = st.sidebar.text_input(
    "Tickers (comma separated)",
    value="SPY, QQQ, IWM, XLE"
)

tickers = [t.strip().upper() for t in tickers_input.split(",")]

lookback_months = st.sidebar.number_input(
    "Lookback (months)",
    min_value=1,
    max_value=24,
    value=12,
)

exclude_last_month = st.sidebar.checkbox(
    "Exclude most recent month (12-1)",
    value=True,
)

# ==========================================
# Data download
# ==========================================
end = datetime.today()
start = end - timedelta(days=lookback_months * 35 + 60)

@st.cache_data
def load_data(tickers, start, end):
    df = yf.download(tickers, start=start, end=end, auto_adjust=True)["Close"]
    return df

prices = load_data(tickers, start, end)

if prices.empty:
    st.error("No data.")
    st.stop()

# ==========================================
# Momentum calculation
# ==========================================
days_per_month = 21

results = []

for t in tickers:
    try:
        if exclude_last_month:
            end_idx = -days_per_month
        else:
            end_idx = -1

        price_end = prices[t].iloc[end_idx]
        price_start = prices[t].iloc[end_idx - lookback_months * days_per_month]

        mom = price_end / price_start - 1
        last_price = prices[t].iloc[-1]

        results.append([t, last_price, mom])

    except:
        results.append([t, None, None])

# ==========================================
# Table
# ==========================================
res_df = pd.DataFrame(results, columns=["Ticker", "Price", "Momentum"])

res_df = res_df.sort_values("Momentum", ascending=False)

st.subheader("🏆 Ranking")
st.dataframe(res_df)

# ==========================================
# Normalized chart
# ==========================================
st.subheader("📈 Normalized Performance")

norm_prices = prices / prices.iloc[0]
st.line_chart(norm_prices)

# ==========================================
# Momentum bars
# ==========================================
st.subheader("Momentum Comparison")

mom_series = res_df.set_index("Ticker")["Momentum"]
st.bar_chart(mom_series)

