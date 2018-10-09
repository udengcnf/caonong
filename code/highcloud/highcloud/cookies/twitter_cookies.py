#encoding:utf-8

import sys
import random
import time
import logging
from scrapy import Item, Field
from selenium import webdriver
from highcloud.utils.login_accounts import twitter_accounts
from highcloud.utils.utils_redis import RedisUtils

reload(sys)
sys.setdefaultencoding('utf8')

class TwitterCookie(Item):
    '''
        账号cookie
    '''

    id = Field() ## 账户名
    cookie = Field() ## cookie

def get_cookie_from_twitter_com(accounts):
    '''
        https://weibo.cn/login/
        获取一个账号的cookie
    '''
    try:
        cookie = {}
        loginURL = 'https://twitter.com/login'

        rand_user = random.choice(accounts)
        account, psw, phone = rand_user['no'], rand_user['psw'], rand_user['phone']
        browser = webdriver.Chrome()

        # browser.set_window_size(1050, 840)
        browser.get(loginURL)
        time.sleep(1)

        username = browser.find_element_by_css_selector('.js-username-field.email-input.js-initial-focus')
        username.clear()
        username.send_keys(account)

        password = browser.find_element_by_css_selector('.js-password-field')
        password.clear()
        password.send_keys(psw)

        login = browser.find_element_by_css_selector('.submit.EdgeButton.EdgeButton--primary.EdgeButtom--medium')
        login.click()
        time.sleep(1)

        if '验证' in browser.title:
            ## 验证手机号
            phone_input = browser.find_element_by_css_selector('.Form-textbox')
            phone_input.clear()
            phone_input.send_keys(phone)

            login = browser.find_element_by_id('email_challenge_submit')
            login.click()
            time.sleep(3)
        ## 获取cookie
        for elem in browser.get_cookies():
            cookie[elem['name']] = elem['value']
        logging.info("Get Cookie success! Account[%s], [%s]!" % (account, cookie))

    except Exception as e:
        logging.error("Get Cookie Failed! Account[%s], Reason[%s]" % (account, str(sys.exc_info()[1])))
    finally:
        try:
            browser.close()
        except Exception as e:
            pass
        finally:
            return cookie

def getCookie(accounts):
    '''
        获取账号的cookie并入库
    '''
    try:
        rand_user = random.choice(accounts)
        item = TwitterCookie()
        item['id'] = rand_user['no']
        res = RedisUtils.item_query(item)
        if res == {}:
            return get_cookie_from_twitter_com(accounts)
        else:
            return res['cookie']
    except Exception as e:
        logging.error("initCookie Failed! %s" %  str(sys.exc_info()[1]))
    finally:
        pass

def initCookie(accounts):
    '''
        获取账号的cookie并入库
    '''
    try:
        for a in accounts:
            c = get_cookie_from_twitter_com([a])
            if c != {}:
                item = TwitterCookie()
                item['id'] = a['no']
                item['cookie'] = c
                RedisUtils.item_insert(item)
            time.sleep(2)
    except Exception as e:
        logging.error("initCookie Failed! %s" %  str(sys.exc_info()[1]))
    finally:
        pass

if __name__ == '__main__':
    initCookie(twitter_accounts)
else:
    cookie = None
    # cookie = getCookie(twitter_accounts)
    logging.info('Get Cookies Finish [%s]' % cookie)