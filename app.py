from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
#from linebot.models import *
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ImageSendMessage, 
    PostbackEvent, PostbackTemplateAction, URITemplateAction,
    CarouselColumn, CarouselTemplate, ButtonsTemplate, ConfirmTemplate
)
import os
import random
import datetime
import csv
import pandas as pd

import openai
openai.api_key = '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'

from weather import Get_Weather, Get_Forecast, Get_AQI, Get_Earthquake

app = Flask(__name__)
# Channel Access Token(YOUR_CHANNEL_ACCESS_TOKEN)
line_bot_api = LineBotApi('t6pQxlob2d6HG7eli4Ck0y0yq49zE03JiedrVk2rjmHu3StIrdyGijxM+jQqXj+oSniedXwjZqkuHNZHntBe8k1hf2qccsdJsgaEPvAVHfNb6wJ6LX3zmiLACCJQ1/leSRmgaXWecMZq48aMVYEvqQdB04t89/1O/w1cDnyilFU=')
# Channel Secret(YOUR_CHANNEL_SECRET)
handler = WebhookHandler('f618a9e80020ea18a0a16b2c4643bbb5')

typedcit = {'Documentary': (0, '紀錄'), 'History': (1, '歷史'), 'Comedy': (2, '喜劇'),
			'Crime': (3, '犯罪'), 'Sport': (4, '運動'), 'War': (5, '戰爭'),
			'Animation': (6, '動畫'), 'Thriller': (7, '驚悚'), 'Sci-Fi': (8, '科幻'),
			'Musical': (9, '歌舞'), 'Western': (10, '西部'), 'Short': (11, '短片'),
			'Biography': (12, '傳記'), 'Music': (13, '音樂'), 'Drama': (14, '劇情'),
			'Family': (15, '家庭'), 'Adventure': (16, '冒險'), 'Mystery': (17, '懸疑'),
			'Action': (18, '動作'), 'Horror': (19, '恐怖'), 'Romance': (20, '浪漫'),
			'Fantasy': (21, '奇幻')}
movieTable, typeTable, statusTable, resultTable = [], [], [], []
honmpage_picture = 'https://attach.setn.com/newsimages/2017/02/10/805406-XXL.jpg'
error_picture = 'https://cdn0.techbang.com/system/excerpt_images/55555/original/d5045073e258563e2b62eed24605cd60.png?1512550227'
playing_k = 20 # 近期上映的前k部電影
carousel_size = 20 # 旋轉模板長度上限

class Movie2():
    def __init__(self, id = None, name = None, t = None):
        self.id = id
        self.nameEnglish = name
        self.time = t
        self.info_addr = None
        self.grade = None
        self.type = []
        self.picture= None

class Personal_Status():
	def __init__(self, id):
		self.user_id = str(id)
		self.update_data()

	def update_data(self, sta = 0, gpi = 0, cat2 = [], cat3 = [], sci = 0, scj = 0, buf2 = [], sco = [], aib = []):
		self.status = sta
		self.GP_ii = gpi
		self.category2 = cat2
		self.category3 = cat3
		self.SC_ii = sci
		self.SC_jj = scj
		self.buffer2 = buf2
		self.scoring = sco
		self.aibuf = aib

# 保存狀態
def Store_Status(id):
	print("######### Store_Status ########")
	global status, GP_ii, category2, category3, SC_ii, SC_jj, buffer2, scoring, aibuf
	for i in range(0, len(statusTable)):
		if statusTable[i].user_id == id:
			print(' >> ', id, status)
			statusTable[i].update_data(sta = status, gpi = GP_ii, cat2 = category2, cat3 = category3, sci = SC_ii, scj = SC_jj, buf2 = buffer2, sco = scoring, aib = aibuf)
			break
	else:
		i = len(statusTable)
		new_PS = Personal_Status(id)
		new_PS.update_data(sta = status, gpi = GP_ii, cat2 = category2, cat3 = category3, sci = SC_ii, scj = SC_jj, buf2 = buffer2, sco = scoring, aib = aibuf)
		statusTable.append(new_PS)
	print("  Store >>> "+id+" >>> Table["+str(i)+"]")

