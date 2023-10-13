# LINE Chatbot with Movie Recommendation and ChatGPT API
LINE chatbot running on Render

## Prerequisites
- Python3, Pandas, Requests, Flask, Flask-SQLAlchemy, Psycopg2, LINE Messaging API SDK, OpenAI API
- [LINE Developers](https://developers.line.biz/en/) (Messaging API)
- [OpenAI](https://platform.openai.com/) (ChatGPT)
- [Render](https://render.com/) (Web Service, PostgreSQL)

## Description
- app.py: 程式主介面，
- dbpsql.py: PostgreSQL 資料庫的資料新增與讀取功能
- weather.py: 取得天氣狀況與空氣品質相關資訊的功能，參考自 [STEAM 教育學習網](https://steam.oxxostudio.tw/category/python/example/line-bot-weather-3.html)

## Dataset
- [KNN Movie Recommendation](https://github.com/Magic8763/knn_recommendation) 的 movies_sorted.csv 電影特徵資料集和 knn_recommended_sorted.csv 電影推薦結果
  - movies_sorted.csv: 根據上映年份遞增排序的 62423 部電影與其特徵
  - knn_recommended_sorted.csv: 7459 部電影各自的 50 近鄰

## Authors
* **Chih-Chien Cheng** - (categoryv@cycu.org.tw)
