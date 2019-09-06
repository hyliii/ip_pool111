# coding:utf-8
# from db.SqlHelper import SqlHelper
# from util.exception import Con_DB_Fail
# try:
#     sqlhelper = SqlHelper()
#     sqlhelper.init_db()
# except Exception:
#     raise Con_DB_Fail
# proxy = {'ip': '192.168.1.1', 'port': int('80'), 'type': 0, 'protocol': 0, 'country': u'中国', 'area': u'四川', 'speed': 0}
# speed = [{'pro_speed': '0.001', 'company': '车智汇通'}]
# sqlhelper.insert(proxy,speed)


from test.my_ForeignKey import Student, ClassTable,engine
from sqlalchemy.orm import sessionmaker
DB_session = sessionmaker(engine)
db_session = DB_session()
# 1.查询所有数据,并显示班级名称,连表查询
student_list = db_session.query(Student).all()
for row in student_list:
    print(row.name,row.to_class.name,row.class_id)
# 2.反向查询
class_list = db_session.query(ClassTable).all()
for row in class_list:
    for row2 in row.stu2class:
        print(row.name,row2.name)
# row.stu2class 通过 backref 中的 stu2class 反向关联到 Student 表中根据ID获取name
db_session.close()