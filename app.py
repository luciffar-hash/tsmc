import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from email.utils import parsedate_to_datetime
from datetime import datetime

# 設定網頁標籤頁標題與圖標
st.set_page_config(page_title="台股即時新聞看板 v2.0", page_icon="📈", layout="centered")

# 網頁主標題與版本號
st.title("📈 台股即時焦點新聞看板 `v2.0` 🚀")
st.caption("本網站由 Python 爬蟲即時驅動 • 升級版：支援自訂股票與時間排序")

# 搜尋輸入框（預設值為台積電，使用者可自行更改為其他股票名稱、代號或財經關鍵字）
search_target = st.text_input("🔍 請輸入想查詢的股票名稱、代號或關鍵字：", value="台積電")

# 手動重新整理按鈕
if st.button("🔄 重新整理新聞"):
    st.rerun()

# 確保使用者有輸入東西才執行爬蟲邏輯
if search_target:
    # 將中文或數字關鍵字進行網址編碼（URL Encoding）
    encoded_query = urllib.parse.quote(search_target)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        # 顯示載入中的動畫
        with st.spinner(f"正在擷取「{search_target}」最新市場動態..."):
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "xml")
            news_items = soup.find_all("item")

        parsed_news = []
        for item in news_items:
            title = item.title.text
            raw_date = item.pubDate.text
            link = item.link.text
            
            # 解析 Google RSS 的格林威治時間，並自動轉換為台灣在地時區（+8小時）
            try:
                dt_object = parsedate_to_datetime(raw_date).astimezone()
                formatted_date = dt_object.strftime("%Y-%m-%d %H:%M") # 轉換為年-月-日 時:分 格式
            except Exception:
                dt_object = None
                formatted_date = raw_date

            parsed_news.append({
                "title": title,
                "link": link,
                "date_obj": dt_object,
                "date_str": formatted_date
            })

        # 核心排序：利用 Python 懂的時間物件（date_obj）將新聞「由新到舊」完美洗牌
        # 若遇到沒有時間的新聞則自動放到最後面（datetime.min）
        parsed_news.sort(key=lambda x: x["date_obj"] if x["date_obj"] else datetime.min, reverse=True)

        # 顯示搜尋結果
        if parsed_news:
            st.success(f"成功找到 {min(15, len(parsed_news))} 則關於「{search_target}」的最新新聞！")
            
            # 僅抓取排序過後的前 15 則最新新聞顯示在網頁上
            for index, item in enumerate(parsed_news[:15], 1):
                title = item["title"]
                link = item["link"]
                pub_date = item["date_str"]
                
                # 切割新聞標題與媒體來源（Google RSS 的標題尾端通常會自帶 " - 媒體名稱"）
                source_name = "新聞焦點"
                if " - " in title:
                    title, source_name = title.rsplit(" - ", 1)

                # 使用 Streamlit 的容器元件，幫每則新聞畫上精美的對話框邊框
                with st.container(border=True):
                    st.markdown(f"### [{index}] [{title}]({link})")
                    
                    # 畫面左右分欄，左邊放發布時間，右邊放藍色的媒體標籤
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
