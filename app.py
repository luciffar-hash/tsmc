import streamlit as st
import requests
import os
from bs4 import BeautifulSoup
import urllib.parse
from email.utils import parsedate_to_datetime
from datetime import datetime

# 設定網頁標籤頁標題與圖標
st.set_page_config(
    page_title="Luciffar Think Tank: Eye of Decision", 
    page_icon="logo.png" if os.path.exists("logo.png") else "👁️", 
    layout="centered"
)

# 🛠️ 強化版 AI 金鑰讀取機制
# 優先嘗試從 Streamlit Cloud Secrets 讀取，若無則使用寫死的 Key 作為備援
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = "AIzaSyAVAQ0go8bHnisnrdWZVyOkvdmY6f0YXT8"

def get_ai_summary(news_title):
    if not GEMINI_API_KEY:
        return "⚠️ 未偵測到 API 金鑰"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        f"你是一位精準的財經分析師。請根據新聞標題：『{news_title}』，"
        f"用繁體中文提供一句話（25字內）的核心重點濃縮，嚴謹客觀，不廢話。"
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return "❌ AI 模組暫時休眠中..."
    except:
        return "⏱️ AI 運算逾時"

# 渲染 Banner
if os.path.exists("logo.png"):
    col1, col2 = st.columns([1, 4]) 
    with col1:
        st.write("") 
        st.image("logo.png", use_container_width=True) 
    with col2:
        st.title("路西法智庫決策之眼 `v4.2` 🚀")
        st.subheader("Luciffar Think Tank: Eye of Decision")
else:
    st.title("👁️ 路西法智庫決策之眼 `v4.2` 🚀")
    st.subheader("Luciffar Think Tank: Eye of Decision")

st.caption("由 AI 時代技術驅動的即時財經聚合看板 • 獨立決策層核心工具")

# 搜尋與處理邏輯
search_target = st.text_input("🔍 請輸入想查詢的股票名稱、代號或關鍵字：", value="台積電")

if st.button("🔄 重新整理新聞 (Refresh)"):
    st.rerun()

if search_target:
    encoded_query = urllib.parse.quote(search_target)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        with st.spinner("正在調閱情報並進行 AI 提煉..."):
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "xml")
            news_items = soup.find_all("item")

        parsed_news = []
        for item in news_items:
            title = item.title.text
            raw_date = item.pubDate.text
            link = item.link.text
            
            try:
                dt_object = parsedate_to_datetime(raw_date).astimezone()
                formatted_date = dt_object.strftime("%Y-%m-%d %H:%M")
            except:
                dt_object = None
                formatted_date = raw_date

            parsed_news.append({
                "title": title,
                "link": link,
                "date_obj": dt_object,
                "date_str": formatted_date
            })

        parsed_news.sort(key=lambda x: x["date_obj"] if x["date_obj"] else datetime.min, reverse=True)

        for index, item in enumerate(parsed_news[:15], 1):
            with st.container(border=True):
                st.markdown(f"### [{index}] [{item['title']}]({item['link']})")
                st.markdown(f"💡 **AI 決策提煉**：`{get_ai_summary(item['title'])}`")
                col1_news, col2_news = st.columns([2, 1])
                with col1_news:
                    st.caption(f"📅 發布時間: {item['date_str']}")
    except Exception as e:
        st.error(f"連線錯誤: {e}")
else:
    st.info("請輸入股票名稱。")

st.markdown("---")
st.caption("**【免責聲明】本站僅為公開財經資訊聚合，不構成投資建議。**")
