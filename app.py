from flask import Flask, request, abort # pip install flask
from linebot import LineBotApi, WebhookHandler # pip install line-bot-sdk
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextSendMessage, TemplateSendMessage, ImageSendMessage, # TextMessage,
    PostbackEvent, PostbackTemplateAction, URITemplateAction,
    CarouselColumn, CarouselTemplate, ButtonsTemplate, ConfirmTemplate
)
from weather import Get_Weather, Get_Forecast, Get_AQI, Get_Earthquake, RadarEcho_url
from dbpsql import userRatings, userIDs
from movie_class import Movie2
import os
import random
# import datetime
import pandas as pd
from openai import OpenAI # pip install openai
import pickle
import threading
import time
from surprise import Reader, Dataset #, SVD, SVDpp
import numpy as np

app = Flask(__name__)
# Environment variables on Render
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN')) # Channel Access Token
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET')) # Channel Secret
openai_api_key = os.environ.get('OPENAI_API_KEY') # OPENAI_API_KEY

genres_dict = {'Documentary': (0, '紀錄'), 'Comedy': (1, '喜劇'), 'Crime': (2, '犯罪'),
            'War': (3, '戰爭'), 'Musical': (4, '歌舞'), 'Western': (5, '西部'),
            'Animation': (6, '動畫'), 'Thriller': (7, '驚悚'), 'Sci-Fi': (8, '科幻'),
            'Drama': (9, '劇情'), 'Adventure': (10, '冒險'), 'Mystery': (11, '懸疑'),
            'Action': (12, '動作'), 'Horror': (13, '恐怖'), 'Romance': (14, '浪漫'),
            'Fantasy': (15, '奇幻'), 'Children': (16, '兒童'), 'Film-Noir': (17, '默劇'),
            'IMAX': (18, 'IMAX'),
            'History': (19, '歷史'), 'Sport': (20, '運動'), 'Short': (21, '短片'),
            'Biography': (22, '傳記'), 'Music': (23, '音樂'), 'Family': (24, '家庭'),
            'News': (25, '新聞'), 'Adult': (26, '成人'), 'Reality-TV': (27, '實境秀'),
            'Talk-Show': (28, '脫口秀')}
honmpage_picture = 'https://media.istockphoto.com/id/1175497926/photo/interior-of-empty-movie-theater-with-red-seats.jpg?s=612x612&w=0&k=20&c=jqQUcMrgwBqE0xbHwkd_eA-JDGQjUwFwnUnF3x0lKto='
missing_picture = 'https://media.istockphoto.com/id/1311367104/vector/404-page-not-found-banner-template.jpg?s=612x612&w=0&k=20&c=2o5WdgneLw6S2Bc5NalxJByoKMRnkd1w5O-7UnL5wBs='
carousel_size = 4 # 旋轉模板長度
output_size = 20 # 用戶buffer一次可暫存的電影總數, 即5頁旋轉模板

def writeVar(obj, drt, fname):
    if not os.path.exists(drt):
        os.makedirs(drt)
    try:
        with open(drt+'/'+fname+'.pkl', 'wb') as file:
            pickle.dump(obj, file)
    except:
        print('File exist, but open error.')

def readVar(drt, fname, return_dict=False):
    obj = {} if return_dict else []
    if os.path.exists(drt+'/'+fname+'.pkl'):
        try:
            with open(drt+'/'+fname+'.pkl', 'rb') as file:
                obj = pickle.load(file)
        except:
            print('File "', fname, '" exist, but open error.', sep='')
    return obj