# 還原狀態
def Restore_Status(id):
	print("######### Restore_Status ########")
	global status, GP_ii, category2, category3, SC_ii, SC_jj, buffer2, scoring, aibuf
	for st in statusTable:
		if st.user_id == id:
			print(' << ', id, status)
			status = st.status
			GP_ii = st.GP_ii
			category2 = st.category2
			category3 = st.category3
			buffer2 = st.buffer2
			SC_ii = st.SC_ii
			SC_jj = st.SC_jj
			scoring = st.scoring
			aibuf = st.aibuf
			break
	else:
		status = GP_ii = SC_ii = SC_jj = 0
		category2, category3, buffer2, scoring, aibuf = [], [], [], [], []
	print("  Restore <<< "+id+" <<< Table["+str(len(statusTable))+"]")

# 監聽所有來自'.../callback'的 Post Request
@app.route("/callback", methods = ['POST'])
def linebot(): # 每個訊息的首站
	#print("######### callback ########")
	print("\n######### linebot running ########")
	signature = request.headers['X-Line-Signature'] # get X-Line-Signature header value
	body = request.get_data(as_text = True) # get request body as text
	app.logger.info("Request body: "+body)
	try:
		handler.handle(body, signature) # handle webhook body
	except InvalidSignatureError:
		abort(400)
	return 'OK'

# 讀資料檔
def Read_All_Data2():
	print("######### Read_All_Data2 ########")
	"""
	with open('movieData.csv', newline = '', encoding = 'utf8') as csvfile:
		rows = csv.DictReader(csvfile)
		for row in rows:
			movie = Movie2(str(row['movieId']), str(row['nameEnglish']),str(row['time']))
			movie.info_addr = 'https://www.imdb.com/title/'+str(row['info_addr'])
			if row['grade'] != 'N/A':
				movie.grade = str(row['grade'])
			if row['type'] != 'N/A':
				movie.type = str(row['type']).split(', ')
			if row['picture'] != 'N/A':
				movie.picture = str(row['picture'])
			else:
				movie.picture = error_picture
			movieTable.append(movie)
	"""
	df = pd.read_csv('movieData.csv', sep = ',')
	for i in range(0, len(df)):
		movie = Movie2(str(df['movieId'].iloc[i]), str(df['nameEnglish'].iloc[i]),str(df['time'].iloc[i]))
		movie.info_addr = 'https://www.imdb.com/title/'+str(df['info_addr'].iloc[i])
		if df['grade'].iloc[i] != 'N/A':
			movie.grade = str(df['grade'].iloc[i])
		if df['type'].iloc[i] != 'N/A':
			movie.type = str(df['type'].iloc[i]).split(', ')
		if df['picture'].iloc[i] != 'N/A':
			movie.picture = str(df['picture'].iloc[i])
		else:
			movie.picture = error_picture
		movieTable.append(movie)

# 電影分類
def Classification():
	print("######### Classification ########")
	for _ in range(0, len(typedcit)):
		typeTable.append([])
	for i in range(0, len(movieTable)):
		for tp in movieTable[i].type:
			if tp in typedcit:
				typeTable[typedcit[tp][0]].append(i)

# 推薦結果
def KNN_Result():
	print("######### KNN_Result ########")
	for _ in range(0, len(movieTable)):
		resultTable.append({})
	with open('movie3477.txt', 'r', encoding = 'utf8') as f:
		read = f.readlines()
	for inMovie in read:
		info = inMovie.split('\t')
		resultTable[int(info[0])] = {int(info[i]) for i in range(1, len(info)-1)}

# 類型翻譯
def Translater(buffer, ch):
	return [typedcit[tp][ch] for tp in buffer]

