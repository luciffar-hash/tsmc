import streamlit as st
import requests
import os
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

# ==========================================
# 1. 設定
# ==========================================
st.set_page_config(
    page_title="Luciffar Think Tank: Eye of Decision", 
    page_icon="logo.png" if os.path.exists("logo.png") else "👁️", 
    layout="centered"
)

GEMINI_API_KEY = "AIzaSyAVAQ0go8bHnisnrdWZVyOkvdmY6f0YXT8"

# ==========================================
# 2. AI 核心模組 (修正路徑與參數)
# ==========================================
def get_ai_summary(news_title):
    # 修正後的穩定 API 路徑
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": f"請將以下財經新聞標題濃縮成一句話（25字內），要嚴謹客觀：{news_title}"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return f"❌ API 錯誤: {response.status_code} - 請檢查 API Key 權限"
    except Exception as e:
        return f"❌ 連線異常: {str(e)}"

# ==========================================
# 3. 網頁渲染
# ==========================================
if os.path.exists("logo.png"):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo.png", use_container_width=True)
    with col2:
        st.title("路西法智庫決策之眼 `v4.4`")
else:
    st.title("👁️ 路西法智庫決策之眼 `v4.4`")

search_target = st.text_input("🔍 輸入關鍵字：", value="台積電")

if st.button("🔄 重新整理情報"):
    st.rerun()

if search_target:
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(search_target)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        
        st.success(f"已鎖定 {len(items[:15])} 則情報")
        
        for item in items[:15]:
            title = item.title.text
            link = item.link.text
            
            with st.container(border=True):
                st.markdown(f"### [{title}]({link})")
                # 執行 AI 提煉
                ai_result = get_ai_summary(title)
                st.markdown(f"💡 **AI 提煉**: `{ai_result}`")
                st.caption(f"📅 {item.pubDate.text}")
                
    except Exception as e:
        st.error(f"RSS 讀取失敗: {e}")
else:
    st.info("請輸入關鍵字以開始情報分析。")

st.markdown("---")
st.caption("【免責聲明】本站內容聚合自網路公開資訊。")