# 讀資料檔
def Read_All_Data(fname):
    print("######### Read_All_Data ########")
    global movieTable, genresTable, nameTable, classTable
    movieTable = readVar('var', 'movieTable')
    print('  movieTable:', len(movieTable))
    genresTable = readVar('var', 'genresTable')
    print('  genresTable:', len(genresTable))
    nameTable = readVar('var', 'nameTable', True)
    print('  nameTable:', len(nameTable))
    classTable = readVar('var', 'classTable', True)
    print('  classTable:', len(classTable))
    if movieTable and genresTable and nameTable and classTable:
        return
    df = pd.read_csv('data/'+fname+'.csv', sep=',')
    movieTable, nameTable = [], {}
    genresTable = [[] for _ in range(len(genres_dict))]
    for i in range(len(df)):
        movieId, movieName, movieTitle, movieClass = str(df['movieId'].iloc[i]), str(df['letters'].iloc[i]), str(df['title'].iloc[i]), int(df['movieClass'].iloc[i])
        nameTable[movieId] = (i, movieTitle)
        if movieClass > 0:
            classTable[i] = movieClass
        movie = Movie2(movieId, movieName, movieTitle, str(df['year'].iloc[i]))
        if df['genres'].iloc[i] != 'N/A' and df['genres'].iloc[i] != '(no genres listed)':
            movie.genres = str(df['genres'].iloc[i]).split('|')
        movie.imdbId = 'https://www.imdb.com/title/'+str(df['imdbId'].iloc[i])
        if df['grade'].iloc[i] != 'N/A':
            movie.grade = str(df['grade'].iloc[i])
            if float(movie.grade) >= 7.0:
                for tp in movie.genres: # 分類評分>=7.0的電影
                    genresTable[genres_dict[tp][0]].append(i)
        if df['picture'].iloc[i] != 'N/A':
            movie.picture = str(df['picture'].iloc[i])
        else:
            movie.picture = missing_picture
        movieTable.append(movie)
    print('  movieTable:', len(movieTable))
    writeVar(movieTable, 'var', 'movieTable')
    print('  genresTable:', len(genresTable))
    writeVar(genresTable, 'var', 'genresTable')
    print('  nameTable:', len(nameTable))
    writeVar(nameTable, 'var', 'nameTable')
    print('  classTable:', len(classTable))
    writeVar(classTable, 'var', 'classTable')

# 載入KNN推薦結果, 用於冷啟動
def Load_KNN():
    print("######### Load_KNN ########")
    global knnRec
    knnRec = readVar('var', 'knnRec', True)
    if not knnRec:
        df = pd.read_csv('data/knn_recommended_sorted.csv', sep=',')
        df = df.to_numpy().astype(int)
        for i in range(len(df)):
            knnRec[df[i][0]] = df[i][1:]
        writeVar(knnRec, 'var', 'knnRec')
    else:
        print('  knnRec:', len(knnRec))

# 載入SVD推薦模型, 用於熱啟動
def Load_SVD(svd_name):
    print("######### Load_SVD ########")
    global svdRec, svd_max_userId, svd_last_userId
    svdRec = readVar('var', svd_name, True)
    if not svdRec:
        print('  load svdRec fail.')
    else:
        svdRec, svd_max_userId, svd_last_userId = svdRec['svd'], svdRec['max_userId'], svdRec['last_userId']
        print('  load svdRec\n    svd_max_userId:', svd_max_userId) # 非LINE用戶的最大userId
        print('    svd_last_userId', svd_last_userId) # 最新可用svd模型的用戶ID

# 類型翻譯
def Translater(buffer, ch):
    return [genres_dict[tp][ch] for tp in buffer]

