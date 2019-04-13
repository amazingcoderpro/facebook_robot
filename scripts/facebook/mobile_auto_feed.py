#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from scripts.facebook.mobile_exception import FacebookException
from config import logger


def start_chrome(finger_print, headless=True):
    """
    :action: 启动浏览器
    :return:
    """
    try:
        # 定制浏览器启动项
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-gpu')

        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-popup-blocking')  # 禁止弹出拦截
        chrome_options.add_argument('--user-agent=iphone')
        chrome_options.add_argument("--ignore-certificate-errors")  # 忽略 Chrome 浏览器证书错误报警提示
        chrome_options.add_argument('lang=en_US')
        # 移动设备仿真
        mobile_emulation = {
            'deviceName': finger_print.get("device"),
            # "deviceMetrics": {"width": 600, "height":800, "pixelRatio": 4.0},
            # "userAgent": "Mozilla/5.0 (Linux; Android 8.0.0; XT1635-02 Build/OPNS27.76-12-22-9)"
        }
        chrome_options = Options()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        driver = webdriver.Chrome(chrome_options=chrome_options)
        # time.sleep(5)
        # driver.delete_all_cookies()
        # driver.get_screenshot_as_file("")
        return driver, ''
    except Exception as e:
        logger.error("The browser did not start successfully driver:{}".format(str(e)))
        return None, str(e)


def auto_login(driver, account, password, gender=1):
    """
    : 登录FB平台校验
    """
    # 登录FB
    # driver.delete_all_cookies()
    driver.get('https://www.facebook.com/')
    time.sleep(3)
    logger.info('auto_login:{},{}'.format(account, password))
    try:
        # FB登录
        email_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))
        email_box.send_keys(account)
        time.sleep(3)

        password_tabindex = driver.find_elements_by_css_selector('input[tabindex^="-"]')
        # 代表没有密码输入框
        if password_tabindex:
            login_btn = driver.find_element_by_css_selector('button[type="button"]')
            login_btn.send_keys(Keys.ENTER)
            time.sleep(2)

        password_box = driver.find_element_by_name("pass")
        password_box.send_keys(password)

        # login_ebutn = driver.find_element_by_css_selector('button[type="button"]')
        # login_ebutn.send_keys(Keys.ENTER)
        time.sleep(3)
        password_box.send_keys(Keys.ENTER)
        old_url = driver.current_url

        time.sleep(3)
        retry = 0
        while retry < 3:
            if driver.current_url == old_url:
                password_box.send_keys(Keys.ENTER)
                retry += 1
                time.sleep(2)
            else:
                break

        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="MComposer"]')))
        logger.info("login success！username={}, passwork={}".format(account, password))
        return True, 0
    except Exception as e:
        logger.exception('auto_login exception, e={}'.format(e))
        fb_exp = FacebookException(driver)
        return fb_exp.auto_process(4, wait=2, account=account, gender=gender)


def browse_page(driver, browse_times=10, distance=0, interval=3):
    """
    浏览页面
    :param driver: 浏览器驱动
    :param browse_times: 浏览次数
    :param distance: 每次间隔距离，默认为零，代表使用随机距离
    :param interval: 间隔时间， 单位秒
    :return:
    """
    # 浏览页面js
    try:
        logger.info('browse_page start.')
        y_dis = 0
        for i in range(browse_times):
            if distance > 0:
                y_dis += distance
            else:
                y_dis += random.randint(50, 500)

            driver.execute_script("window.scrollTo(0,{})".format(y_dis))
            time.sleep(interval)

        driver.execute_script("window.scrollTo(1800,0)")
        return True
    except Exception as e:
        logger.exception('browse_page exception. e={}'.format(e))
        fb_exp = FacebookException(driver)
        return fb_exp.auto_process(3)


def user_messages(driver):
    # 查看FB最新动态
    try:
        logger.info('user_messages start.')
        time.sleep(3)
        user_news = driver.find_element_by_css_selector('div[id="bookmarks_jewel"]')
        user_news.click()
        browse_page(driver)
        driver.find_element_by_css_selector('span[data-sigil="most_recent_bookmark"]').click()
        browse_page(driver)
        logger.info("View the latest news success driver={}".format(driver.name))
        return True, 0
    except:
        logger.exception('user_messages exception.')
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def local_surface(driver):
    # 浏览本地新闻
    try:
        logger.info('local_surface start.')
        user_news = driver.find_element_by_css_selector('div[id="bookmarks_jewel"]')
        user_news.click()
        browse_page(driver)
        driver.get("https://m.facebook.com/local_surface/?query_type=HOME&ref=bookmarks")
        browse_page(driver)
        logger.info("View the local news success driver={}".format(driver.name))
        return True, 0
    except:
        logger.exception('local_surface catch exception. start process..')
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def add_friends(driver, friends):
    #添加朋友
    try:
        for friend in friends:
            driver.get("https://m.facebook.com/search/people/?q={}&source=filter&isTrending=0".format(friend))
            time.sleep(3)

            # main-search-input

            add_search_fridens = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#u_1e_z > div > div')))
            add_search_fridens.click()
            add__fridens = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, 'a[data-sigil="touchable ajaxify"]')))
            add__fridens.click()
        return True, 0
    except:
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def send_messages(driver):
    #跟朋友聊天
    try:
        # 1.检查该账号是否存在好友
        # 2.向好友发送消息
        time.sleep(3)
        driver.get("https://m.facebook.com/search/people/?q={}&source=filter&isTrending=0".format("xiaoning"))
        time.sleep(1000)
        add_search_fridens = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#u_1e_z > div > div')))
        add_search_fridens.cliick()
        add__fridens = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, 'a[data-sigil="touchable ajaxify"]')))
        add__fridens.click()
        return True, 0
    except:
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def user_home(driver):
    #用户中心浏览
    try:
        time.sleep(3)
        driver.get("https://m.facebook.com/search/people/?q={}&source=filter&isTrending=0".format("xiaoning"))
        time.sleep(1000)
        add_search_fridens = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#u_1e_z > div > div')))
        add_search_fridens.cliick()
        add__fridens = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, 'a[data-sigil="touchable ajaxify"]')))
        add__fridens.click()
        return True, 0
    except:
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def post_status(driver):
    try:
        fb = FacebookException(driver)
        if 0 == fb.auto_check():
            pass

    except Exception as e:
        pass

if __name__ == '__main__':
    driver, msg = start_chrome({'device': 'iPhone 6'}, headless=False)
    auto_login(driver, 'michele53s@hotmail.com', 'v578jnd0jN1')
    # user_messages(driver)
    # local_surface(driver)
    add_friends(driver, ['lady gaga', 'kobe'])
    time.sleep(100)
    driver.quit()




