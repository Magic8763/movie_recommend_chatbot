from flask import Flask, request, abort # pip install flask
from linebot import LineBotApi, WebhookHandler # pip install line-bot-sdk
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ImageSendMessage, 
	PostbackEvent, PostbackTemplateAction, URITemplateAction,
	CarouselColumn, CarouselTemplate, ButtonsTemplate, ConfirmTemplate
)
from weather import Get_Weather, Get_Forecast, Get_AQI, Get_Earthquake, Get_RadarEcho
import os
import random
import datetime
import pandas as pd
import numpy as np
import openai # pip install openai
import pickle
import threading
import time

app = Flask(__name__)
# Channel Access Token(YOUR_CHANNEL_ACCESS_TOKEN)
line_bot_api = LineBotApi('t6pQxlob2d6HG7eli4Ck0y0yq49zE03JiedrVk2rjmHu3StIrdyGijxM+jQqXj+oSniedXwjZqkuHNZHntBe8k1hf2qccsdJsgaEPvAVHfNb6wJ6LX3zmiLACCJQ1/leSRmgaXWecMZq48aMVYEvqQdB04t89/1O/w1cDnyilFU=')
# Channel Secret(YOUR_CHANNEL_SECRET)
handler = WebhookHandler('f618a9e80020ea18a0a16b2c4643bbb5')
# OPENAI_API_KEY
openai.api_key = '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'

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
honmpage_picture = 'https://attach.setn.com/newsimages/2017/02/10/805406-XXL.jpg'
missing_picture = 'https://cdn0.techbang.com/system/excerpt_images/55555/original/d5045073e258563e2b62eed24605cd60.png?1512550227'
default_picture = 'https://m.media-amazon.com/images/G/01/imdb/images/social/imdb_logo.png'
playing_k = 20 # 近期上映的前k部電影
carousel_size = 20 # 旋轉模板長度上限

class Movie2:
	def __init__(self, id = None, name = None, title = None, t = None):
		self.id = id
		self.nameEnglish = name
		self.title = title
		self.year = t
		self.genres = []
		self.grade = None
		self.imdbId = None
		self.picture= None

def writeVar(obj, drt, fname):
	if not os.path.exists(drt):
		os.mkdir(drt)
	with open(drt+'/'+fname, 'wb') as file:
		pickle.dump(obj, file)

def readVar(drt, fname, return_dict=False):
	obj = {} if return_dict else []
	if os.path.exists(drt+'/'+fname):
		with open(drt+'/'+fname, 'rb') as file:
			obj = pickle.load(file)
	return obj

# 讀資料檔
def Read_All_Data2():
	print("######### Read_All_Data2 ########")
	global movieTable, genresTable, nameTable
	movieTable = readVar('var', 'movieTable')
	genresTable = readVar('var', 'genresTable')
	nameTable = readVar('var', 'nameTable', True)
	if movieTable and genresTable and nameTable:
		print('  movieTable:', len(movieTable))
		print('  genresTable:', len(genresTable))
		print('  nameTable:', len(nameTable))
		return
	df = pd.read_csv('data/movies_extended_known_sorted.csv', sep = ',')
	genresTable = [[] for _ in range(0, len(genres_dict))]
	for i in range(0, len(df)):
		movieId, movieName, movieTitle = str(df['movieId'].iloc[i]), str(df['nameEnglish'].iloc[i]), str(df['title'].iloc[i])
		nameTable[movieId] = (i, movieTitle)
		movie = Movie2(movieId, movieName, movieTitle, str(df['year'].iloc[i]))
		if df['genres'].iloc[i] != 'N/A' and df['genres'].iloc[i] != '(no genres listed)':
			movie.genres = str(df['genres'].iloc[i]).split('|')
			for tp in movie.genres: # 電影分類
				genresTable[genres_dict[tp][0]].append(i)
		movie.imdbId = 'https://www.imdb.com/title/'+str(df['imdbId'].iloc[i])
		if df['grade'].iloc[i] != 'N/A':
			movie.grade = str(df['grade'].iloc[i])
		if df['picture'].iloc[i] != 'N/A':
			movie.picture = str(df['picture'].iloc[i])
		else:
			movie.picture = missing_picture
		movieTable.append(movie)
	writeVar(movieTable, 'var', 'movieTable')
	writeVar(genresTable, 'var', 'genresTable')
	writeVar(nameTable, 'var', 'nameTable')

