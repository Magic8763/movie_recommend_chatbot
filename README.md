# Movie Recommendation Chatbot
![](https://img.shields.io/github/stars/magic8763/linebot_on_Render)
![](https://img.shields.io/github/watchers/magic8763/linebot_on_Render)
![](https://img.shields.io/github/forks/magic8763/linebot_on_Render)
![shields](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)

本專案為具有電影推薦和 ChatGPT 功能的 LINE 聊天機器人，具有可供查詢與推薦電影的操作介面，並導入 ChatGPT 回應用戶的文字訊息。

藉由用戶與聊天機器人的互動，系統會逐漸更新電影推薦清單，得出符合用戶近期偏好的專屬內容。

對使用者而言，所有操作僅在 LINE App 上進行，不必安裝其他應用，不用進行軟體更新，也不會佔用任何儲存空間，具有高度輕便性。 

## Demo
**電影推薦**
>首頁介面
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/%E9%A6%96%E9%A0%81.jpg?token=GHSAT0AAAAAACIASZ5WCZCR5SI2PJK4FRN2ZJLWGAQ">

>點擊首頁的"近期上映"按鈕或輸入"@電影推薦機器人：近期上映"，返回上映日期最近的幾部電影。
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/%E8%BF%91%E6%9C%9F%E4%B8%8A%E6%98%A0.jpg?token=GHSAT0AAAAAACIASZ5XTBY5XTFWBBANIAE2ZJLWIEQ">

>點擊首頁的"關鍵字搜尋"按鈕或輸入"@電影推薦機器人：關鍵字搜尋"，接著輸入關鍵字，返回片名與其相符的所有電影。
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/%E9%97%9C%E9%8D%B5%E5%AD%97%E6%90%9C%E5%B0%8B.jpg?token=GHSAT0AAAAAACIASZ5XSKIHUB5KVX3NKCJSZJLWISA">

>點擊首頁的"智慧推薦"按鈕或輸入"@電影推薦機器人：智慧推薦"，返回推薦給用戶的幾部電影。
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/%E6%99%BA%E6%85%A7%E6%8E%A8%E8%96%A6.jpg?token=GHSAT0AAAAAACIASZ5XUQ7RJTA5AF7HLGDUZJLWIZQ">

>點擊首頁的"評分紀錄"按鈕或輸入"@電影推薦機器人：評分紀錄"，返回用戶最近 10 筆電影評分。
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/%E8%A9%95%E5%88%86%E6%9F%A5%E8%A9%A2.jpg?token=GHSAT0AAAAAACIASZ5XK76ILWM3M32WJFGYZJLWDDQ">

>點擊電影模板的"給予評分"按鈕，接著輸入 1 ~ 10 之間的分數給予評分。
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/%E7%B5%A6%E4%BA%88%E8%A9%95%E5%88%86.jpg?token=GHSAT0AAAAAACIASZ5WNQXT3QTS7FHFNQIOZJLWDLQ">

>點擊電影模板的"同類推薦"按鈕，返回與該電影類型相同的電影清單。
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/%E5%90%8C%E9%A1%9E%E6%8E%A8%E8%96%A6-%E5%8B%95%E4%BD%9C.jpg?token=GHSAT0AAAAAACIASZ5XYKLB7AEID26G6OSQZJLWDVQ">

**ChatGPT**
>非"@電影推薦機器人"前綴的文字訊息將由 ChatGPT 進行回應。
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/ChatGPT.jpg?token=GHSAT0AAAAAACIASZ5WB45Q7WMDQKWDTOXKZJLWD7A">

**天氣狀況**
>輸入"@地震資訊"，返回最近的中央氣象署地震報告。
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/%E5%9C%B0%E9%9C%87%E8%B3%87%E8%A8%8A.jpg?token=GHSAT0AAAAAACIASZ5WJRTWXHYQM4G7FEEAZJLWEHQ">

>輸入"@雷達回波圖"，返回最近的中央氣象署雷達合成回波圖。
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/%E9%9B%B7%E9%81%94%E5%9B%9E%E6%B3%A2%E5%9C%96.jpg?token=GHSAT0AAAAAACIASZ5XVAPBTUMD3KPIPL2YZJLWEQA">

>分享位置資訊，返回該地點的天氣資訊。
<img src="https://raw.githubusercontent.com/Magic8763/linebot_on_Render/main/img/%E6%9C%AC%E5%9C%B0%E5%A4%A9%E6%B0%A3.jpg?token=GHSAT0AAAAAACIASZ5WPVEMR7E5F3M3CWVGZJLWEZA">

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