# 主選單
def Menu(keyword, home):
	print("######### Menu ########")
	if home == 0:
		msg = TemplateSendMessage(
			alt_text = 'Buttons template',
			template = ButtonsTemplate(
				thumbnail_image_url = honmpage_picture,
				title = '歡迎使用電影推薦機器人',
				text = '請選擇欲執行的功能',
				actions = [
					PostbackTemplateAction(
						label = '近期上映',
						data = 'action=1-1'
					),
					PostbackTemplateAction(
						label = '關鍵字搜尋',
						data = 'action=2-1'
					),
					PostbackTemplateAction(
						label = '智慧推薦',
						data = 'action=6-1'
					),
					PostbackTemplateAction(
						label = '評分紀錄',
						data = 'action=4-1'
					)
				]
			)
		)
	elif home == 1:
		msg = CarouselColumn(
			thumbnail_image_url = honmpage_picture,
			title = '近期上映',
			text = '請選擇欲執行的功能',
			actions = [
				PostbackTemplateAction(
					label = '顯示更多',
					data = 'action=1-2'
				),
				PostbackTemplateAction(
					label = '返回首頁',
					data = 'action=0'
				),
				PostbackTemplateAction(
					label = ' ',
					data = 'action=0'
				)
			]
		)
	elif home == 2:
		if keyword != None:
			head = '\"'+keyword+'\"的搜尋結果'
		else:
			head = '其他結果'
		msg = CarouselColumn(
			thumbnail_image_url = honmpage_picture,
			title = head,
			text = '請選擇欲執行的功能',
			actions = [
				PostbackTemplateAction(
					label = '顯示更多',
					data = 'action=2-2'
				),
				PostbackTemplateAction(
					label = '重新搜尋',
					data = 'action=2-1'
				),
				PostbackTemplateAction(
					label = '返回首頁',
					data = 'action=0'
				)
			]
		)
	elif home == 3:
		msg = CarouselColumn(
			thumbnail_image_url = honmpage_picture,
			title='\"'+keyword+'\"的搜尋結果',
			text = '請選擇欲執行的功能',
			actions = [
				PostbackTemplateAction(
					label = '顯示更多',
					data = 'action=3-2'
				),
				PostbackTemplateAction(
					label = '下個類型',
					data = 'action=3-3'
				),
				PostbackTemplateAction(
					label = '返回首頁',
					data = 'action=0'
				)
			]
		)
	elif home == 4:
		msg = CarouselColumn(
			thumbnail_image_url = honmpage_picture,
			title = '智慧推薦',
			text = '請選擇欲執行的功能',
			actions = [
				PostbackTemplateAction(
					label = '顯示更多',
					data = 'action=6-2'
				),
				PostbackTemplateAction(
					label = '返回首頁',
					data = 'action=0'
				),
				PostbackTemplateAction(
					label = ' ',
					data = 'action=0'
				)
			]
		)
	return msg

# 更新紀錄檔
def Save_Personal_Record(id, name, num):
	print("######### Save_Personal_Record ########")
	today = datetime.datetime.now()
	try:
		f = open('HS_'+str(id)+'.txt', 'a', encoding = 'utf8')
		record_str = str(today.year)+'\t'+str(today.month)+'\t'+str(today.day)+'\t'+str(name)+'\t'+str(num)+'\n'
		f.write(record_str)
		f.close()
	except IOError:
		print('更新紀錄檔失敗')

# 讀取紀錄檔
def Read_Personal_Record(event, get_msg = True):
	print("######### Read_Personal_Record ########")
	id = event.source.user_id
	try:
		with open('HS_'+str(id)+'.txt', 'r', encoding = 'utf8') as f:
			read = f.readlines()
		record_str = ''
		for infile in read:
			info = infile.split('\t')
			record_str = str(info[1])+'/'+str(info[2])+' ['+str(info[3])+']: '+str(info[4])+record_str 
		msg = TextSendMessage(text = record_str[:-1]) if get_msg else str(info[3])
	except IOError:
		msg = TextSendMessage(text = '查無本id的紀錄') if get_msg else None
	return msg

