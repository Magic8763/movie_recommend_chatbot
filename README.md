# Movie Recommendation Chatbot
![](https://img.shields.io/github/stars/magic8763/linebot_on_Render)
![](https://img.shields.io/github/watchers/magic8763/linebot_on_Render)
![](https://img.shields.io/github/forks/magic8763/linebot_on_Render)
![shields](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)

本專案為基於 Flask 框架所開發的 LINE 聊天機器人，具有可供查詢與推薦電影的操作介面，並導入 ChatGPT 回應用戶的文字訊息。

透過用戶與聊天機器人的互動，系統會逐漸更新電影推薦清單，得出符合用戶近期偏好的專屬內容。

對使用者而言，所有操作僅在 LINE App 上進行，不必安裝其他應用，不用進行軟體更新，也不會佔用任何儲存空間，具有高度輕便性。 

## Demo
**電影推薦**
>首頁介面

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Menu.jpg)

>點擊首頁的"近期上映"按鈕或輸入"@電影推薦機器人：近期上映"，返回上映日期最近的幾部電影。

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Get_Playing2.jpg)

>點擊首頁的"關鍵字搜尋"按鈕或輸入"@電影推薦機器人：關鍵字搜尋"，接著輸入關鍵字，返回片名與其相符的所有電影。

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Keyword_Search.jpg)

>點擊首頁的"智慧推薦"按鈕或輸入"@電影推薦機器人：智慧推薦"，返回推薦給用戶的幾部電影。

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Recommend2.jpg)

>點擊首頁的"評分紀錄"按鈕或輸入"@電影推薦機器人：評分紀錄"，返回用戶最近 10 筆電影評分。

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Read_Personal_Record.jpg)

>點擊電影模板的"給予評分"按鈕，接著輸入 1 ~ 10 之間的分數給予評分。

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Score_message.jpg)

>點擊電影模板的"同類推薦"按鈕，返回與該電影類型相同的電影清單。

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Same_Category3.jpg)

**ChatGPT**
>非"@電影推薦機器人"前綴的文字訊息將由 ChatGPT 進行回應。

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Call_ChatGPT.jpg)

**天氣狀況**
>輸入"@地震資訊"，返回最近的中央氣象署地震報告。

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Get_Earthquake.jpg)

>輸入"@雷達回波圖"，返回最近的中央氣象署雷達合成回波圖。

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Get_RadarEcho.jpg)

>分享位置資訊，返回該地點的天氣資訊。

![image](https://github.com/Magic8763/linebot_on_Render/blob/main/img/Get_Weather.jpg)

## Prerequisites
- Python3, Pandas, Requests, Flask, Flask-SQLAlchemy, Psycopg2, LINE Messaging API SDK, OpenAI API
- [LINE Official Account](https://manager.line.biz/) (建立機器人帳戶)
- [LINE Developers](https://developers.line.biz/en/) (串接 Messaging API)
- [OpenAI](https://platform.openai.com/) (串接 ChatGPT API)
- [Render](https://render.com/) (Web Service, PostgreSQL)

## Description
- `app.py`: 程式主體，針對 LINE 用戶的請求做出對應的回覆
- `dbpsql.py`: PostgreSQL 資料庫的資料新增與讀取功能
- `weather.py`: 取得天氣狀況與空氣品質資訊的相關功能，參考自 [STEAM 教育學習網](https://steam.oxxostudio.tw/category/python/example/line-bot-weather-3.html)

## Dataset
- [KNN Movie Recommendation](https://github.com/Magic8763/knn_recommendation) 的 `movies_sorted.csv` 和 `knn_recommended_sorted.csv`
  - `movies_sorted.csv`: 電影特徵資料集，根據上映年份遞增排序的 62423 部電影與其特徵
  - `knn_recommended_sorted.csv`: 由 KNN 模型計算所得的電影推薦矩陣，包含與 7459 部相異電影各自高度相似的 50 部其他電影

## Authors
* **[Magic8763](https://github.com/Magic8763)**

## License
This project is licensed under the [MIT License](https://github.com/Magic8763/linebot_on_Render/blob/main/LICENSE)
