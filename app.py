import streamlit as st
import requests
import os
from bs4 import BeautifulSoup
import urllib.parse
from email.utils import parsedate_to_datetime
from datetime import datetime

# ==========================================
# 🔐 AI 金鑰設定（已安全嵌入你的專屬金鑰）
# ==========================================
GEMINI_API_KEY = "AIzaSyAVAQ0go8bHnisnrdWZVyOkvdmY6f0YXT8"

# 設定網頁標籤頁標題與圖標
st.set_page_config(
    page_title="Luciffar Think Tank: Eye of Decision", 
    page_icon="logo.png" if os.path.exists("logo.png") else "👁️", 
    layout="centered"
)

# 🤖 核心函數：調用 Gemini API 進行即時新聞濃縮
def get_ai_summary(news_title):
    if not GEMINI_API_KEY or "請替換成" in GEMINI_API_KEY:
        return "⚠️ 未偵測到有效 AI 金鑰，無法進行濃縮。"
    
    # 使用目前最快、最省配額的 gemini-2.5-flash 模型
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # 建立給 AI 的促請詞（Prompt），嚴格限制格式以維持看板乾淨
    prompt = (
        f"你是一位精準的財經分析師。請根據以下這則新聞標題，"
        f"用繁體中文提供『一句話（25字內）的核心重點濃縮』，"
        f"語氣要嚴謹客觀、一針見血，不要廢話。新聞標題：{news_title}"
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        # 💡 已修正：改用標準的 status_code 進行判斷
        if response.status_code == 200:
            result = response.json()
            # 解析 Gemini 返回的文字
            summary = result['candidates'][0]['content']['parts'][0]['text']
            return summary.strip()
        else:
            return "❌ AI 模組暫時休眠中..."
    except Exception:
        return "⏱️ AI 運算逾時，請稍後重試。"

# 核心優化：將「決定版.jpg」與智庫標題完美融合成高級網頁 Banner 結構
if os.path.exists("logo.png"):
    col1, col2 = st.columns([1, 4]) 
    with col1:
        st.write("") 
        st.image("logo.png", use_container_width=True) 
    with col2:
        st.title("路西法智庫決策之眼 `v4.1` 🚀")
        st.subheader("Luciffar Think Tank: Eye of Decision")
else:
    st.title("👁️ 路西法智庫決策之眼 `v4.1` 🚀")
    st.subheader("Luciffar Think Tank: Eye of Decision")

st.caption("由 AI 時代技術驅動的即時財經聚合看板 • 獨立決策層核心工具")

# 數據時間與時區驗證說明
with st.expander("ℹ️ 數據時間與時區驗證說明 / Time Verification Info"):
    st.info("""
    本站情報時間由 **Google RSS 官方數據**即時驅動，若發現時間有些許落差，主因如下：
    1. **媒體後台更新**：部分財經媒體（如經濟日報、鉅亨網）在發布新聞後，會持續微調內文並更新網頁時間，本站抓取的是 **最初發布時間**。
    2. **跨國時區轉換**：駐外記者（如中央社駐歐美記者）發稿時，系統傳輸的標準格林威治時間（GMT）可能因部分媒體標籤不標準，導致與台灣本地時間產生時差。
    
    *※ 本站已內建標準台灣時區轉換與最即時排序，請安心閱讀！*
    """)

# 搜尋輸入框
search_target = st.text_input("🔍 請輸入想查詢的股票名稱、代號或關鍵字 (Stock Name, Code or Keywords)：", value="台積電")

# 手動重新整理按鈕
if st.button("🔄 重新整理新聞 (Refresh)"):
    st.rerun()

# 確保使用者有輸入東西才執行爬蟲邏輯
if search_target:
    encoded_query = urllib.parse.quote(search_target)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        with st.spinner(f"正在調閱「{search_target}」最新決策情報並啟動 AI 腦分析... / Analyzing..."):
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

        parsed_news.sort(key=lambda x: x["date_obj"] if x["date_obj"] else datetime.min, reverse=True)

        if parsed_news:
            st.success(f"決策之眼已鎖定 {min(15, len(parsed_news))} 則關於「{search_target}」的即時情報！")
            
            for index, item in enumerate(parsed_news[:15], 1):
                title = item["title"]
                link = item["link"]
                pub_date = item["date_str"]
                
                source_name = "新聞焦點"
                if " - " in title:
                    title, source_name = title.rsplit(" - ", 1)

                with st.container(border=True):
                    # 1. 渲染新聞連結與標題
                    st.markdown(f"### [{index}] [{title}]({link})")
                    
                    # 💡 2. 核心功能：調用 AI 對該標題進行即時一字濃縮分析
                    ai_brief = get_ai_summary(title)
                    st.markdown(f"💡 **AI 決策提煉**：`{ai_brief}`")
                    
                    col1_news, col2_news = st.columns([2, 1])
                    with col1_news:
                        st.caption(f"📅 發布時間 (Published): {pub_date}")
                    with col2_news:
                        st.markdown(f":blue[[{source_name}]]")
        else:
            st.warning(f"決策之眼未偵測到關於「{search_target}」的新聞，請換個關鍵字試試看！")

    except Exception as e:
        st.error(f"網站暫時無法連線，錯誤原因: {e}")
else:
    st.info("請在上方輸入框輸入股票關鍵字。")

# 網站底部的官方標準【免責聲明】
st.markdown("---")
st.caption(
    "**【免責聲明 / Disclaimer】** 本網站（路西法智庫決策之眼 / Luciffar Think Tank）僅為公開財經新聞之技術聚合測試看板，"
    "網頁內容與數據皆來自公開網路資訊。本站不提供任何形式的投資建議、個股推薦或操盤引導。"
    "市場投資具有風險，使用者依本站資訊所做出之任何投資決策，應自行承擔風險與盈虧，本站概不負責。"
)
