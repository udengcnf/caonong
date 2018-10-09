#encoding:utf-8

import base64
import requests
import sys
import json
import time
import logging
import random
from selenium import webdriver
from slide import slide
from login_accounts import sina_accounts
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

reload(sys)
sys.setdefaultencoding('utf8')
COOKIE_GETWAY = 1

def get_cookie_from_login_sina_com_cn(accounts):
    '''
        https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)
        获取一个账号的cookie
    '''

    loginURL = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
    rand_user = random.choice(accounts)
    account, password = rand_user['no'], rand_user['psw']
    username = base64.b64encode(account.encode('utf-8')).decode('utf-8')
    postData = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }

    session = requests.Session()
    r = session.post(loginURL, data=postData)
    jsonStr = r.content.decode('gbk')
    info = json.loads(jsonStr)

    if info['retcode'] == '0':
        logging.info('Get Cookie Success (Account[%s], Session[%s])' % (account, info))
        cookie = session.cookies.get_dict()
        return cookie
    else:
        logging.error('Get Cookie Failure (Account[%s], Reason[%s])' % (account, info['reason']))
        return {}


def get_cookie_from_weibo_cn(accounts):
    '''
        https://weibo.cn/login/
        获取一个账号的cookie
    '''
    try:
        loginURL = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/'
        # browser = webdriver.Chrome('D:\\work\\spider\\code\\highcloud\\highcloud\\chromedriver.exe')
        rand_user = random.choice(accounts)
        account, password = rand_user['no'], rand_user['psw']
        browser = webdriver.Chrome()
        browser.set_window_size(1050, 840)
        browser.get(loginURL)
        time.sleep(1)

        username = browser.find_element_by_id('loginName')
        username.clear()
        username.send_keys(account)

        psd = browser.find_element_by_id('loginPassword')
        psd.clear()
        psd.send_keys(password)

        commit = browser.find_element_by_id('loginAction')
        commit.click()
        time.sleep(3)

        if '我的首页' not in browser.title:
            ttype = slide.getType(browser)  # 识别图形路径
            print 'Result: %s!' % ttype
            slide.draw(browser, ttype)  # 滑动破解
            time.sleep(3)

        cookie = {}
        if '我的首页' in browser.title:
            for elem in browser.get_cookies():
                cookie[elem['name']] = elem['value']
            logging.info("Get Cookie Success!( Account:%s )" % account)
        return cookie
        # return json.dumps(cookie)
    except Exception as e:
        logging.error("Get Cookie Failed! Account[%s], Reason[%s]" % (account, str(sys.exc_info()[1])))
        return ''
    finally:
        try:
            browser.close()
        except Exception as e:
            pass

def getCookie(accounts):
    if COOKIE_GETWAY == 0:
        return get_cookie_from_login_sina_com_cn(accounts)
    elif COOKIE_GETWAY == 1:
        return get_cookie_from_weibo_cn(accounts)
    else:
        logging.error('getCookie error')

cookie = getCookie(sina_accounts)
logging.info('Get Cookies Finish [%s]' % cookie)