#encoding:utf-8

import base64
import requests
import sys
import random
import time
import logging
from selenium import webdriver
from login_accounts import twitter_accounts
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

reload(sys)
sys.setdefaultencoding('utf8')
IDENTIFY = 1 ## 验证方式 1/看截图, 2/云打码
COOKIE_GETWAY = 1


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

        # remember_me = browser.find_element_by_name('remember_me')
        # remember_me.click()

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
    return get_cookie_from_twitter_com(accounts)

cookie = getCookie(twitter_accounts)
logging.info('Get Cookies Finish [%s]' % cookie)