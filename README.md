# LINE Chatbot with Movie Recommendation and ChatGPT
LINE chatbot running on Render.

，同時採用 Python threading 模組，實現能同時處理多位用戶的請求的能力

本專題以智慧電影推薦機器人為題材，以 Python 開發 Chatbot 基本架構，
導入基於 Python 與 TensorFlow 的電影推薦演算法，並透過 Heroku 雲端運算平
台以 LINE Bot 訊息介面呈現。
藉由這次專題能了解 Chatbot 的架構設計，雲端運算平台的運作方式，資料
庫數據的應用，AI 演算法的使用與分析，以及其他輔助功能的運用，進而整合
所有技術，完善整個系統，提升應用品質與效能。
 本專題主要利用 Chatbot 與 LINE 用戶的互動，推薦出多部符合使用者喜好
的電影。使用者檢閱完一部電影的資訊後，能夠自由給予電影評分，個人的評分
紀錄能反映出一位使用者偏好的電影類型與喜好程度。而推薦演算法結合個人評
分紀錄與過往的歷史數據，構建出預測模型並加以訓練，最後得出個人專屬的推
薦電影清單。 

智慧電影推薦機器人是以 TensorFlow 電影推薦演算法為核心，使用源自於
Movielens 的大量用戶評分紀錄進行模型訓練，其運算結果將與 LINE Bot 訊息
介面整合，並經由 Heroku 雲端運算平台與 LINE server 發送給該使用者的 LINE
App 窗口。除了主要的推薦系統之外，同時具備基本的電影查找功能，例如以片
名關鍵字或檔期進行電影搜尋。
 對使用者而言，所有操作僅在 LINE App 上進行，不必安裝其他應用，不用
進行軟體更新，也不會額外佔用儲存空間，具有高度穩定性與輕便性。 

## Prerequisites
- Python3, Pandas, Requests, Flask, Flask-SQLAlchemy, Psycopg2, LINE Messaging API SDK, OpenAI API
- [LINE Developers](https://developers.line.biz/en/) (Messaging API)
- [OpenAI](https://platform.openai.com/) (ChatGPT API)
- [Render](https://render.com/) (Web Service, PostgreSQL)

## Description
- app.py: 程式主體，針對 LINE 用戶的請求做出相應的回覆
- dbpsql.py: PostgreSQL 資料庫的資料新增與讀取功能
- weather.py: 取得天氣狀況與空氣品質資訊的相關功能，參考自 [STEAM 教育學習網](https://steam.oxxostudio.tw/category/python/example/line-bot-weather-3.html)

## Dataset
- [KNN Movie Recommendation](https://github.com/Magic8763/knn_recommendation) 的 movies_sorted.csv 和 knn_recommended_sorted.csv
  - movies_sorted.csv: 電影特徵資料集，根據上映年份遞增排序的 62423 部電影與其特徵
  - knn_recommended_sorted.csv: 電影推薦矩陣，分別與 7459 部電影高度相似的前 50 部其他電影

## Screenshot



## Authors
* **Chih-Chien Cheng** - (categoryv@cycu.org.tw)