class Request_Handle:
    def __init__(self, event, isPostback=False):
        uid = str(event.source.user_id)
        status_dict = readVar('user', uid, True)
        if not status_dict:
            self.new_user(uid)
        else:
            print('  user:', status_dict['uid'])
            self.load_status(status_dict)
        message = self.Message_text(event) if not isPostback else self.Message_Postback(event)
        status_dict = self.get_status()
        writeVar(status_dict, 'user', uid)
        line_bot_api.reply_message(event.reply_token, message)

    def new_user(self, uid):
        self.uid, self.status, self.GP_end = uid, 0, 0
        self.genres_buff = {} # genres_buff = {類別: 推薦清單}
        self.keyword_buff, self.ai_buff = [], []
        self.scoring, self.searched = [], {} # searched: 追蹤最近查詢/評分/點擊的3部電影的movieId, searched[i]與該電影相關的推薦內容
        self.reset_gpt_log() 

    def load_status(self, status_dict):
        self.uid, self.status, self.GP_end = status_dict['uid'], status_dict['status'], status_dict['GP_end']
        self.genres_buff = status_dict['genres_buff']
        self.keyword_buff, self.ai_buff = status_dict['keyword_buff'], status_dict['ai_buff']
        self.scoring, self.searched = status_dict['scoring'], status_dict['searched']
        self.gpt_log = status_dict['gpt_log']

    def get_status(self):
        return {'uid': self.uid, 'status': self.status, 'GP_end': self.GP_end,
                'genres_buff': self.genres_buff,
                'keyword_buff': self.keyword_buff, 'ai_buff': self.ai_buff,
                'scoring': self.scoring, 'searched': self.searched,
                'gpt_log': self.gpt_log}

    def reset_gpt_log(self):
        self.gpt_log = [{'role': 'system', 'content': 'You are a helpful assistant.'}]

    def Message_text(self, event):
        if self.status in (2, 5):
            print('  >>> 電影推薦機器人 <<<')
            if self.status == 2: # 關鍵字搜尋
                message = self.Keyword_Search(1, event.message.text)
            elif self.status == 5: # 給予評分
                message = self.Score_message(event.message.text)
            self.status = 0
        elif event.message.type == 'location': # 發送本地位置 "https://line.me/R/nv/location/" 訊息
            print('  >>> 氣象預報機器人 <<<')
            address = event.message.address
            msg = address+'\n'+Get_Weather(address)+'\n'+Get_AQI(address)+'\n'+Get_Forecast(address)
            message = TextSendMessage(text=msg)
        else: # event.message.type == 'text'
            text = event.message.text
            if text[:8] == '@電影推薦機器人':
                print('  >>> 電影推薦機器人 <<<')
                text = text[9:]
                if text == "最新電影":
                    message = self.Get_New(1)
                elif text == "關鍵字搜尋":
                    self.status = 2
                    message = TextSendMessage(text='請輸入欲查詢的電影名稱(英文)')
                elif text == "智慧推薦":
                    message = self.Get_Recommended(get_more=False)
                elif text == "評分紀錄":
                    message = self.Read_Personal_Record()
                else:
                    self.status = 0
                    message = self.Menu(None, 0)
            elif text == "@氣象雷達":
                print('  >>> 氣象雷達 <<<')
                message = self.Get_RadarEcho()
            elif text == "@地震資訊":
                print('  >>> 地震資訊 <<<')
                msg, img = Get_Earthquake()
                if not img:
                    img = missing_picture
                message = [TextSendMessage(text=msg), ImageSendMessage(original_content_url=img, preview_image_url=img)]
            else:
                print('  >>> ChatGPT <<<')
                return self.Call_ChatGPT(text)
        self.reset_gpt_log()
        return message

    def Message_Postback(self, event):
        if event.postback.data == 'action=0':
            self.status = 0
            message = self.Menu(None, 0)
        elif event.postback.data == 'action=1-1':
            message = self.Get_New(1)
        elif event.postback.data == 'action=1-2':
            message = self.Get_New(2)
        elif event.postback.data == 'action=2-1':
            self.status = 2
            message = TextSendMessage(text='請輸入欲查詢的電影名稱(英文)')
        elif event.postback.data == 'action=2-2': # 關鍵字搜尋附帶頁: 顯示更多
            message = self.Keyword_Search(2)
        elif event.postback.data == 'action=2-3': # 關鍵字搜尋失敗, self.status歸零
            self.status = 0
            message = TextSendMessage(text='關鍵字搜尋結束')
        elif event.postback.data[0:10] == 'action=3-1':
            text = event.postback.data.split('\n')[1:]
            self.Update_Searched(text[0])
            message = self.Get_Similar(text[1:], 1)
        elif event.postback.data == 'action=3-2':
            message = self.Get_Similar(None, 2)
        elif event.postback.data == 'action=3-3':
            message = self.Get_Similar(None, 3)
        elif event.postback.data == 'action=4-1':
            message = self.Read_Personal_Record()
        elif event.postback.data[0:10] == 'action=5-1':
            self.status = 5
            self.scoring = event.postback.data.split('\n')[1:]
            message = TextSendMessage(text='請輸入分數(1~10)')
        elif event.postback.data == 'action=6-1':
            message = self.Get_Recommended(get_more=False)
        elif event.postback.data == 'action=6-2':
            message = self.Get_Recommended(get_more=True)
        else:
            message = self.Menu(None, 0)
        self.reset_gpt_log()
        return message

    # 主選單
    def Menu(self, keyword, home):
        print("######### Menu ########")
        if home == 0:
            msg = TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    thumbnail_image_url=honmpage_picture,
                    title='歡迎使用電影推薦機器人',
                    text='請選擇欲執行的功能',
                    actions=[
                        PostbackTemplateAction(
                            label='最新電影',
                            data='action=1-1'
                        ),
                        PostbackTemplateAction(
                            label='關鍵字搜尋',
                            data='action=2-1'
                        ),
                        PostbackTemplateAction(
                            label='智慧推薦',
                            data='action=6-1'
                        ),
                        PostbackTemplateAction(
                            label='評分紀錄',
                            data='action=4-1'
                        )
                    ]
                )
            )
        elif home == 1:
            msg = CarouselColumn(
                thumbnail_image_url=honmpage_picture,
                title='最新電影',
                text='請選擇欲執行的功能',
                actions=[
                    PostbackTemplateAction(
                        label='顯示更多',
                        data='action=1-2'
                    ),
                    PostbackTemplateAction(
                        label='返回首頁',
                        data='action=0'
                    ),
                    PostbackTemplateAction(
                        label=' ',
                        data='action=0'
                    )
                ]
            )
        elif home == 2:
            if keyword != None:
                head = '\"'+keyword+'\"的搜尋結果'
            else:
                head = '其他結果'
            msg = CarouselColumn(
                thumbnail_image_url=honmpage_picture,
                title=head,
                text='請選擇欲執行的功能',
                actions=[
                    PostbackTemplateAction(
                        label='顯示更多',
                        data='action=2-2'
                    ),
                    PostbackTemplateAction(
                        label='重新搜尋',
                        data='action=2-1'
                    ),
                    PostbackTemplateAction(
                        label='返回首頁',
                        data='action=0'
                    )
                ]
            )
        elif home == 3:
            msg = CarouselColumn(
                thumbnail_image_url=honmpage_picture,
                title='\"'+keyword+'\"的搜尋結果',
                text='請選擇欲執行的功能',
                actions=[
                    PostbackTemplateAction(
                        label='顯示更多',
                        data='action=3-2'
                    ),
                    PostbackTemplateAction(
                        label='下個類型',
                        data='action=3-3'
                    ),
                    PostbackTemplateAction(
                        label='返回首頁',
                        data='action=0'
                    )
                ]
            )
        elif home == 4:
            msg = CarouselColumn(
                thumbnail_image_url=honmpage_picture,
                title='智慧推薦',
                text='請選擇欲執行的功能',
                actions=[
                    PostbackTemplateAction(
                        label='顯示更多',
                        data='action=6-2'
                    ),
                    PostbackTemplateAction(
                        label='返回首頁',
                        data='action=0'
                    ),
                    PostbackTemplateAction(
                        label=' ',
                        data='action=0'
                    )
                ]
            )
        return msg

    # 製作訊息模板
    def Carousel_template(self, sub_buffer, text, home):
        print("######### Carousel_template ########")
        template_list = []
        for i in range(len(sub_buffer)):
            if len(sub_buffer[i].title) > 40:
                continue
            movie_info = 'action=5-1\n'+sub_buffer[i].id+'\n'+sub_buffer[i].title
            context = '('+str(sub_buffer[i].year)+')'
            if sub_buffer[i].genres:
                sub = Translater(sub_buffer[i].genres, 1)
                context += '\n'+sub[0]
                action = 'action=3-1\n'+sub_buffer[i].id+'\n'+sub_buffer[i].genres[0]
                for j in range(1, len(sub_buffer[i].genres)):
                    context += ', '+sub[j]
                    action += '\n'+sub_buffer[i].genres[j]
                action += '\n'+str(i)
            else:
                context += '\n尚無分類'
                action = ' '
            if sub_buffer[i].grade != None:
                context += '\n[score '+sub_buffer[i].grade+']'
            if len(context) > 60:
                continue
            template = CarouselColumn(
                thumbnail_image_url=sub_buffer[i].picture,
                title=sub_buffer[i].title,
                text=context,
                actions=[
                    URITemplateAction(
                        label='IMDb主頁',
                        uri=sub_buffer[i].imdbId
                    ),
                    PostbackTemplateAction(
                        label='給予評分',
                        data=movie_info
                    ),
                    PostbackTemplateAction(
                        label='同類推薦',
                        data=action
                    )
                ]
            )
            template_list.append(template)
        template_list.append(self.Menu(text, home))
        msg = TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=template_list
            )
        )
        return msg

    # 最新電影
    def Get_New(self, type):
        print("######### Get_New ########")
        if type == 1:
            self.GP_end = 0
        GP_start = self.GP_end-carousel_size
        sub_buffer = movieTable[GP_start:self.GP_end] if self.GP_end < 0 else movieTable[GP_start:]
        if sub_buffer:
            self.GP_end = GP_start
            msg = self.Carousel_template(sub_buffer[::-1], None, 1)
        else:
            msg = TextSendMessage(text='沒有任何電影') if type == 1 else  TextSendMessage(text='沒有更多電影')
        return msg

    # 同類推薦
    def Get_Similar(self, text, type):
        print("######### Get_Similar ########")
        if type == 1: # 同類推薦
            movieidx, genres_english = int(text[-1]), text[:-1]
            cpbuf = set(knnRec[movieidx]) if movieidx in knnRec.keys() else set() # 優先從KNN推薦結果中篩選具有相同類型者
            genres_indices = Translater(genres_english, 0)
            self.genres_buff = {}
            for l in range(len(genres_english)):
                tybuf = set()
                for cp in cpbuf:
                    if genres_english[l] in movieTable[cp].genres:
                        tybuf.add(cp)
                while len(tybuf) < output_size:
                    picked = random.sample(range(len(genresTable[genres_indices[l]])), 1)[0]
                    tybuf.add(genresTable[genres_indices[l]][picked])
                scbuf = [movieTable[tp] for tp in tybuf]
                random.shuffle(scbuf)
                if scbuf:
                    self.genres_buff[genres_english[l]] = scbuf
        if type == 3: # 換下個類型
            if not self.genres_buff:
                return TextSendMessage(text='沒有更多類型')
            key = next(iter(self.genres_buff))
            del self.genres_buff[key]
        if self.genres_buff:
            key = next(iter(self.genres_buff))
            if self.genres_buff[key]:
                genres_zhtw = genres_dict[key][1]
                sub_buffer = self.genres_buff[key][:carousel_size]
                self.genres_buff[key] = self.genres_buff[key][carousel_size:]
                msg = self.Carousel_template(sub_buffer, genres_zhtw, 3)
                return msg
        return TextSendMessage(text='沒有更多電影') if type == 1 else TextSendMessage(text='沒有同類電影')

    # KNN推薦
    def KNN_Recommended(self, getSVD=False):
        print("######### KNN_Recommended ########")
        if len(self.searched) < 3:
            self.Read_Personal_Record(get_last=True)
        buf, knnKeys = set(), list(knnRec.keys())
        searchedKeys = list(self.searched.keys())
        keep_searched = {}
        random.shuffle(knnKeys)
        for movieidx in searchedKeys:
            if movieidx in knnKeys:
                keep_searched[movieidx] = self.searched[movieidx]
            del self.searched[movieidx]
        self.searched = {movieidx: 0 for movieidx in knnKeys[:3-len(keep_searched)]}
        for movieidx in keep_searched.keys():
            self.searched[movieidx] = keep_searched[movieidx]
        for movieidx in self.searched.keys():
            n = len(knnRec[movieidx])
            start = self.searched[movieidx]%n
            end = min(start+carousel_size, n)
            for i in range(start, end):
                if knnRec[movieidx][i] not in self.searched.keys():
                    buf.add(knnRec[movieidx][i])
            self.searched[movieidx] = end
        buf = list(buf)
        if getSVD:
            return buf
        else:
            random.shuffle(buf)
        return [movieTable[i] for i in buf]

    # SVD推薦
    def SVD_Recommended(self, userId, target_movies):
        print("######### SVD_Recommended ########")
        indices = [i for i in target_movies if i in classTable]
        movieClass = [classTable[i] for i in indices]
        rows = {'userId': [userId]*len(movieClass),
                'movieId': movieClass}
        test_df = pd.DataFrame(rows)
        test_df['rating'] = 0.0
        dataset = Dataset.load_from_df(test_df, Reader())
        dataset = dataset.build_full_trainset().build_testset()
        preds = svdRec.test(dataset) # 測試模型
        estimations = np.array([est for _, _, _, est, _ in preds])
        sorted_indices = estimations.argsort()[::-1]
        res = [movieTable[indices[i]] for i in sorted_indices]
        return res

    # 智慧推薦
    def Get_Recommended(self, get_more=False):
        print("######### Get_Recommended ########")
        if not get_more:
            dbid = userIDs.User_reader(self.uid)
            if dbid == None or dbid.id+svd_max_userId > svd_last_userId:
                self.ai_buff = self.KNN_Recommended(getSVD=False)
                # buf = self.KNN_Recommended(getSVD=True)
                # self.ai_buff = self.SVD_Recommended(svd_max_userId, buf)
            else:
                buf = self.KNN_Recommended(getSVD=True)
                self.ai_buff = self.SVD_Recommended(dbid.id+svd_max_userId, buf)
        elif not self.ai_buff:
            return TextSendMessage(text='沒有更多電影')
        sub_buffer = self.ai_buff[:carousel_size]
        self.ai_buff = self.ai_buff[carousel_size:]
        return self.Carousel_template(sub_buffer, None, 4)

    # 更新紀錄檔
    def Save_Personal_Record(self, movieId, num):
        print("######### Save_Personal_Record ########")
        dbid = userIDs.User_reader(self.uid)
        if dbid == None:
            userIDs.User_adder(self.uid)
            dbid = userIDs.User_reader(self.uid)
        userRatings.Record_adder(dbid.id+svd_max_userId, movieId, num)

    # 讀取紀錄檔
    def Read_Personal_Record(self, get_last=False):
        print("######### Read_Personal_Record ########")
        dbid = userIDs.User_reader(self.uid)
        if dbid == None:
            return TextSendMessage(text='您尚未完成電影評分')
        records = userRatings.Record_reader(dbid.id+svd_max_userId)
        if get_last: # 選擇近期最多3個評分紀錄填充self.searched
            n = len(records)
            for i in range(max(0, n-3+len(self.searched)), n):
                movieidx = nameTable[records[i].movie][0]
                self.searched[movieidx] = 0
        else:
            records.reverse()
            catched = min(10, len(records))
            date = str(records[0].timestamp).split(' ')[0]
            date = date.replace('-', '/')
            movieTitle = nameTable[records[0].movie][1]
            record_str = '您的最近'+str(catched)+'筆評分紀錄\n'+date+' ['+movieTitle+']: '+str(records[0].rating)
            for i in range(1, catched): # 僅輸出最近最多10筆的評分紀錄
                date = str(records[i].timestamp).split(' ')[0]
                date = date.replace('-', '/')
                movieTitle = nameTable[records[i].movie][1]
                record_str += '\n'+date+' ['+movieTitle+']: '+str(records[i].rating)
            return TextSendMessage(text=record_str)

    # 追蹤最近(給予評分/同類推薦)的3部電影idx
    def Update_Searched(self, movieId):
        print("######### Update_Searched ########")
        movieidx = nameTable[movieId][0]
        if movieidx not in self.searched.keys():
            self.searched[movieidx] = 0
        if len(self.searched.keys()) > 3:
            first_key = list(self.searched.keys())[0]
            del self.searched[first_key]
        print(' Update ', self.uid, ', searched: ', self.searched.keys(), sep='')

    # 紀錄評分
    def Score_message(self, text):
        print("######### Score_message ########")
        movieId = str(self.scoring[0]) # 電影id
        movieName = str(self.scoring[1]) # 電影名稱
        try:
            num = min(10, max(1, int(text)))
            if num > 5:
                self.Update_Searched(movieId)
            self.Save_Personal_Record(movieId, num)
            print('\n****'+ self.uid+'****'+movieId+'****'+movieName+'****'+str(num)+'****')
            msg = TextSendMessage(text='"'+movieName+'" 已評分')        
        except ValueError:
            msg = TextSendMessage(text='評分失敗')
        return msg

    # 關鍵字搜尋
    def Keyword_Search(self, type, input_text = ''):
        print("######### Keyword_Search ########")
        if type == 1:
            movie_name = input_text.lower().replace(' ', '')
            matched = [(len(movie.title), i) for i, movie in enumerate(movieTable) if movie_name in movie.letters or movie_name in movie.title]
            matched.sort(key=lambda x: (x[0], -x[1]))
            self.keyword_buff = [movieTable[i] for _, i in matched[:20]]
            if self.keyword_buff:
                sub_buffer = self.keyword_buff[:carousel_size]
                self.keyword_buff = self.keyword_buff[carousel_size:]
                if len(sub_buffer) == 1: # 查詢只找到一部電影時將加入追蹤清單
                    self.Update_Searched(sub_buffer[0].id)
                msg = self.Carousel_template(sub_buffer, input_text, 2)
            else: # 沒有找到電影
                msg = TemplateSendMessage(
                    alt_text='ConfirmTemplate',
                    template=ConfirmTemplate(
                        text='搜尋失敗，是否要重新搜尋？',
                        actions=[
                            PostbackTemplateAction(
                                label='是',
                                data='action=2-1'
                            ),
                            PostbackTemplateAction(
                                label='否',
                                data='action=2-3'
                            )
                        ]
                    )
                )
        elif type == 2:
            if self.keyword_buff:
                sub_buffer = self.keyword_buff[:carousel_size]
                self.keyword_buff = self.keyword_buff[carousel_size:]
                msg = self.Carousel_template(sub_buffer, None, 2)
            else:
                msg = TextSendMessage(text='沒有更多電影')
        return msg

    # 氣象雷達
    def Get_RadarEcho(self):
        return ImageSendMessage(original_content_url=RadarEcho_url, preview_image_url=RadarEcho_url)

    # 以ChatGPT回覆訊息
    def Call_ChatGPT(self, input_text):
        self.gpt_log.append({'role': 'user', 'content': input_text})
        #print(self.gpt_log)
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            #model = 'gpt-3.5-turbo',
            model = 'gpt-4',
            messages = self.gpt_log,
            max_tokens = 512, # max_tokens 最大為2048
            temperature = 1
        )
        msg = response.choices[0].message.content
        self.gpt_log.pop()
        self.gpt_log.append({'role': 'assistant', 'content': msg})
        return TextSendMessage(text=msg)