# 製作訊息模板
def Carousel_template2(event, sub_buffer, text, home):
	print("######### Carousel_template2 ########")
	personal_id = event.source.user_id
	template_list = []
	for i in range(0, len(sub_buffer)):
		if len(sub_buffer[i].nameEnglish) > 40:
			continue
		movie_info = 'action=5-1'+personal_id+'\n'+sub_buffer[i].id+'\n'+sub_buffer[i].nameEnglish
		context = '('+str(sub_buffer[i].time)+')'
		if sub_buffer[i].type:
			sub	= Translater(sub_buffer[i].type, 1)
			context += '\n'+sub[0]
			action = 'action=3-1'+sub_buffer[i].type[0]
			for j in range(1, len(sub_buffer[i].type)):
				context += ','+sub[j]
				action += '\n'+sub_buffer[i].type[j]
			action += '\n'+str(i)
		else:
			action = ' '
			#action = 'action=3-1' + sub_buffer[i].nameEnglish
		if sub_buffer[i].grade != None:
			context += '\n[score '+sub_buffer[i].grade+']'
		if len(context) > 60:
			continue
		template = CarouselColumn(
			thumbnail_image_url = sub_buffer[i].picture,
			title = sub_buffer[i].nameEnglish,
			text = context,
			actions = [
				URITemplateAction(
					label = 'IMDb網頁',
					uri = sub_buffer[i].info_addr
				),
				PostbackTemplateAction(
					label = '給予評分',
					data = movie_info
				),
				PostbackTemplateAction(
					label = '同類推薦',
					data = action
				)
			]
		)
		template_list.append(template)
	template_list.append(Menu(text, home))
	msg = TemplateSendMessage(
		alt_text = 'Carousel template',
		template = CarouselTemplate(
			columns = template_list
		)
	)
	#Save_Personal_Record(event, sub_buffer)
	return msg

# 近期上映
def Get_Playing2(event, type):
	print("######### Get_Playing2 ########")
	global GP_ii
	if type == 1:
		GP_ii = len(movieTable)-playing_k
	if GP_ii < len(movieTable):
		sub = min(GP_ii+5, len(movieTable))
		sub_buffer = movieTable[GP_ii:sub]
		msg = Carousel_template2(event, sub_buffer, None, 1)
		GP_ii = sub
	elif type == 1:
		msg = TextSendMessage(text = '沒有任何電影')
	elif type == 2:
		GP_ii = len(movieTable)-playing_k
		msg = TextSendMessage(text = '沒有更多電影')
	return msg

# 共同篩選
def Filtering(lastmovie, quantity_ratings, have_seen_movie_list):
	print("######### Filtering ########")
	df = pd.read_csv('ourRatings.csv', sep = ',')    
	movie_titles = pd.read_csv('movieData.csv')
#	myMovie = pd.read_csv('movieData.csv')
	myMovie = movie_titles.reset_index()[['index','nameEnglish']]
	movie_titles = movie_titles[['movieId','nameEnglish']]
	df = pd.merge(df, movie_titles, on = 'movieId') 
	ratings = pd.DataFrame(df.groupby('nameEnglish')['rating'].mean())
	ratings['number_of_ratings'] = df.groupby('nameEnglish')['rating'].count() 
	movie_matrix = df.pivot_table(index = 'userId', columns = 'nameEnglish', values = 'rating') 
	lastmovie_ratings = movie_matrix[lastmovie]
	similar_to_lastmovie = movie_matrix.corrwith(lastmovie_ratings)
	corr_lastmovie_ratings = pd.DataFrame(similar_to_lastmovie, columns = ['Correlation']) 
	#print(corr_lastmovie_ratings)
	corr_lastmovie_ratings.dropna(inplace = True) 
	#print(corr_lastmovie_ratings.sort_values(by = 'Correlation',ascending=False).head(10))
	t = corr_lastmovie_ratings.join(ratings['number_of_ratings'])
	t = t[t['number_of_ratings'] > quantity_ratings].sort_values(by = 'Correlation', ascending = False).reset_index()["nameEnglish"]
