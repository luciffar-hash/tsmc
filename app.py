import streamlit as st
import requests
import os
from bs4 import BeautifulSoup
import urllib.parse
from email.utils import parsedate_to_datetime
from datetime import datetime

# ==========================================
# 1. 設定與金鑰（直接內嵌，保證生效）
# ==========================================
st.set_page_config(
    page_title="Luciffar Think Tank: Eye of Decision", 
    page_icon="logo.png" if os.path.exists("logo.png") else "👁️", 
    layout="centered"
)

GEMINI_API_KEY = "AIzaSyAVAQ0go8bHnisnrdWZVyOkvdmY6f0YXT8"

# ==========================================
# 2. AI 核心模組（精簡版，排查錯誤用）
# ==========================================
def get_ai_summary(news_title):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"請將以下財經新聞標題濃縮成一句話（25字內），要嚴謹客觀：{news_title}"}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=8)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return f"❌ 伺服器回應錯誤 (Code: {response.status_code})"
    except Exception as e:
        return f"❌ 連線失敗: {str(e)}"

# ==========================================
# 3. 網頁渲染邏輯
# ==========================================
if os.path.exists("logo.png"):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo.png", use_container_width=True)
    with col2:
        st.title("路西法智庫決策之眼 `v4.3`")
else:
    st.title("👁️ 路西法智庫決策之眼 `v4.3`")

# 搜尋框與重整
search_target = st.text_input("🔍 輸入關鍵字：", value="台積電")
if st.button("🔄 重新整理情報"):
    st.rerun()

# 數據處理
if search_target:
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(search_target)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    try:
        soup = BeautifulSoup(requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).content, "xml")
        items = soup.find_all("item")
        
        st.success(f"已鎖定 {len(items[:15])} 則情報")
        
        for item in items[:15]:
            title = item.title.text
            link = item.link.text
            
            with st.container(border=True):
                st.markdown(f"### [{title}]({link})")
                # AI 提煉顯示
                ai_result = get_ai_summary(title)
                st.markdown(f"💡 **AI 提煉**: `{ai_result}`")
                st.caption(f"📅 {item.pubDate.text}")
                
    except Exception as e:
        st.error(f"系統錯誤: {e}")
else:
    st.info("請輸入股票名稱")

st.markdown("---")
st.caption("【免責聲明】本站僅供資訊聚合測試，投資風險請自負。")
