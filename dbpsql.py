
from flask import Flask
from flask_sqlalchemy import SQLAlchemy # pip install flask_sqlalchemy
from datetime import datetime
# import os

app = Flask(__name__)
# [DB_TYPE]+[DB_CONNECTOR]://[USERNAME]:[PASSWORD]@[HOST]:[PORT]/[DB_NAME]
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') # 使用Render上的環境變數
db = SQLAlchemy(app) # pip3 install psycopg2-binary

class userRatings(db.Model):
    __tablename__ = 'userRatings' # 目標資料表
    __table_args__ = {'keep_existing': True}
    id = db.Column(db.Integer, primary_key = True) # 整數型主鍵
    uid =db.Column(db.Integer) # 整數型用戶ID
    movie = db.Column(db.String(6)) # 字串型電影ID (長度上限=6)
    rating = db.Column(db.Integer) # 整數型評分
    timestamp = db.Column(db.TIMESTAMP, default=datetime.now) # 時間型時間戳記

    def __init__(self, userId, movieId, rating): # 建構子
        # 不指定 self.id,self.timestamp時, 兩者便會自動採用預設值
        self.uid = userId
        self.movie = movieId
        self.rating = rating

    # GET: 讀取用戶所有的評分紀錄
    def Record_reader(userId):
        with app.app_context():
            records = userRatings.query.filter_by(uid=userId).all() # filter_by同WHERE
        return records

    # POST: 上傳用戶本次評分紀錄
    def Record_adder(userId, movieId, rating):
        with app.app_context():
            rows = userRatings(userId, movieId, rating)
            db.session.add(rows)
            db.session.commit()

    # DELETE: 移除用戶對指定電影的所有評分紀錄
    def Record_remover(userId, movieId):
        with app.app_context():
            rows = userRatings.query.filter_by(uid=userId, movie=movieId).all()
            for row in rows:
                db.session.delete(row)
            db.session.commit()

    # PUT: 以給定電影ID替換指定電影ID
    def Record_updater(target, movieId):
        with app.app_context():
            rows = userRatings.query.filter_by(movie=target).all()
            for row in rows:
                row.movie = movieId
            db.session.commit()

class userIDs(db.Model):
    __tablename__ = 'userIDs' # 目標資料表
    __table_args__ = {'keep_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    lineID = db.Column(db.String(40))
    timestamp = db.Column(db.TIMESTAMP, default=datetime.now)

    def __init__(self, userId):
        # 不指定 self.id,self.timestamp時, 兩者便會自動採用預設值
        self.lineID = userId

    # GET: 讀取用戶資料
    def User_reader(userId):
        with app.app_context():
            row = userIDs.query.filter_by(lineID=userId).first()
        return row

    # POST: 上傳用戶資料
    def User_adder(userId):
        with app.app_context():
            rows = userIDs(userId)
            db.session.add(rows)
            db.session.commit()

with app.app_context():
    db.create_all() # 創建空資料表