
import requests, json, statistics
import os

# 氣象資料開放平台授權碼
AuthorizationCode = os.environ.get('AuthorizationCode')
# 雷達回波圖, 伺服器端未更新為cwa
RadarEcho_url = 'https://cwbopendata.s3.ap-northeast-1.amazonaws.com/MSC/O-A0058-003.png'

# 本地天氣狀況
def Get_Weather(address):
	city_list, area_list, area_list2 = {}, {}, {} # 定義好待會要用的變數

	# 定義取得資料的函式
	def get_data(url):
		w_data = requests.get(url) # 爬取目前天氣網址的資料
		w_data_json = w_data.json() # json 格式化訊息內容
		location = w_data_json['cwaopendata']['location'] # 取出對應地點的內容
		for i in location:
			name = i['locationName'] # 測站地點
			city = i['parameter'][0]['parameterValue'] # 縣市名稱
			area = i['parameter'][2]['parameterValue'] # 鄉鎮行政區
			temp = float(i['weatherElement'][3]['elementValue']['value']) # 氣溫
			humd = max(float(round(float(i['weatherElement'][4]['elementValue']['value'] )*100 , 1)), 0) # 相對濕度
			r24 = max(float(i['weatherElement'][6]['elementValue']['value']), 0) # 累積雨量
			if area not in area_list:
				area_list[area] = {'temp': temp, 'humd': humd, 'r24': r24} # 以鄉鎮區域為 key，儲存需要的資訊
			if city not in city_list:
				city_list[city] = {'temp':[], 'humd':[], 'r24':[]} # 以主要縣市名稱為 key，準備紀錄裡面所有鄉鎮的數值
			city_list[city]['temp'].append(temp) # 記錄主要縣市裡鄉鎮區域的溫度 ( 串列格式 )
			city_list[city]['humd'].append(humd) # 記錄主要縣市裡鄉鎮區域的濕度 ( 串列格式 )
			city_list[city]['r24'].append(r24) # 記錄主要縣市裡鄉鎮區域的雨量 ( 串列格式 )

	# 定義產生回傳訊息的函式
	def msg_content(loc):
		for i in loc:
			if i in address: # 如果地址裡存在 key 的名稱
				temp = f"氣溫 {loc[i]['temp']} 度，"
				humd = f"相對濕度 {loc[i]['humd']}%，" if loc[i]['humd'] > 0 else ''
				r24 = f"累積雨量 {loc[i]['r24']}mm" if loc[i]['r24'] > 0 else ''
				description = f'{temp}{humd}{r24}'.strip('，')
				return f'{description}。' # 取出 key 的內容作為回傳訊息使用
		return '找不到氣象資訊。'

	try:
		# 因為目前天氣有兩組網址，兩組都爬取
		#get_data(f'https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0001-001?Authorization={AuthorizationCode}&downloadType=WEB&format=JSON')
		get_data(f'https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0003-001?Authorization={AuthorizationCode}&downloadType=WEB&format=JSON')
		"""
		for i in city_list:
			if i not in area_list2: # 將主要縣市裡的數值平均後，以主要縣市名稱為 key，再度儲存一次，如果找不到鄉鎮區域，就使用平均數值
				area_list2[i] = {'temp':round(statistics.mean(city_list[i]['temp']), 1),
								'humd':round(statistics.mean(city_list[i]['humd']), 1),
								'r24':round(statistics.mean(city_list[i]['r24']), 1)
								}
		#return msg_content(area_list2)  # 將訊息改為「大縣市」
		"""
		return msg_content(area_list)   # 將訊息改為「鄉鎮區域」
	except:
		pass
	return '找不到氣象資訊。'

