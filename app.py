import streamlit as st
import requests
import os
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

# ==========================================
# 1. 設定與金鑰 (v4.5 最終修正版)
# ==========================================
st.set_page_config(page_title="Luciffar Think Tank", page_icon="👁️", layout="centered")

GEMINI_API_KEY = "AIzaSyAVAQ0go8bHnisnrdWZVyOkvdmY6f0YXT8"

def get_ai_summary(news_title):
    # 使用最通用的 gemini-pro 模型，解決 404 問題
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"請將財經新聞標題：{news_title}，濃縮成一句話（25字內），嚴謹客觀。"}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return f"❌ 伺服器錯誤: {response.status_code}"
    except Exception as e:
        return f"❌ 連線失敗: {str(e)}"

# ==========================================
# 2. 網頁渲染 (保持你的簡潔高質感)
# ==========================================
st.title("路西法智庫決策之眼 `v4.5`")
search_target = st.text_input("🔍 輸入關鍵字：", value="台積電")

if st.button("🔄 重新整理"):
    st.rerun()

if search_target:
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(search_target)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    try:
        soup = BeautifulSoup(requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).content, "xml")
        items = soup.find_all("item")
        
        for item in items[:15]:
            with st.container(border=True):
                st.markdown(f"### [{item.title.text}]({item.link.text})")
                st.markdown(f"💡 **AI 提煉**: `{get_ai_summary(item.title.text)}`")
                st.caption(f"📅 {item.pubDate.text}")
    except Exception as e:
        st.error(f"連線失敗: {e}")
