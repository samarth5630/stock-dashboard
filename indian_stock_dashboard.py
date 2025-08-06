import streamlit as st
import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

st.set_page_config(page_title="Hexagon", layout="wide")
st.title("📊 Hexagon Stock Recommendation")

symbol = st.text_input("Enter NSE Stock Symbol (e.g. RELIANCE.NS):", "RELIANCE.NS")

if symbol:
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period="6mo")

        # Technical signal: moving average crossover
        hist['MA50'] = hist['Close'].rolling(50).mean()
        hist['MA200'] = hist['Close'].rolling(200).mean()
        latest = hist.iloc[-1]
        tech_signal = 'Buy' if latest['MA50'] > latest['MA200'] else 'Sell' if latest['MA50'] < latest['MA200'] else 'Hold'

        # News sentiment (via NewsAPI or simple fetched headlines)
        api_key = "733329e2d69a4cb2b32483a80a6b64c5"
        resp = requests.get(
            f"https://newsapi.org/v2/everything?q={symbol.split('.')[0]}&sortBy=publishedAt&apiKey={api_key}&pageSize=5"
        )
        sentiment = SentimentIntensityAnalyzer()
        news_text = ""
        news_sent = 0.0
        if resp.status_code == 200:
            articles = resp.json().get('articles', [])
            for art in articles:
                title = art.get('title', '')
                score = sentiment.polarity_scores(title)['compound']
                news_text += f"- {title} (score: {score:.2f})\n"
                news_sent += score
            news_sent_avg = news_sent / max(1, len(articles))
        else:
            news_text = "News fetch failed"
            news_sent_avg = 0.0

        # Combined recommendation
        if tech_signal == 'Buy' and news_sent_avg > 0.1:
            recommendation = "Strong Buy"
        elif tech_signal == 'Buy':
            recommendation = "Buy"
        elif tech_signal == 'Sell' and news_sent_avg < -0.1:
            recommendation = "Strong Sell"
        elif tech_signal == 'Sell':
            recommendation = "Sell"
        else:
            recommendation = "Hold"

        st.subheader(f"{info.get('longName','')} ({symbol})")
        col1, col2 = st.columns(2)
        col1.metric("Current Price", f"₹{info.get('currentPrice',0):.2f}")
        col1.metric("Market Cap", f"₹{int(info.get('marketCap',0)):,}")
        col2.metric("Tech Signal", tech_signal)
        col2.metric("Sentiment Score", f"{news_sent_avg:.2f}")

        st.markdown(f"## 🔍 Recommendation: **{recommendation}**")

        st.subheader("Let's see recent closing prices:")
        st.line_chart(hist['Close'])

        st.subheader("News headlines & sentiment:")
        st.text(news_text or "No articles found")

    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
else:
    st.info("Please enter a valid NSE symbol.")