# 監聽所有來自'.../'的 Post Request
@app.route("/", methods=['POST'])
def callback(): # 每個訊息的首站
    print("\n######### linebot running ########")
    signature = request.headers['X-Line-Signature'] # get X-Line-Signature header value
    body = request.get_data(as_text=True) # get request body as text
    app.logger.info("Request body: "+body)
    try:
        handler.handle(body, signature) # handle webhook body, 將 body 交由 handler 分類處理
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def Threading_Handle(event, isPostback=False):
    print("######### Threading_Handle ########")
    Request_Handle(event, isPostback)
    time.sleep(1)

# 處理"模板點擊"
@handler.add(PostbackEvent)
def handle_postback(event):
    print("######### handle_postback ########")
    #Request_Handle(event, True)
    thread = threading.Thread(target=Threading_Handle, args=(event, True)) # 以thread生成
    thread.start()

# 處理"訊息發送"
@handler.add(MessageEvent)
def handle_message(event):
    print("######### handle_message ########")
    # profile = line_bot_api.get_profile(event.source.user_id)
    # profile.display_name = 使用者Line暱稱
    # event.source.user_id = 使用者Line帳戶ID
    # event.source.room_id = Line聊天室ID
    # event.message.text = 使用者輸入訊息
    #Request_Handle(event, False)
    thread = threading.Thread(target=Threading_Handle, args=(event, False)) # 以thread生成
    thread.start()
"""
if __name__ == "__main__": # 當app.py是被執行而非被引用時, 執行下列程式碼
    print("\n######### main ########")
    Read_All_Data('movies@0x1000_1M_compactify')
    Load_KNN()
    Load_SVD('SVD++_best@0x1000_1M')
    port = int(os.environ.get('PORT', 5000))
    #app.debug = True
    app.run(host='0.0.0.0', port=port) # 以linebot()接收請求
    #serve(app, host='0.0.0.0', port=port) # 使用 Waitress (WSGI伺服器), 在Render上不支援
"""
print("\n######### main ########")
Read_All_Data('movies@0x1000_1M_compactify')
Load_KNN()
Load_SVD('SVD++_best@0x1000_1M')
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port) # 以linebot()接收請求