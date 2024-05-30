# Movie Recommendation Chatbot
![](https://img.shields.io/github/stars/magic8763/movie_recommend_chatbot)
![](https://img.shields.io/github/watchers/magic8763/movie_recommend_chatbot)
![](https://img.shields.io/github/forks/magic8763/movie_recommend_chatbot)
![shields](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)

本專案為採用 Flask 框架開發的 LINE 聊天機器人，具有可供查詢與推薦電影的整合介面，並導入 ChatGPT 回應用戶的文字訊息。

隨著用戶與聊天機器人的互動，系統會動態更新電影推薦清單，得出符合用戶近期偏好的專屬內容。

用戶所有操作只需在 LINE App 上進行，不必安裝其他應用，無需定期更新軟體，也不會佔用額外儲存空間，具有高度輕便性。 

另外整合了 ChatGPT 和天氣資訊 API 等泛用功能，提供多元化服務。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/structure.jpg)

## Demo
**電影推薦**
>輸入「@電影推薦機器人」觸發機器人返回電影推薦首頁介面。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Menu.jpg)

>點擊首頁的「最新電影」按鈕或輸入「@電影推薦機器人：最新電影」，返回上映日期最近的數部電影。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Get_New.jpg)

>點擊首頁的「關鍵字搜尋」按鈕或輸入「@電影推薦機器人：關鍵字搜尋」，接著輸入關鍵字，返回片名與其相符的所有電影。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Keyword_Search.jpg)

>點擊首頁的「智慧推薦」按鈕或輸入「@電影推薦機器人：智慧推薦」，返回與用戶近期查詢偏好相近的電影。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Get_Recommended.jpg)

>點擊電影模板的「同類推薦」按鈕，返回與該電影類型相同的電影清單。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Get_Similar.jpg)

>點擊電影模板的「給予評分」按鈕，接著輸入 1 ~ 10 之間的分數給予評分。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Score_message.jpg)

>點擊首頁的「評分紀錄」按鈕或輸入「@電影推薦機器人：評分紀錄」，返回用戶最近 10 筆電影評分。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Read_Personal_Record.jpg)

**ChatGPT**
>非'@'前綴的文字訊息將由 ChatGPT 進行回應。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Call_ChatGPT.jpg)

**天氣資訊**
>輸入「@地震資訊」，返回最近的中央氣象署地震報告。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Get_Earthquake.jpg)

>輸入「@氣象雷達」，返回最近的中央氣象署雷達合成回波圖。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Get_RadarEcho.jpg)

>從 LINE app 分享位置訊息，返回該地點的天氣資訊。

![image](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/img/Get_Weather.jpg)

## Prerequisites
- Python3, Flask, Flask-RESTful, Flask-SQLAlchemy, Psycopg2, Requests, Pandas, NumPy, Surprise, LINE Messaging API SDK, OpenAI API
- [LINE Official Account](https://manager.line.biz/) (建立機器人帳戶)
- [LINE Developers](https://developers.line.biz/en/) (串接 Messaging API)
- [OpenAI](https://platform.openai.com/) (串接 ChatGPT API)
- [Render](https://render.com/) (Web Service, PostgreSQL)

## Description
- `app.py`: 程式主體，提供電影推薦和 ChatGPT 功能，並回覆 LINE 用戶的請求
- `dbpsql.py`: PostgreSQL 資料庫的資料新增與查詢功能
- `weather.py`: 天氣資訊 API 相關功能

## Dataset & Model
- [Movie Recommendation Model](https://github.com/Magic8763/knn_svd_recommendation)
  - `movies@0x1000_1M_compactify.csv`: 電影特徵資料集，根據上映年份遞增排序的 62423 部電影與其特徵
  - `knn_recommended_sorted.csv`: 以 KNN 模型生成的電影推薦矩陣，包含與 3794 部電影各自高度相似的 50 部其他電影, 用於冷啟動 (*Cold Start*) 電影推薦
  - `SVD++_best@0x1000_1M.pkl`: 預訓練的 Surprise SVD++ 模型, 能預測指定用戶對任一電影的評分, 用於熱啟動 (*Warm Start*) 電影推薦

## Reference
- [LINE BOT 教學](https://steam.oxxostudio.tw/category/python/example/line-bot-weather-3.html) - STEAM 教育學習網

## Authors
* **[Magic8763](https://github.com/Magic8763)**

## License
This project is licensed under the [MIT License](https://github.com/Magic8763/movie_recommend_chatbot/blob/main/LICENSE)