# 本地天氣預報
def Get_Forecast(address):
	"""
	# 將主要縣市個別的 JSON 代碼列出
	json_api = {"宜蘭縣":"F-D0047-001","桃園市":"F-D0047-005","新竹縣":"F-D0047-009","苗栗縣":"F-D0047-013",
				"彰化縣":"F-D0047-017","南投縣":"F-D0047-021","雲林縣":"F-D0047-025","嘉義縣":"F-D0047-029",
				"屏東縣":"F-D0047-033","臺東縣":"F-D0047-037","花蓮縣":"F-D0047-041","澎湖縣":"F-D0047-045",
				"基隆市":"F-D0047-049","新竹市":"F-D0047-053","嘉義市":"F-D0047-057","臺北市":"F-D0047-061",
				"高雄市":"F-D0047-065","新北市":"F-D0047-069","臺中市":"F-D0047-073","臺南市":"F-D0047-077",
				"連江縣":"F-D0047-081","金門縣":"F-D0047-085"}
	"""
	try:
		url = f'https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization={AuthorizationCode}&downloadType=WEB&format=JSON'
		f_data = requests.get(url) # 取得主要縣市預報資料
		f_data_json = f_data.json() # json 格式化訊息內容
		location = f_data_json['cwaopendata']['dataset']['location'] # 取得全縣市的預報內容
		for i in location:
			city = i['locationName'] # 縣市名稱
			if city in address:
				wx8 = i['weatherElement'][0]['time'][0]['parameter']['parameterName'] # 天氣現象
				maxt8 = i['weatherElement'][1]['time'][0]['parameter']['parameterName'] # 最高溫
				mint8 = i['weatherElement'][2]['time'][0]['parameter']['parameterName'] # 最低溫
				pop8 = i['weatherElement'][2]['time'][0]['parameter']['parameterName'] # 降雨機率
				return f'未來 8 小時{wx8}，最低溫 {mint8} 度，最高溫 {maxt8} 度，降雨機率 {pop8}%。' # 組合成回傳的訊息，存在以縣市名稱為 key 的字典檔裡
	except:
		try:
			url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/{json_api[i]}?Authorization={code}&elementName=WeatherDescription'
			f_data = requests.get(url)  # 取得主要縣市裡各個區域鄉鎮的氣象預報
			f_data_json = f_data.json() # json 格式化訊息內容
			location = f_data_json['records']['locations'][0]['location']	# 取得預報內容
			for i in location:		  
				city = i['locationName']   # 取得縣市名稱
				if city in address:		   # 如果使用者的地址包含鄉鎮區域名稱
					wd = i['weatherElement'][0]['time'][1]['elementValue'][0]['value']  # 綜合描述
					return f'未來八小時天氣{wd}' # 將 msg 換成對應的預報資訊
		except:
			pass
	return '找不到天氣預報資訊。' # 如果取資料有發生錯誤，直接回傳 msg

# 空氣品質
def Get_AQI(address):
	city_list, site_list = {}, {}
	try:
		url = 'https://data.epa.gov.tw/api/v2/aqx_p_432?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=ImportDate%20desc&format=JSON'
		a_data = requests.get(url)			 # 使用 get 方法透過空氣品質指標 API 取得內容
		a_data_json = a_data.json()			# json 格式化訊息內容
		for i in a_data_json['records']:	   # 依序取出 records 內容的每個項目
			city = i['county']				 # 取出縣市名稱
			if city not in city_list:
				city_list[city] = []			 # 以縣市名稱為 key，準備存入串列資料
			site = i['sitename']			   # 取出鄉鎮區域名稱
			aqi = int(i['aqi'])				# 取得 AQI 數值
			status = i['status']			   # 取得空氣品質狀態
			site_list[site] = {'aqi':aqi, 'status':status}  # 記錄鄉鎮區域空氣品質
			city_list[city].append(aqi)		# 將各個縣市裡的鄉鎮區域空氣 aqi 數值，以串列方式放入縣市名稱的變數裡
		for i in city_list:
			if i in address: # 如果地址裡包含縣市名稱的 key，就直接使用對應的內容
				aqi_val = round(statistics.mean(city_list[i]),0)  # 計算平均數值，如果找不到鄉鎮區域，就使用縣市的平均值
				aqi_status = '' # 手動判斷對應的空氣品質說明文字
				if aqi_val > 300:
					aqi_status = '危害'
				elif aqi_val > 200:
					aqi_status = '非常不健康'
				elif aqi_val > 150:
					aqi_status = '對所有族群不健康'
				elif aqi_val > 100:
					aqi_status = '對敏感族群不健康'
				elif aqi_val > 50:
					aqi_status = '普通'
				else:
					aqi_status = '良好'
				msg = f'空氣品質{aqi_status} ( AQI {aqi_val} )。' # 定義回傳的訊息
				break
		for i in site_list:
			if i in address: # 如果地址裡包含鄉鎮區域名稱的 key，就直接使用對應的內容
				msg = f'空氣品質{site_list[i]["status"]} ( AQI {site_list[i]["aqi"]} )。'
				break
		return msg # 回傳 msg
	except:
		pass
	return '找不到空氣品質資訊。'

# 地震資訊
def Get_Earthquake():
	try:
		url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={AuthorizationCode}'
		e_data = requests.get(url) # 爬取地震資訊網址	 
		e_data_json = e_data.json() # json 格式化訊息內容
		eq = e_data_json['records']['Earthquake'] # 取出地震資訊
		for i in eq:
			loc = i['EarthquakeInfo']['Epicenter']['Location'] # 地震地點
			val = i['EarthquakeInfo']['EarthquakeMagnitude']['MagnitudeValue'] # 地震規模 
			dep = i['EarthquakeInfo']['FocalDepth'] # 地震深度
			eq_time = i['EarthquakeInfo']['OriginTime'] # 地震時間
			img = i['ReportImageURI'] # 地震圖
			return (f'{loc}，芮氏規模 {val} 級，深度 {dep} 公里，發生時間 {eq_time}。', img)
	except:
		pass
	return ('找不到地震資訊。', None)
