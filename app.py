import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from email.utils import parsedate_to_datetime
from datetime import datetime

st.set_page_config(page_title="台股即時新聞看板", page_icon="📈", layout="centered")

st.title("📈 台股即時焦點新聞看板")
st.caption("本網站由 Python 爬蟲即時驅動 • 依最新發布時間排序")

# 💡 升級：新增股票搜尋功能，預設值一樣是台積電
search_target = st.text_input("🔍 請輸入想查詢的股票名稱、代號或關鍵字：", value="台積電")

if st.button("🔄 重新整理新聞"):
    st.rerun()

# 確保使用者有輸入東西才執行爬蟲
if search_target:
    encoded_query = urllib.parse.quote(search_target)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        with st.spinner(f"正在擷取「{search_target}」最新市場動態..."):
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

        # 根據時間物件進行「由新到舊」排序
        parsed_news.sort(key=lambda x: x["date_obj"] if x["date_obj"] else datetime.min, reverse=True)

        # 顯示搜尋結果
        if parsed_news:
            st.success(f"成功找到 {min(15, len(parsed_news))} 則關於「{search_target}」的最新新聞！")
            
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
        else:
            st.warning(f"找不到關於「{search_target}」的新聞，請換個關鍵字試試看！")

    except Exception as e:
        st.error(f"網站暫時無法連線，錯誤原因: {e}")
else:
    st.info("請在上方輸入框輸入股票關鍵字。")
