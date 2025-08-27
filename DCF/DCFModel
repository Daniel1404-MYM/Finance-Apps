import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from groq import Groq
from dotenv import load_dotenv

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# Streamlit App UI
st.set_page_config(page_title="DCF Valuation AI", page_icon="📊", layout="wide")
st.title("📊 DCF Valuation AI – Discounted Cash Flow Model")
st.write("Enter a stock ticker to fetch financial data and build a real-time DCF model!")

# User Input
company_name = st.text_input("🔍 Enter a Stock Ticker:", "AAPL")  # Default: Apple Inc.

if st.button("🚀 Generate DCF Model"):
    try:
        # Fetch financial data
        stock = yf.Ticker(company_name)
        financials = stock.financials.fillna(0)  # Avoid missing data
        cash_flow = stock.cashflow.fillna(0)  # Fix for missing cash flow items
        market_data = stock.history(period="1y")

        # Extract key financial data
        revenue = financials.loc["Total Revenue"].values[0] if "Total Revenue" in financials.index else 0
        net_income = financials.loc["Net Income"].values[0] if "Net Income" in financials.index else 0

        # Fix: Handle missing cash flow data
        operating_cash_flow = cash_flow.loc["Total Cash From Operating Activities"].values[0] if "Total Cash From Operating Activities" in cash_flow.index else 0
        capex = cash_flow.loc["Capital Expenditures"].values[0] if "Capital Expenditures" in cash_flow.index else 0

        free_cash_flow = operating_cash_flow - capex  # Free Cash Flow Calculation
        shares_outstanding = stock.info.get("sharesOutstanding", 1)
        risk_free_rate = 0.025  # Approximate risk-free rate (US 10-Year Treasury)

        # **User Input for DCF Assumptions**
        st.sidebar.header("📊 DCF Assumptions")
        growth_rate = st.sidebar.slider("Revenue Growth Rate (%)", 0, 20, 5) / 100
        discount_rate = st.sidebar.slider("Discount Rate (WACC) (%)", 1, 15, 10) / 100
        terminal_growth_rate = st.sidebar.slider("Terminal Growth Rate (%)", 0, 5, 2) / 100
        projection_years = st.sidebar.slider("Projection Period (Years)", 1, 10, 5)

        # **DCF Model Calculations**
        cash_flows = []
        for i in range(projection_years):
            free_cash_flow *= (1 + growth_rate)
            discounted_cash_flow = free_cash_flow / ((1 + discount_rate) ** (i + 1))
            cash_flows.append(discounted_cash_flow)

        terminal_value = (free_cash_flow * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
        discounted_terminal_value = terminal_value / ((1 + discount_rate) ** projection_years)
        total_enterprise_value = sum(cash_flows) + discounted_terminal_value
        intrinsic_value_per_share = total_enterprise_value / shares_outstanding

        # **Display DCF Results**
        st.subheader("📊 DCF Valuation Results")
        st.write(f"**Enterprise Value:** ${total_enterprise_value:,.2f}")
        st.write(f"**Intrinsic Value per Share:** ${intrinsic_value_per_share:,.2f}")
        st.write(f"**Current Market Price per Share:** ${stock.info.get('currentPrice', 'N/A')}")
        st.write(f"**Upside/Downside Potential:** {((intrinsic_value_per_share / stock.info.get('currentPrice', 1) - 1) * 100):.2f}%")

        # **Plot DCF Cash Flows**
        st.subheader("📈 Projected Free Cash Flows")
        years = list(range(1, projection_years + 1))
        fig_dcf = go.Figure()
        fig_dcf.add_trace(go.Bar(x=years, y=cash_flows, name="Discounted Cash Flow", marker_color="blue"))
        fig_dcf.add_trace(go.Scatter(x=[projection_years], y=[discounted_terminal_value], name="Terminal Value", mode="markers", marker=dict(size=10, color="red")))
        fig_dcf.update_layout(title=f"{company_name} Projected Free Cash Flows", xaxis_title="Years", yaxis_title="Cash Flow (USD)", template="plotly_dark")
        st.plotly_chart(fig_dcf)

        # **AI-Powered Valuation Insights**
        st.subheader("🤖 AI-Powered Valuation Insights")

        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI financial analyst providing insights on Discounted Cash Flow (DCF) valuation models."},
                {"role": "user", "content": f"Here is the DCF valuation summary for {company_name}:\n"
                                            f"Revenue Growth Rate: {growth_rate*100:.2f}%\n"
                                            f"Discount Rate (WACC): {discount_rate*100:.2f}%\n"
                                            f"Terminal Growth Rate: {terminal_growth_rate*100:.2f}%\n"
                                            f"Enterprise Value: ${total_enterprise_value:,.2f}\n"
                                            f"Intrinsic Value per Share: ${intrinsic_value_per_share:,.2f}\n"
                                            f"Current Market Price: ${stock.info.get('currentPrice', 'N/A')}\n"
                                            f"What are the key insights and investment considerations based on this valuation?"}
            ],
            model="llama3-8b-8192",
        )

        st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"⚠️ Error fetching financial data: {e}")
