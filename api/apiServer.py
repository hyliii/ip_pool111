# coding:utf-8
import json
import sys
import web
import config
from db.DataStore import sqlhelper
urls = ('/', 'select','/delete', 'delete',)
def start_api_server():
    sys.argv.append('0.0.0.0:%s' % config.API_PORT)
    app = web.application(urls, globals())
    app.run()
class select(object):
    def GET(self):
        inputs = web.input()
        count=inputs.get('count', None)
        if count==None:
            count=1
        text=[{'ip':i[0],'port':str(i[1]),'protocol':str(i[3])} for i in sqlhelper.select(count, inputs)]
        json_result = json.dumps(text)
        print('select'+str(json_result))
        return json_result
class delete(object):
    params = {}
    def GET(self):
        inputs = web.input()
        json_result = json.dumps(sqlhelper.delete(inputs))
        print('delect' + str(json_result))
        return json_result
if __name__ == '__main__':
    sys.argv.append('0.0.0.0:8000')
    app = web.application(urls, globals())
    app.run()
    # start_api_server()