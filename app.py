import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 設定網頁標題與圖示（這會顯示在瀏覽器的分頁標籤上）
st.set_page_config(page_title="台積電新聞看板", page_icon="📈", layout="centered")

st.title("📈 TSMC 台積電最新焦點新聞")
st.caption("本網站由 Python 爬蟲即時驅動 • 點擊標題即可閱讀原文")

# 加一個「重新整理」的按鈕
if st.button("🔄 重新整理新聞"):
    st.rerun()

# 爬蟲核心邏輯
query = "台積電"
encoded_query = urllib.parse.quote(query)
url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    with st.spinner("正在擷取最新市場動態..."):
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "xml")
        news_items = soup.find_all("item")

    # 顯示新聞卡片
    for index, item in enumerate(news_items[:15], 1):
        title = item.title.text
        pub_date = item.pubDate.text
        link = item.link.text
        
        source_name = "新聞焦點"
        if " - " in title:
            title, source_name = title.rsplit(" - ", 1)

        # 使用 Streamlit 內建的 container 做出卡片效果
        with st.container(border=True):
            # 用 markdown 語法做出超連結標題
            st.markdown(f"### [{index}] [{title}]({link})")
            
            # 做出兩欄排版放時間與來源
            col1, col2 = st.columns([2, 1])
            with col1:
                st.caption(f"📅 發布時間: {pub_date}")
            with col2:
                st.markdown(f":blue[[{source_name}]]")

except Exception as e:
    st.error(f"網站暫時無法連線，錯誤原因: {e}")