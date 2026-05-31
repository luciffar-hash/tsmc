import streamlit as st
import requests
import os
from bs4 import BeautifulSoup
import urllib.parse

# 1. 品牌識別配置
st.set_page_config(
    page_title="Luciffar Think Tank", 
    page_icon="logo.png" if os.path.exists("logo.png") else "👁️", 
    layout="centered"
)

# 2. 視覺排版
if os.path.exists("logo.png"):
    col1, col2 = st.columns([1, 4]) 
    with col1:
        st.image("logo.png", use_container_width=True) 
    with col2:
        st.title("路西法智庫決策之眼 `v4.7`")
else:
    st.title("👁️ 路西法智庫決策之眼 `v4.7`")

# 3. 內容聚合 (保持穩定運作)
search_target = st.text_input("🔍 輸入關鍵字：", value="台積電")

if st.button("🔄 重新整理情報"):
    st.rerun()

if search_target:
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(search_target)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    try:
        soup = BeautifulSoup(requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).content, "xml")
        items = soup.find_all("item")
        
        st.success(f"已鎖定 {len(items[:15])} 則情報")
        
        for item in items[:15]:
            with st.container(border=True):
                st.markdown(f"### [{item.title.text}]({item.link.text})")
                st.caption(f"📅 {item.pubDate.text}")
    except Exception as e:
        st.error(f"情報讀取失敗: {e}")

st.markdown("---")
st.caption("【免責聲明】本站為公開資訊聚合看板。")
