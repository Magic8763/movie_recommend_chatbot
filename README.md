# LINE Chatbot with Movie Recommendation and ChatGPT
本專案為具有電影推薦和 ChatGPT 功能的 LINE 聊天機器人，我們以 Python 開發聊天機器人的基本架構，設計具有查詢與推薦功能的電影資料庫介面，並導入 ChatGPT API 來回應用戶的文字訊息。

藉由用戶與聊天機器人的互動，系統會逐漸更新電影推薦清單，得出符合用戶近期偏好的專屬內容。

採用 Python threading 模組，實現能同時處理複數請求而不衝突的穩定性。

對使用者而言，所有操作僅在 LINE App 上進行，不必安裝其他應用，不用進行軟體更新，也不會佔用任何儲存空間，具有高度輕便性。 

## Prerequisites
- Python3, Pandas, Requests, Flask, Flask-SQLAlchemy, Psycopg2, LINE Messaging API SDK, OpenAI API
- [LINE Developers](https://developers.line.biz/en/) (Messaging API)
- [OpenAI](https://platform.openai.com/) (ChatGPT API)
- [Render](https://render.com/) (Web Service, PostgreSQL)

## Description
- app.py: 程式主體，針對 LINE 用戶的請求做出對應的回覆
- dbpsql.py: PostgreSQL 資料庫的資料新增與讀取功能
- weather.py: 取得天氣狀況與空氣品質資訊的相關功能，參考自 [STEAM 教育學習網](https://steam.oxxostudio.tw/category/python/example/line-bot-weather-3.html)

## Dataset
- [KNN Movie Recommendation](https://github.com/Magic8763/knn_recommendation) 的 movies_sorted.csv 和 knn_recommended_sorted.csv
  - movies_sorted.csv: 電影特徵資料集，根據上映年份遞增排序的 62423 部電影與其特徵
  - knn_recommended_sorted.csv: 由 KNN 模型計算所得的電影推薦矩陣，包含與 7459 部相異電影各自高度相似的 50 部其他電影

## Screenshot



## Authors
* **Chih-Chien Cheng** - (categoryv@cycu.org.tw)
