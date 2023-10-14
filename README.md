# Movie Recommendation Chatbot
![](https://img.shields.io/github/stars/Magic8763/TPMP.svg) ![](https://img.shields.io/github/watchers/Magic8763/TPMP.svg) ![](https://img.shields.io/github/forks/Magic8763/TPMP.svg) ![shields](https://img.shields.io/badge/python-3.11%2B-blue.svg?style=flat-square) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

本專案為具有電影推薦和 ChatGPT 功能的 LINE 聊天機器人，具有可供查詢與推薦電影的操作介面，並導入 ChatGPT API 來回應用戶的文字訊息。

藉由用戶與聊天機器人的互動，系統會逐漸更新電影推薦清單，得出符合用戶近期偏好的專屬內容。

對使用者而言，所有操作僅在 LINE App 上進行，不必安裝其他應用，不用進行軟體更新，也不會佔用任何儲存空間，具有高度輕便性。 

## Demo
掃描以下 QR code 將聊天機器人加為好友

<img height="100" border="0" alt="QRcode" src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/qrcode.png?token=GHSAT0AAAAAACIASZ5XDYNFTWNEWOVLVV6EZJKSR4Q">

<a href="https://line.me/R/ti/p/@syw6100p"><img height="30" border="0" alt="加入好友" src="https://scdn.line-apps.com/n/line_add_friends/btn/zh-Hant.png"></a>



## Prerequisites
- Python3, Pandas, Requests, Flask, Flask-SQLAlchemy, Psycopg2, LINE Messaging API SDK, OpenAI API
- [LINE Official Account](https://manager.line.biz/) (建立機器人帳戶)
- [LINE Developers](https://developers.line.biz/en/) (串接 Messaging API)
- [OpenAI](https://platform.openai.com/) (串接付費 ChatGPT API)
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
