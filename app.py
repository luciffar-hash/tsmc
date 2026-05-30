import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from email.utils import parsedate_to_datetime
from datetime import datetime # 💡 這裡！剛剛漏掉了這行，補上就完美了！

st.set_page_config(page_title="台積電新聞看板", page_icon="📈", layout="centered")

st.title("📈 TSMC 台積電最新焦點新聞")
st.caption("本網站由 Python 爬蟲即時驅動 • 依最新發布時間排序")

if st.button("🔄 重新整理新聞"):
    st.rerun()

query = "台積電"
encoded_query = urllib.parse.quote(query)
url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    with st.spinner("正在擷取最新市場動態..."):
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
        except Exception:
            dt_object = None
            formatted_date = raw_date

        parsed_news.append({
            "title": title,
            "link": link,
            "date_obj": dt_object,
            "date_str": formatted_date
        })

    # 這次 datetime 已經正確載入，排序絕對不會報錯了！
    parsed_news.sort(key=lambda x: x["date_obj"] if x["date_obj"] else datetime.min, reverse=True)

    for index, item in enumerate(parsed_news[:15], 1):
        title = item["title"]
        link = item["link"]
        pub_date = item["date_str"]
        
        source_name = "新聞焦點"
        if " - " in title:
            title, source_name = title.rsplit(" - ", 1)

        with st.container(border=True):
            st.markdown(f"### [{index}] [{title}]({link})")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.caption(f"📅 發布時間: {pub_date}")
            with col2:
                st.markdown(f":blue[[{source_name}]]")

except Exception as e:
    st.error(f"網站暫時無法連線，錯誤原因: {e}")
