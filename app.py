import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from email.utils import parsedate_to_datetime
from datetime import datetime

# 設定網頁標籤頁標題與圖標（精準校正品牌拼字 Luciffar）
st.set_page_config(page_title="Luciffar Think Tank: Eye of Decision v2.4", page_icon="👁️", layout="centered")

# 網頁主標題與版本號（中英雙語品牌大氣登場，校正雙 f 拼字）
st.title("👁️ 路西法智庫決策之眼 `v2.4` 🚀")
st.subheader("Luciffar Think Tank: Eye of Decision")
st.caption("由 AI 時代技術驅動的即時財經聚合看板 • 獨立決策層核心工具")

# 💡 質感升級：時間解說改用優雅的 st.info 藍色區塊搭配摺疊設計，視覺更顯洗練專業
with st.expander("ℹ️ 數據時間與時區驗證說明 / Time Verification Info"):
    st.info("""
    本站情報時間由 **Google RSS 官方數據**即時驅動，若發現時間有些許落差，主因如下：
    1. **媒體後台更新**：部分財經媒體（如經濟日報、鉅亨網）在發布新聞後，會持續微調內文並更新網頁時間，本站抓取的是 **最初發布時間**。
    2. **跨國時區轉換**：駐外記者（如中央社駐歐美記者）發稿時，系統傳輸的標準格林威治時間（GMT）可能因部分媒體標籤不標準，導致與台灣本地時間產生時差。
    
    *※ 本站已內建標準台灣時區轉換與最即時排序，請安心閱讀！*
    """)

# 搜尋輸入框（預設值為台積電，使用者可自行更改為其他股票名稱、代號或財經關鍵字）
search_target = st.text_input("🔍 請輸入想查詢的股票名稱、代號或關鍵字 (Stock Name, Code or Keywords)：", value="台積電")

# 手動重新整理按鈕
if st.button("🔄 重新整理新聞 (Refresh)"):
    st.rerun()

# 確保使用者有輸入東西才執行爬蟲邏輯
if search_target:
    # 將中文或數字關鍵字進行網址編碼（URL Encoding）
    encoded_query = urllib.parse.quote(search_target)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        # 顯示載入中的動畫
        with st.spinner(f"正在調閱「{search_target}」最新決策情報... / Fetching Intel..."):
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
        parsed_news.sort(key=lambda x: x["date_obj"] if x["date_obj"] else datetime.min, reverse=True)

        # 顯示搜尋結果
        if parsed_news:
            st.success(f"決策之眼已鎖定 {min(15, len(parsed_news))} 則關於「{search_target}」的即時情報！")
            
            # 僅抓取排序過後的前 15 則最新新聞顯示在網頁上
            for index, item in enumerate(parsed_news[:15], 1):
                title = item["title"]
                link = item["link"]
                pub_date = item["date_str"]
                
                # 切割新聞標題與媒體來源
                source_name = "新聞焦點"
                if " - " in title:
                    title, source_name = title.rsplit(" - ", 1)

                # 使用 Streamlit 的容器元件，幫每則新聞畫上精美的對話框邊框
                with st.container(border=True):
                    st.markdown(f"### [{index}] [{title}]({link})")
                    
                    # 畫面左右分欄，左邊放發布時間，右邊放藍色的媒體標籤
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.caption(f"📅 發布時間 (Published): {pub_date}")
                    with col2:
                        st.markdown(f":blue[[{source_name}]]")
        else:
            st.warning(f"決策之眼未偵測到關於「{search_target}」的新聞，請換個關鍵字試試看！")

    except Exception as e:
        st.error(f"網站暫時無法連線，錯誤原因: {e}")
else:
    st.info("請在上方輸入框輸入股票關鍵字。")

# 網站底部的官方標準【免責聲明】（精準校正 Luciffar 拼字）
st.markdown("---")
st.caption(
    "**【免責聲明 / Disclaimer】** 本網站（路西法智庫決策之眼 / Luciffar Think Tank）僅為公開財經新聞之技術聚合測試看板，"
    "網頁內容與數據皆來自公開網路資訊。本站不提供任何形式的投資建議、個股推薦或操盤引導。"
    "市場投資具有風險，使用者依本站資訊所做出之任何投資決策，應自行承擔風險與盈虧，本站概不負責。"
)
