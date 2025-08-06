import streamlit as st
import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

# Page config
st.set_page_config(page_title="Hexagon", page_icon="📈", layout="wide")

# Logo and title
st.markdown("""
    <div style='text-align: center; padding: 20px'>
        <img src='https://raw.githubusercontent.com/Hexagonfcc/stock-dashboard/main/hexagon_logo.png' width='80'/>
        <h1 style='font-size: 40px; color: #222;'>Hexagon</h1>
        <p style='font-size: 18px; color: gray;'>Smarter Stock Insights. Instantly.</p>
    </div>
""", unsafe_allow_html=True)

# Input
symbol = st.text_input("🔎 Enter NSE Stock Symbol (e.g., RELIANCE.NS):", "RELIANCE.NS")

if symbol:
    try:
        # Fetch stock data
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period="6mo")

        # Moving Averages
        hist['MA50'] = hist['Close'].rolling(50).mean()
        hist['MA200'] = hist['Close'].rolling(200).mean()
        latest = hist.iloc[-1]
        tech_signal = 'Buy' if latest['MA50'] > latest['MA200'] else 'Sell' if latest['MA50'] < latest['MA200'] else 'Hold'

        # Sentiment Analysis (optional fallback without NewsAPI)
        headlines = [
            f"{info.get('longName', symbol)} sees steady growth amid market volatility.",
            "Investors are eyeing this stock after recent financial reports.",
            "Analysts suggest this could be a good time to review positions."
        ]
        sentiment = SentimentIntensityAnalyzer()
        scores = [sentiment.polarity_scores(h)['compound'] for h in headlines]
        avg_sent = sum(scores) / len(scores)

        # Final Recommendation
        if tech_signal == 'Buy' and avg_sent > 0.1:
            recommendation = "✅ Strong Buy"
        elif tech_signal == 'Buy':
            recommendation = "Buy"
        elif tech_signal == 'Sell' and avg_sent < -0.1:
            recommendation = "❌ Strong Sell"
        elif tech_signal == 'Sell':
            recommendation = "Sell"
        else:
            recommendation = "Hold"

        # Layout
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"₹{info.get('currentPrice', 0):,.2f}")
        col2.metric("52 Week High", f"₹{info.get('fiftyTwoWeekHigh', 0):,.2f}")
        col3.metric("52 Week Low", f"₹{info.get('fiftyTwoWeekLow', 0):,.2f}")

        col4, col5, col6 = st.columns(3)
        col4.metric("Market Cap", f"₹{info.get('marketCap', 0):,}")
        col5.metric("Tech Signal", tech_signal)
        col6.metric("Sentiment Score", f"{avg_sent:.2f}")

        # Recommendation Box
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; border-radius: 12px; background-color: #f2f2f2; margin-top: 30px;'>
            <h2 style='color: #1a1a1a;'>📊 Recommendation</h2>
            <p style='font-size: 24px; font-weight: bold; color: #0077cc;'>{recommendation}</p>
        </div>
        """, unsafe_allow_html=True)

        # Chart
        st.markdown("### 📉 Stock Price (6 months)")
        st.line_chart(hist[['Close', 'MA50', 'MA200']])

        # News Headlines (mock)
        st.markdown("### 📰 News Sentiment Headlines")
        for headline, score in zip(headlines, scores):
            st.markdown(f"- {headline} (Sentiment: `{score:.2f}`)")

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
else:
    st.info("Please enter a valid NSE stock symbol like `TCS.NS` or `INFY.NS`.")
