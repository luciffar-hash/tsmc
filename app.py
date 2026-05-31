import streamlit as st
import requests
import os
from bs4 import BeautifulSoup
import urllib.parse

# ==========================================
# 1. 基礎設定與 Logo 邏輯
# ==========================================
st.set_page_config(
    page_title="Luciffar Think Tank", 
    page_icon="logo.png" if os.path.exists("logo.png") else "👁️", 
    layout="centered"
)

if os.path.exists("logo.png"):
    col1, col2 = st.columns([1, 4])
    with col1: st.image("logo.png", use_container_width=True)
    with col2: st.title("路西法智庫決策之眼 `v4.3`")
else:
    st.title("👁️ 路西法智庫決策之眼 `v4.3`")

# ==========================================
# 2. 資訊聚合 (純淨穩定版)
# ==========================================
search_target = st.text_input("🔍 輸入關鍵字：", value="台積電")

if st.button("🔄 重新整理情報"):
    st.rerun()

if search_target:
    # 確保 RSS 請求格式最穩定
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(search_target)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        
        if not items:
            st.warning("目前無相關情報。")
        else:
            for item in items[:15]:
                with st.container(border=True):
                    # 直接連結與標題
                    st.markdown(f"### [{item.title.text}]({item.link.text})")
                    # 顯示原始日期
                    st.caption(f"📅 {item.pubDate.text}")
                    
    except Exception as e:
        st.error(f"情報讀取失敗，請稍後再試。原因: {e}")
else:
    st.info("請輸入關鍵字以開始情報分析。")

st.markdown("---")
st.caption("【系統狀態】已回滾至純聚合模式 (v4.3)。")