#	myMovie = myMovie.reset_index()[['index','nameEnglish']]
	res = set()
	for title in t : 
		i = myMovie[myMovie['nameEnglish'] == title]['index'].tolist()[0]
		res.add(i)
	return res

# 相關性同類推薦
def Same_Category3(event, text, type):
	print("######### Same_Category3 ########")
	global category2, category3, SC_ii, SC_jj
	if type == 1: # 同類推薦
		category2, category3 = [], [] # 電影清單, 類型清單
		movieindex, text = int(text[-1]), text[:-1]
		cpbuf = Filtering(movieTable[movieindex].nameEnglish, carousel_size, [movieTable[movieindex].nameEnglish]) if movieindex < (len(movieTable)-playing_k) else {}
		title, index = Translater(text, 1), Translater(text, 0)
		for l in range(0, len(text)):
			buf = []
			for cp in cpbuf:
				if movieTable[cp].type:
					for tp in movieTable[cp].type:
						if str(text[l]) == tp:
							buf.append(cp)
			if len(buf) < carousel_size:
				tybuf = []
				for tp in typeTable[index[l]]:
					if tp not in cpbuf:
						tybuf.append(tp)
				for i in random.sample(range(len(tybuf)), carousel_size-len(buf)):
					buf.append(tybuf[i])
			scbuf = []
			for i in random.sample(range(len(buf)), carousel_size):
				scbuf.append(movieTable[buf[i]])
			if len(scbuf) > 0:
				category2.append(scbuf)
				category3.append(str(title[l]))
		SC_ii = 0
		if category2:
			SC_jj = min(SC_ii+5, len(category2[0]))
			msg = Carousel_template2(event, category2[0][SC_ii:SC_jj], category3[0], 3)
		else:
			msg = TextSendMessage(text = '沒有同類電影')
	elif type == 2: # 顯示更多
		if len(category2[0])-SC_jj >= 1:
			SC_ii = SC_jj
			SC_jj = min(SC_ii+5, len(category2[0]))
			msg = Carousel_template2(event, category2[0][SC_ii:SC_jj], category3[0], 3)
		else:
			msg = TextSendMessage(text = '沒有更多電影')
	elif type == 3: # 下個類型
		if len(category2) > 1:
			category2, category3 = category2[1:], category3[1:]
			SC_jj = min(5, len(category2[0]))
			msg = Carousel_template2(event, category2[0][:SC_jj], category3[0], 3)
		else:
			msg = TextSendMessage(text = '沒有更多類型')
	return msg

# 直接推薦
def Recommend2(event, type):
	print("######### Recommend2 ########")
	global aibuf
	if type == 1:
		id = event.source.user_id
		movieName = Read_Personal_Record(event, False) #[2069] = 75731 Toy Story 3
		buf = []
		if movieName != None:
			for i in range(0, len(movieTable)):
				if movieTable[i].nameEnglish == movieName:
					cpbuf = Filtering(movieName, carousel_size, [movieName]) if i < (len(movieTable)-playing_k) else resultTable[i]
					for cp in cpbuf:
						if movieTable[cp].type:
							buf.append(cp)
					break
		aibuf = []
		if len(buf) < carousel_size:
			for i in random.sample(range(len(movieTable)), carousel_size-len(buf)):
				aibuf.append(movieTable[i])
		else:
			for i in random.sample(range(len(buf)), carousel_size):
				aibuf.append(movieTable[buf[i]])
		if not aibuf:
			return None
		sub = min(5, len(aibuf))
		sub_buffer = aibuf[0:sub]
		msg = Carousel_template2(event, sub_buffer, None, 4)
	elif type == 2:
		if len(aibuf) > 5:
			aibuf = aibuf[5:]
			if not aibuf:
				return None
			sub = min(5, len(aibuf))
			sub_buffer = aibuf[0:sub]
			msg = Carousel_template2(event, sub_buffer, None, 4)
		else:
			aibuf = []
			msg = TextSendMessage(text='沒有更多電影')
	return msg

