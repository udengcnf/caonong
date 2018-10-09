#coding:utf-8

port = '8009'
host = '13.94.31.118'
# host = '127.0.0.1'

start_url = 'http://' + host + ':' + port + '/StartTask'
start_task = {
    'action': 'StartTask',
    'params': {
        'start_time':'2018-01-10 15:48:29', ## 任务开始时间
        'end_time':'2018-12-11 11:27:29', ## 任务结束时间
        'refresh_time':60, ## 页面刷新时间(单位s)
        'user_id':'59bf81e7f8c064d6ad1ea902', ## 创建用户ID
        'content_count':100000,
        'source_id':
        [
            2, 3 ## 信息来源ID
        ],
        'search_type':0, ## 搜索类型(0/单词搜索, 1/分类搜索)
        'search_content':'十九大', ##(0/单词内容, 1/分类ID)
        'description':'shijiuda_', ## 任务描述
    }
}

resstart_url = 'http://' + host + ':' + port + '/RestartTask'
restart_task = {
    'action': 'RestartTask',
    'params': {
        'task_id':'573e332c-eeff-4f26-ad27-442e75d991ca', ## 任务ID
    }
}

stop_url = 'http://' + host + ':' + port + '/StopTask'
stop_task = {
    'action': 'StopTask',
    'params': {
        'task_id':'01_19shijiuda_4e6be3ea-e75c-4614-9b49-341a344ab2fa', ## 任务ID
    }
}


import urllib2, urllib
f = urllib2.urlopen(url =start_url, data = urllib.urlencode(start_task))
# f = urllib2.urlopen(url =resstart_url, data = urllib.urlencode(restart_task))
# f = urllib2.urlopen(url = stop_url, data = urllib.urlencode(stop_task))
print f.read()