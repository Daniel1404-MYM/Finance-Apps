import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# App Title
st.title("📈 Stock Market Visualizer with Buy/Sell Signals & Alerts")
st.sidebar.title("Options")

# Helper Functions
def fetch_stock_data(ticker, start_date, end_date):
    """Fetch stock data using yfinance."""
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date)

def plot_candlestick_with_signals(data, short_window, long_window):
    """Plot candlestick with Buy/Sell signals based on MA crossover."""
    # Hitung Moving Average sesuai input user
    data[f"MA{short_window}"] = data['Close'].rolling(window=short_window).mean()
    data[f"MA{long_window}"] = data['Close'].rolling(window=long_window).mean()

    # Generate Signals
    data['Signal'] = 0
    data['Signal'][long_window:] = np.where(
        data[f"MA{short_window}"][long_window:] > data[f"MA{long_window}"][long_window:], 1, -1
    )
    data['Position'] = data['Signal'].diff()

    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candlestick"
    ))

    # Moving Averages
    fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{short_window}"], 
                             line=dict(color='blue', width=1), 
                             name=f"MA{short_window}"))
    fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{long_window}"], 
                             line=dict(color='orange', width=1), 
                             name=f"MA{long_window}"))

    # Buy Signals
    buy_signals = data[data['Position'] == 2]
    fig.add_trace(go.Scatter(
        x=buy_signals.index, y=buy_signals['Close'],
        mode="markers", marker_symbol="triangle-up", marker_color="green",
        marker_size=12, name="Buy Signal"
    ))

    # Sell Signals
    sell_signals = data[data['Position'] == -2]
    fig.add_trace(go.Scatter(
        x=sell_signals.index, y=sell_signals['Close'],
        mode="markers", marker_symbol="triangle-down", marker_color="red",
        marker_size=12, name="Sell Signal"
    ))

    fig.update_layout(title=f"Candlestick with Buy/Sell Signals (MA{short_window} vs MA{long_window})", 
                      template="plotly_dark",
                      xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

    # ======================
    # 🔔 ALERT OTOMATIS
    # ======================
    if not data.empty:
        last_position = data['Position'].iloc[-1]
        last_close = data['Close'].iloc[-1]
        if last_position == 2:
            st.success(f"🔔 ALERT: BUY signal terdeteksi pada harga {last_close:.2f} ({data.index[-1].date()})")
        elif last_position == -2:
            st.error(f"🔔 ALERT: SELL signal terdeteksi pada harga {last_close:.2f} ({data.index[-1].date()})")
        else:
            st.info("ℹ️ Tidak ada sinyal baru pada data terbaru.")

    # Rekomendasi terakhir
    if not buy_signals.empty and (sell_signals.empty or buy_signals.index[-1] > sell_signals.index[-1]):
        st.success(f"✅ Rekomendasi: BUY pada harga {buy_signals['Close'].iloc[-1]:.2f}")
    elif not sell_signals.empty and (buy_signals.empty or sell_signals.index[-1] > buy_signals.index[-1]):
        st.error(f"⚠️ Rekomendasi: SELL pada harga {sell_signals['Close'].iloc[-1]:.2f}")
    else:
        st.info("ℹ️ Tidak ada rekomendasi kuat saat ini.")

def plot_volume(data):
    fig = px.bar(data, x=data.index, y='Volume', title="Trading Volume", template="plotly_dark")
    st.plotly_chart(fig)

def plot_daily_returns(data):
    data['Daily Return'] = data['Close'].pct_change() * 100
    fig = px.line(data, x=data.index, y='Daily Return', title="Daily Returns (%)", template="plotly_dark")
    st.plotly_chart(fig)

def plot_cumulative_returns(data):
    data['Cumulative Return'] = (1 + data['Close'].pct_change()).cumprod() - 1
    fig = px.line(data, x=data.index, y='Cumulative Return', title="Cumulative Returns", template="plotly_dark")
    st.plotly_chart(fig)

def plot_moving_averages(data, windows):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name="Close Price"))
    for window in windows:
        data[f"MA{window}"] = data['Close'].rolling(window=window).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{window}"], mode='lines', name=f"MA {window}"))
    fig.update_layout(title="Moving Averages", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
    st.plotly_chart(fig)

def plot_correlation_matrix(data):
    corr = data.corr()
    fig = px.imshow(corr, title="Correlation Matrix", template="plotly_dark", 
                    text_auto=True, color_continuous_scale='RdBu_r')
    st.plotly_chart(fig)

# Inputs
st.sidebar.header("Stock Selection")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL")
start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

data = fetch_stock_data(ticker, start_date, end_date)

# User pilih strategi buy/sell
st.sidebar.header("Buy/Sell Strategy")
short_window = st.sidebar.number_input("Short Moving Average", min_value=5, max_value=50, value=20)
long_window = st.sidebar.number_input("Long Moving Average", min_value=30, max_value=200, value=50)

# Visualizations
if not data.empty:
    st.subheader(f"Stock Data for {ticker}")
    st.write(data.tail())

    # Candlestick with Buy/Sell Signals & Alerts
    st.subheader("Candlestick Chart with Buy/Sell Signals")
    plot_candlestick_with_signals(data, short_window, long_window)

    # Volume Chart
    st.subheader("Volume Chart")
    plot_volume(data)

    # Daily Returns
    st.subheader("Daily Returns")
    plot_daily_returns(data)

    # Cumulative Returns
    st.subheader("Cumulative Returns")
    plot_cumulative_returns(data)

    # Moving Averages
    st.sidebar.header("Additional Moving Averages")
    moving_averages = st.sidebar.multiselect("Select Moving Averages (days)", 
                                             options=[10, 20, 50, 100, 200], 
                                             default=[20, 50])
    if moving_averages:
        st.subheader("Moving Averages")
        plot_moving_averages(data, moving_averages)

# Portfolio Correlation
st.sidebar.header("Portfolio Analysis")
portfolio_file = st.sidebar.file_uploader("Upload Portfolio (CSV or Excel)")
if portfolio_file:
    portfolio = pd.read_csv(portfolio_file) if portfolio_file.name.endswith("csv") else pd.read_excel(portfolio_file)
    tickers = portfolio['Ticker'].tolist()
    st.subheader("Portfolio Data")
    st.write(portfolio)

    portfolio_data = {t: fetch_stock_data(t, start_date, end_date)['Close'] for t in tickers}
    portfolio_df = pd.DataFrame(portfolio_data)
    st.subheader("Correlation Matrix")
    plot_correlation_matrix(portfolio_df)