# 紀錄評分
def Score_message(text, scoring):
	print("######### Score_message ########")
	global status
	id = str(scoring[0]) # user id
	name = str(scoring[1]) #電影id
	try:
		num = str(min(5.0, max(0.0, float(text))))
		Save_Personal_Record(id, str(scoring[2]), num)
		print('****' + id + '****' + name + '****' + str(scoring[2]) + '****' + num + '****')
		msg = TextSendMessage(text = '已評分')		
		#status = 0
	except ValueError:
		msg = TextSendMessage(text = '評分失敗')
	return msg

# 關鍵字搜尋
def Search_Movie2(event, type):
	print("######### Search_Movie2 ########")
	global buffer2
	if type == 1:
		movie_name = event.message.text
		if movie_name[-1] == ' ':
			movie_name = movie_name[0:-1]
		buffer2 = []
		for movie in movieTable:
			if movie_name.lower() in movie.nameEnglish.lower():
				buffer2.append(movie)
		if buffer2:
			sub = min(5, len(buffer2))
			sub_buffer = buffer2[0:sub]
			msg = Carousel_template2(event, sub_buffer, movie_name, 2)
		else: # 沒有找到電影
			msg = TemplateSendMessage(
				alt_text = 'ConfirmTemplate',
				template = ConfirmTemplate(
					text = '搜尋失敗，是否要重新搜尋？',
					actions = [
						PostbackTemplateAction(
							label = '是',
							data = 'action=2-1'
						),
						PostbackTemplateAction(
							label = '否',
							data = 'action=2-3'
						)
					]
				)
			)
	elif type == 2:
		if len(buffer2) > 5:
			buffer2 = buffer2[5:]
			sub = min(5, len(buffer2))
			sub_buffer = buffer2[0:sub]
			if buffer2:
				msg = Carousel_template2(event, sub_buffer, None, 2)
			else:
				msg = None
		else:
			buffer2 = []
			msg = TextSendMessage(text = '沒有更多電影')
	return msg

# 處理"模板點擊"
@handler.add(PostbackEvent)
def handle_postback(event):
	print("######### handle_postback ########")
	global status, scoring
	id = str(event.source.user_id)
	Restore_Status(id)
	if event.postback.data == 'action=0':
		status = 0
		message = Menu(None, 0)
	elif event.postback.data == 'action=1-1':
		message = Get_Playing2(event, 1)
	elif event.postback.data == 'action=1-2':
		message = Get_Playing2(event, 2)
	elif event.postback.data == 'action=2-1':
		status = 2
		message = TextSendMessage(text = '請輸入欲查詢的電影名稱(英文)')
	elif event.postback.data == 'action=2-2': # 關鍵字搜尋附帶頁: 顯示更多
		#status = 2
		message = Search_Movie2(event, 2)
	elif event.postback.data == 'action=2-3': # 關鍵字搜尋失敗, status歸零
		status = 0
		message = TextSendMessage(text = '關鍵字搜尋結束')
	elif event.postback.data[0:10] == 'action=3-1':
		text = event.postback.data[10:].split('\n')
		message = Same_Category3(event, text, 1)
	elif event.postback.data == 'action=3-2':
		message = Same_Category3(event, None, 2)
	elif event.postback.data == 'action=3-3':
		message = Same_Category3(event, None, 3)
	elif event.postback.data == 'action=4-1':
		message = Read_Personal_Record(event, True)
	elif event.postback.data[0:10] == 'action=5-1':
		status = 5
		scoring = event.postback.data[10:].split('\n')
		print(scoring)
		message = TextSendMessage(text='請輸入分數(0.0~5.0)')
	elif event.postback.data == 'action=6-1':
		message = Recommend2(event, 1)
	elif event.postback.data == 'action=6-2':
		message = Recommend2(event, 2)
	else:
		message = Menu(None, 0)
	line_bot_api.reply_message(event.reply_token, message)
	Store_Status(id)