# KNN推薦結果
def KNN_Recommend():
	print("######### KNN_Recommend ########")
	global recommends
	recommends = readVar('var', 'recommends', True)
	if not recommends:
		df = pd.read_csv('data/knn_recommend_sorted.csv', sep = ',')
		df = df.to_numpy().astype(int)
		for i in range(0, len(df)):
			recommends[df[i][0]] = df[i][1:]
	else:
		print('  recommends:', len(recommends))

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
		line_bot_api.reply_message(event.reply_token, message)
		status_dict = self.save_status()
		writeVar(status_dict, 'user', uid)

	def new_user(self, uid):
		self.uid, self.status, self.phase = uid, 0, 0 # phase尚未使用
		self.GP_ii, self.SC_ii, self.SC_jj = 0, 0, 0
		self.category2, self.category3, self.buffer2 = [], [], []
		self.scoring, self.aibuf, self.searched = [], [], [] # searched: 追蹤最近查詢/評分/點擊的3部電影idx

	def load_status(self, status_dict):
		self.uid, self.status, self.phase = status_dict['uid'], status_dict['status'], status_dict['phase']
		self.GP_ii, self.SC_ii, self.SC_jj = status_dict['GP_ii'], status_dict['SC_ii'], status_dict['SC_jj']
		self.category2, self.category3, self.buffer2 = status_dict['category2'], status_dict['category3'], status_dict['buffer2']
		self.scoring, self.aibuf, self.searched = status_dict['scoring'], status_dict['aibuf'], status_dict['searched']

	def save_status(self):
		return {'uid': self.uid, 'status': self.status, 'phase': self.phase,
				'GP_ii': self.GP_ii, 'SC_ii': self.SC_ii, 'SC_jj': self.SC_jj,
				'category2': self.category2, 'category3': self.category3, 'buffer2': self.buffer2,
				'scoring': self.scoring, 'aibuf': self.aibuf, 'searched': self.searched}

	def Message_text(self, event):
		if self.status in (2, 5):
			print('  >>> 電影推薦機器人 <<<')
			#Restore_Status(id)
			if self.status == 2: # 關鍵字搜尋
				message = self.Search_Movie2(1, event.message.text)
			elif self.status == 5: # 給予評分
				message = self.Score_message(event.message.text)
			self.status = 0
			#Store_Status(id)
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
				#Restore_Status(id)
				if text == "近期上映":
					message = self.Get_Playing2(1)
				elif text == "關鍵字搜尋":
					self.status = 2
					message = TextSendMessage(text = '請輸入欲查詢的電影名稱(英文)')
				elif text == "智慧推薦":
					message = self.Recommend2()
				elif text == "評分紀錄":
					message = self.Read_Personal_Record(True)
				else:
					self.status = 0
					message = self.Menu(None, 0)
				#Store_Status(id)
			elif text == "@雷達回波圖":
				print('  >>> 雷達回波圖 <<<')
				message = Get_RadarEcho()
			elif text == "@地震資訊":
				print('  >>> 地震資訊 <<<')
				msg, img = Get_Earthquake()
				if not img:
					img = missing_picture
				message = [TextSendMessage(text = msg), ImageSendMessage(original_content_url = img, preview_image_url = img)]
			else:
				print('  >>> ChatGPT <<<')
				message = self.Call_ChatGPT(text)
		return message

	def Message_Postback(self, event):
		if event.postback.data == 'action=0':
			self.status = 0
			message = self.Menu(None, 0)
		elif event.postback.data == 'action=1-1':
			message = self.Get_Playing2(1)
		elif event.postback.data == 'action=1-2':
			message = self.Get_Playing2(2)
		elif event.postback.data == 'action=2-1':
			self.status = 2
			message = TextSendMessage(text = '請輸入欲查詢的電影名稱(英文)')
		elif event.postback.data == 'action=2-2': # 關鍵字搜尋附帶頁: 顯示更多
			#self.status = 2
			message = self.Search_Movie2(2)
		elif event.postback.data == 'action=2-3': # 關鍵字搜尋失敗, self.status歸零
			self.status = 0
			message = TextSendMessage(text = '關鍵字搜尋結束')
		elif event.postback.data[0:10] == 'action=3-1':
			text = event.postback.data.split('\n')[1:]
			self.Update_Searched(text[0])
			message = self.Same_Category3(text[1:], 1)
		elif event.postback.data == 'action=3-2':
			message = self.Same_Category3(None, 2)
		elif event.postback.data == 'action=3-3':
			message = self.Same_Category3(None, 3)
		elif event.postback.data == 'action=4-1':
			message = self.Read_Personal_Record(True)
		elif event.postback.data[0:10] == 'action=5-1':
			self.status = 5
			self.scoring = event.postback.data.split('\n')[1:]
			message = TextSendMessage(text = '請輸入分數(1~10)')
		elif event.postback.data == 'action=6-1':
			message = self.Recommend2(False)
		elif event.postback.data == 'action=6-2':
			message = self.Recommend2(True)
		else:
			message = self.Menu(None, 0)
		return message

	# 主選單
	def Menu(self, keyword, home):
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
				title = '\"'+keyword+'\"的搜尋結果',
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

	# 製作訊息模板
	def Carousel_template2(self, sub_buffer, text, home):
		print("######### Carousel_template2 ########")
		template_list = []
		for i in range(0, len(sub_buffer)):
			if len(sub_buffer[i].title) > 40:
				continue
			movie_info = 'action=5-1\n'+sub_buffer[i].id+'\n'+sub_buffer[i].title
			context = '('+str(sub_buffer[i].year)+')'
			if sub_buffer[i].genres:
				sub	= Translater(sub_buffer[i].genres, 1)
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
				thumbnail_image_url = sub_buffer[i].picture,
				title = sub_buffer[i].title,
				text = context,
				actions = [
					URITemplateAction(
						label = 'IMDb主頁',
						uri = sub_buffer[i].imdbId
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
		template_list.append(self.Menu(text, home))
		msg = TemplateSendMessage(
			alt_text = 'Carousel template',
			template = CarouselTemplate(
				columns = template_list
			)
		)
		return msg

	# 近期上映
	def Get_Playing2(self, type):
		print("######### Get_Playing2 ########")
		if type == 1:
			self.GP_ii = len(movieTable)-playing_k
		if self.GP_ii < len(movieTable):
			sub = min(self.GP_ii+5, len(movieTable))
			sub_buffer = movieTable[self.GP_ii:sub]
			msg = self.Carousel_template2(sub_buffer, None, 1)
			self.GP_ii = sub
		elif type == 1:
			msg = TextSendMessage(text = '沒有任何電影')
		elif type == 2:
			self.GP_ii = len(movieTable)-playing_k
			msg = TextSendMessage(text = '沒有更多電影')
		return msg

	# 相關性同類推薦
	def Same_Category3(self, text, type):
		print("######### Same_Category3 ########")
		if type == 1: # 同類推薦
			self.category2, self.category3 = [], [] # 電影清單, 類型清單
			movieidx, genres_english = int(text[-1]), text[:-1]
			cpbuf = set(recommends[movieidx]) if movieidx in recommends.keys() else set() # 優先從KNN推薦結果中篩選具有相同類型者
			genres_indices, genres_zhtw = Translater(genres_english, 0), Translater(genres_english, 1)
			for l in range(0, len(genres_english)):
				tybuf = set()
				for cp in cpbuf:
					if genres_english[l] in movieTable[cp].genres:
						tybuf.add(cp)
				while len(tybuf) < carousel_size:
					picked = random.sample(range(len(genresTable[genres_indices[l]])), 1)[0]
					tybuf.add(genresTable[genres_indices[l]][picked])
				scbuf = [movieTable[tp] for tp in tybuf]
				random.shuffle(scbuf)
				if scbuf:
					self.category2.append(scbuf)
					self.category3.append(genres_zhtw[l])
			self.SC_ii = 0
			if self.category2:
				self.SC_jj = min(self.SC_ii+5, len(self.category2[0]))
				msg = self.Carousel_template2(self.category2[0][self.SC_ii:self.SC_jj], self.category3[0], 3)
			else:
				msg = TextSendMessage(text = '沒有同類電影')
		elif type == 2: # 顯示更多
			if len(self.category2[0])-self.SC_jj >= 1:
				self.SC_ii = self.SC_jj
				self.SC_jj = min(self.SC_ii+5, len(self.category2[0]))
				msg = self.Carousel_template2(self.category2[0][self.SC_ii:self.SC_jj], self.category3[0], 3)
			else:
				msg = TextSendMessage(text = '沒有更多電影')
		elif type == 3: # 下個類型
			if len(self.category2) > 1:
				self.category2, self.category3 = self.category2[1:], self.category3[1:]
				self.SC_jj = min(5, len(self.category2[0]))
				msg = self.Carousel_template2(self.category2[0][:self.SC_jj], self.category3[0], 3)
			else:
				msg = TextSendMessage(text = '沒有更多類型')
		return msg

	# 直接推薦
	def Recommend2(self, get_more=False):
		print("######### Recommend2 ########")
		if get_more and not self.aibuf:
			return TextSendMessage(text = '沒有更多電影')
		elif not get_more:
			picked = set()
			for movieId in self.searched:
				movieidx = nameTable[movieId][0]
				if movieidx in recommends.keys():
					for i in recommends[movieidx]:
						picked.add(i)
			if picked:
				picked = list(picked)
				buf = [picked[i] for i in random.sample(range(len(picked)), min(len(picked), carousel_size))]
			else:
				keys = list(recommends.keys())
				movieidx = random.sample(range(len(keys)), 1)[0] # 隨機一部電影
				movieidx = keys[movieidx]
				buf = recommends[movieidx][:carousel_size] # 直接採用KNN推薦結果
			random.shuffle(buf)
			while len(buf) < carousel_size:
				movieidx = random.sample(range(0, len(movieTable)), 1)
				if movieidx not in picked:
					buf.append(movieidx)
			self.aibuf = [movieTable[i] for i in buf]
		sub_buffer = self.aibuf[:5]
		self.aibuf = self.aibuf[5:]
		msg = self.Carousel_template2(sub_buffer, None, 4)
		return msg

	# 更新紀錄檔
	def Save_Personal_Record(self, movieId, num):
		print("######### Save_Personal_Record ########")
		if not os.path.exists('ratings'):
			os.mkdir('ratings')
		today = datetime.datetime.now()
		try:
			f = open('ratings/HS_'+self.uid+'.txt', 'a', encoding = 'utf8')
			record_str = self.uid+'\t'+str(today.year)+'\t'+str(today.month)+'\t'+str(today.day)+'\t'+movieId+'\t'+str(num)+'\n'
			f.write(record_str)
			f.close()
		except IOError:
			print('更新紀錄檔失敗')

	# 讀取紀錄檔
	def Read_Personal_Record(self, get_msg = True):
		print("######### Read_Personal_Record ########")
		if not os.path.exists('ratings'):
			os.mkdir('ratings')
		try:
			with open('ratings/HS_'+self.uid+'.txt', 'r', encoding = 'utf8') as f:
				read = f.readlines()
			record_str = ''
			for infile in read:
				info = infile.split('\t')
				movieTitle = nameTable[info[4]][1]
				record_str = info[1]+'/'+info[2]+'/'+info[3]+' ['+movieTitle+']: '+info[5]+record_str 
			msg = TextSendMessage(text = record_str) if get_msg else nameTable[info[4]][0] # get_msg==False時返回最後一次評分的電影idx
		except IOError:
			msg = TextSendMessage(text = '查無本id的紀錄') if get_msg else None
		return msg

	# 追蹤最近(給予評分/同類推薦)的3部電影idx
	def Update_Searched(self, movieId):
		print("######### Update_Searched ########")
		if movieId not in self.searched:
			self.searched.append(movieId)
		if len(self.searched) > 3:
			self.searched.pop(0)
		print(' Update ', self.uid, ', searched: ', self.searched, sep='')

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
			#self.Save_Personal_Record(movieName, num)
			print('****'+ self.uid+'****'+movieId+'****'+movieName+'****'+str(num)+'****')
			msg = TextSendMessage(text = '已評分')		
		except ValueError:
			msg = TextSendMessage(text = '評分失敗')
		return msg

	# 關鍵字搜尋
	def Search_Movie2(self, type, input_text = ''):
		print("######### Search_Movie2 ########")
		if type == 1:
			movie_name = input_text.lower().replace(' ', '')
			"""
			self.buffer2 = []
			for movie in movieTable:
				if movie_name in movie.nameEnglish or movie_name in movie.title:
					self.buffer2.append(movie)
			"""
			self.buffer2 = [movie for movie in movieTable if movie_name in movie.nameEnglish or movie_name in movie.title]
			if self.buffer2:
				sub = min(5, len(self.buffer2))
				sub_buffer = self.buffer2[0:sub]
				msg = self.Carousel_template2(sub_buffer, input_text, 2)
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
			if len(self.buffer2) > 5:
				self.buffer2 = self.buffer2[5:]
				sub = min(5, len(self.buffer2))
				sub_buffer = self.buffer2[0:sub]
				msg = self.Carousel_template2(sub_buffer, None, 2) if self.buffer2 else None
			else:
				self.buffer2 = []
				msg = TextSendMessage(text = '沒有更多電影')
		return msg

	# 以ChatGPT回覆訊息
	def Call_ChatGPT(self, text):
		response = openai.Completion.create(
			model = 'text-davinci-003',
			prompt = text,
			max_tokens = 512, # max_tokens 最大為2048
			temperature = 0.5
		)
		msg = 'ChatGPT: '+response['choices'][0]['text'].replace('\n', '', 2)
		return TextSendMessage(text = msg)

# 監聽所有來自'.../'的 Post Request
@app.route("/", methods = ['POST'])
def linebot(): # 每個訊息的首站
	print("\n######### linebot running ########")
	signature = request.headers['X-Line-Signature'] # get X-Line-Signature header value
	body = request.get_data(as_text = True) # get request body as text
	app.logger.info("Request body: "+body)
	try:
		handler.handle(body, signature) # handle webhook body
	except InvalidSignatureError:
		abort(400)
	return 'OK'

def Threading_Handle(event, isPostback=False):
	print("######### Threading_Handle ########")
	req = Request_Handle(event, isPostback)
	time.sleep(1)

# 處理"模板點擊"
@handler.add(PostbackEvent)
def handle_postback(event):
	print("######### handle_postback ########")
	req = Request_Handle(event, True)
	"""
	thread = threading.Thread(target = Threading_Handle, args = (event, True)) # 以thread生成
	thread.start()
	"""

# 處理"訊息發送"
@handler.add(MessageEvent)
def handle_message(event):
	print("######### handle_message ########")
	# profile = line_bot_api.get_profile(event.source.user_id)
	# profile.display_name = 使用者Line暱稱
	# event.source.user_id = 使用者Line帳戶ID
	# event.source.room_id = Line聊天室ID
	# event.message.text = 使用者輸入訊息
	req = Request_Handle(event, False) # 以thread生成
	"""
	thread = threading.Thread(target = Threading_Handle, args = (event, False)) # 以thread生成
	thread.start()
	"""

"""
if __name__ == "__main__": # 當app.py是被執行而非被引用時, 執行下列程式碼
	print("\n######### main ########")
	Read_All_Data2()
	KNN_Recommend()
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port = port) # 以linebot()接收請求
"""
print("\n######### main ########")
Read_All_Data2()
KNN_Recommend()
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port = port) # 以linebot()接收請求