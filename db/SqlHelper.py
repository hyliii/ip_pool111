import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, create_engine, VARCHAR, ForeignKey, engine, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.testing import db
import config
from config import DB_CONFIG, DEFAULT_SCORE
from db.ISqlHelper import ISqlHelper
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import and_ , or_
'''
sql操作的基类
ip池建表字段：
    id(主键)
    ip（ip号）
    port（端口号）
    t_way(免费/付费)
    protocol（0：http,1:https,2:http/https）
    country(国内/国外)
    addr(城市代码)
    t_service(服务类型,电信/联通/移动)
    usable_time（采集时间+时效）
    Update_time（检测时间）
    score（可被取用次数）
    attr(属性，0：采集未检测，1：采集并检测)
'''
BaseModel = declarative_base()
class T_area(BaseModel):
    __tablename__ = 't_area'
    id = Column(Integer, primary_key=True, autoincrement=True)
    provinceId=Column(Integer,nullable=False)
    provinceName=Column(VARCHAR(255), nullable=False)
    provinceLetter=Column(VARCHAR(2), nullable=False)
    cityId=Column(Integer,nullable=False)
    cityName=Column(VARCHAR(255), nullable=False)
    cityLetter=Column(VARCHAR(2), nullable=False)
    cityPinyin=Column(VARCHAR(30), nullable=False)
    state=Column(Integer,nullable=False)
    lng=Column(Float(20),nullable=False)
    lat=Column(Float(20),nullable=False)
    yicheProvinceId=Column(Integer,nullable=False)
    yicheCityId=Column(Integer,nullable=False)
    yicheCityPinyin=Column(VARCHAR(30), nullable=False)
    areaNum=Column(VARCHAR(4), nullable=False)
    proxy= relationship('Proxy', backref='t_area')
class Proxy(BaseModel):
    __tablename__ = 'proxys'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(VARCHAR(20), nullable=False)
    port = Column(Integer, nullable=False)
    t_way = Column(Integer, nullable=False)
    protocol = Column(Integer, nullable=False, default=0)
    country = Column(VARCHAR(20), nullable=False)
    addr_id = Column(Integer,ForeignKey('t_area.cityId', ondelete='CASCADE'), nullable=False)
    t_service = Column(VARCHAR(100), nullable=False)
    usable_time = Column(DateTime,default=datetime.datetime.now)
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    score = Column(Integer, nullable=False, default=DEFAULT_SCORE)
    attr=Column(Integer, nullable=False,default=0)
    speed = relationship('Speed', backref='proxys')
class Speed(BaseModel):
    __tablename__ = 'speeds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_id=Column(Integer, ForeignKey('proxys.id', ondelete='CASCADE'),nullable=False)
    pro_speed = Column(Numeric(5, 2), nullable=False)
    company=Column(VARCHAR(50), nullable=False)
class SqlHelper(ISqlHelper):
    #数据库选择器类！！！
    params = {'ip': Proxy.ip, 'port': Proxy.port, 't_way ':Proxy.t_way ,'protocol': Proxy.protocol,'country': Proxy.country, 'addr_id':Proxy.addr_id,'t_service':Proxy.t_service, 'usable_time':Proxy.usable_time,'update_time':Proxy.update_time,'score': Proxy.score,'attr':Proxy.attr}
    def __init__(self):
        if 'sqlite' in DB_CONFIG['DB_CONNECT_STRING']:
            connect_args = {'check_same_thread': False}
            self.engine = create_engine(DB_CONFIG['DB_CONNECT_STRING'], echo=False, connect_args=connect_args)
        else:
            self.engine = create_engine(DB_CONFIG['DB_CONNECT_STRING'], echo=False)
        DB_Session = sessionmaker(bind=self.engine)
        self.session = DB_Session()
    def init_db(self):
        BaseModel.metadata.create_all(self.engine)
    def drop_db(self):
        BaseModel.metadata.drop_all(self.engine)
    def insert(self,value1,value2):
        if value2[0][0]<50 or value2[0][1]<50 :
            addr_ids = self.session.query(T_area).filter(T_area.cityName == value1['addr_id']).first().cityId
            proxy_obj = Proxy(ip=value1['ip'], port=value1['port'], t_way=value1['t_way'], protocol=value1['protocol'],country=value1['country'],addr_id=addr_ids, t_service=value1['t_service'],attr=value1['attr'])
            self.session.add(proxy_obj)
            ip_ids = self.session.query(Proxy).filter(and_(Proxy.ip == value1['ip'], Proxy.port == value1['port'])).first().id
            for i in range(2,len(value2[0])):
                if value2[0][i]<1000:
                    speed_add=Speed(pro_speed=value2[0][i],company=value2[1][i],ip_id=ip_ids)
                    self.session.add(speed_add)
            self.session.commit()
    def delete(self, conditions=None):
        if conditions:
            conditon_list = []
            for key in list(conditions.keys()):
                if self.params.get(key):
                    conditon_list.append(self.params.get(key) == conditions.get(key))
            conditions = conditon_list
            query = self.session.query(Proxy)
            for condition in conditions:
                query = query.filter(condition)
            deleteNum = query.delete()
            self.session.commit()
        else:
            deleteNum = 0
        return ('deleteNum', deleteNum)
    def update(self, conditions=None, value=None):
        if conditions and value:
            from validator.Validator import getMyIP, checkSped
            selfip = getMyIP()
            speeds = checkSped(selfip, conditions)
            if speeds:
                if speeds[0]<50 or speeds[1]<50:
                    conditon_list = []
                    for key in list(conditions.keys()):
                        if self.params.get(key, None):
                            conditon_list.append(self.params.get(key) == conditions.get(key))
                    conditions = conditon_list
                    query = self.session.query(Proxy)
                    for condition in conditions:
                        query = query.filter(condition)
                    updatevalue = {}
                    for key in list(value.keys()):
                        if self.params.get(key, None):
                            updatevalue[self.params.get(key, None)] = value.get(key)
                    updateNum = query.update(updatevalue)
                    self.session.commit()
                else:
                    self.delete(conditions)
                    updateNum = None
            else:
                self.delete(conditions)
                updateNum = None
        else:
            updateNum=0
        return {'updateNum': updateNum}
    def select(self, count=None, conditions=None):
        if conditions:
            conditon_list =[]
            for key in list(conditions.keys()):
                if self.params.get(key, None):
                    conditon_list.append(self.params.get(key) == conditions.get(key))
            conditions = conditon_list
        else:
            conditions = []
        query = self.session.query(Proxy.ip, Proxy.port, Proxy.score,Proxy.protocol)
        if len(conditions) > 0 and count:
            for condition in conditions:
                query = query.filter(condition)
            return query.order_by(Proxy.score.desc()).limit(count).all()
        elif count:
            return query.order_by(Proxy.score.desc()).limit(count).all()
        elif len(conditions) > 0:
            for condition in conditions:
                query = query.filter(condition)
            return query.order_by(Proxy.score.desc()).all()
        else:
            return query.order_by(Proxy.score.desc()).all()
    def close(self):
        pass
if __name__ == '__main__':
    sqlhelper = SqlHelper()
    sqlhelper.init_db()
    proxy = {'ip': '192.168.1.1', 'port': 80,'t_way':0, 'type': 0, 'protocol': 0, 'country': '中国', 'addr_id': '广州','t_service':'电信' ,'score':20,'attr':0}
    speed=[{'pro_speed':'0.001','company':'车智汇通'}]
    sqlhelper.insert(proxy,speed)
    sqlhelper.update({'ip': '192.168.1.1', 'port': 80}, {'score': 10})
    print(sqlhelper.select(1))