# 以ChatGPT回覆訊息
def Call_ChatGPT(text):
	response = openai.Completion.create(
		model = 'text-davinci-003',
		prompt = text,
		max_tokens = 512, # max_tokens 最大為2048
		temperature = 0.5
	)
	msg = 'ChatGPT: '+response['choices'][0]['text'].replace('\n', '', 2)
	return TextSendMessage(text = msg)

# 雷達回波圖
def Get_RadarEcho():
	return ImageSendMessage(original_content_url = 'https://cwbopendata.s3.ap-northeast-1.amazonaws.com/MSC/O-A0058-003.png',
							preview_image_url = 'https://cwbopendata.s3.ap-northeast-1.amazonaws.com/MSC/O-A0058-003.png')

# 處理"訊息發送"
#@handler.add(MessageEvent, message = TextMessage) # 僅處理文字訊息
@handler.add(MessageEvent)
def handle_message(event):
	print("######### handle_message ########")
	global status
	# profile = line_bot_api.get_profile(event.source.user_id)
	# profile.display_name = 使用者Line暱稱
	# event.source.user_id = 使用者Line帳戶ID
	# event.source.room_id = Line聊天室ID
	# event.message.text = 使用者輸入訊息
	id = str(event.source.user_id)
	if status in (2, 5):
		print('  >>> 電影推薦機器人 <<<')
		Restore_Status(id)
		if status == 2: # 關鍵字搜尋
			message = Search_Movie2(event, 1)
		elif status == 5: # 給予評分
			message = Score_message(event.message.text, scoring)
		status = 0
		Store_Status(id)
	elif event.message.type == 'location':
		print('  >>> 氣象預報機器人 <<<')
		address = event.message.address
		msg = address+'\n'+Get_Weather(address)+'\n'+Get_AQI(address)+'\n'+Get_Forecast(address)
		message = TextSendMessage(text = msg)
	else: # event.message.type == 'text'
		text = event.message.text
		if len(text) > 9 and text[:9] == "@電影推薦機器人：":
			print('  >>> 電影推薦機器人 <<<')
			text = text[9:]
			Restore_Status(id)
			if text == "近期上映":
				message = Get_Playing2(event, 1)
			elif text == "關鍵字搜尋":
				status = 2
				message = TextSendMessage(text = '請輸入欲查詢的電影名稱(英文)')
			elif text == "智慧推薦":
				message = Recommend2(event, 1)
			elif text == "評分紀錄":
				message = Read_Personal_Record(event, True)
			else:
				status = 0
				message = Menu(None, 0)
			Store_Status(id)
		elif text == "@雷達回波圖":
			print('  >>> 雷達回波圖 <<<')
			message = Get_RadarEcho()
		elif text == "@地震資訊":
			print('  >>> 地震資訊 <<<')
			msg, img = Get_Earthquake()
			if not img:
				img = error_picture
			message = [TextSendMessage(text = msg), ImageSendMessage(original_content_url = img, preview_image_url = img)]
		else:
			print('  >>> ChatGPT <<<')
			message = Call_ChatGPT(text)
	#message = TextSendMessage(text=event.message.text)
	#message = TextSendMessage(text=event.source.user_id)
	#message = TextSendMessage(text=event.source.room_id)
	#message = TextSendMessage(text=str(len(movieAll)))
	line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
	print("######### __name__ ########")
	global status
	status = 0
	port = int(os.environ.get('PORT', 5000))
	Read_All_Data2()
	Classification()
	KNN_Result()
	app.run(host='0.0.0.0', port=port)
