#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from scripts.facebook.mobile_exception import FacebookException
from config import logger


def start_chrom(finger_print):
    """
    :action: 启动浏览器
    :return:
    """
    try:
        # 定制浏览器启动项
        chrome_options = webdriver.ChromeOptions()
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
        return driver
    except Exception as e:
        logger.error("The browser did not start successfully driver:{}".format(str(e)))
        return None


def auto_login(driver, account, password):
    """
    : 登录FB平台校验
    """
    # 登录FB
    # driver.delete_all_cookies()
    driver.get('https://www.facebook.com/')
    time.sleep(3)
    # account = inputs['account']
    # password = inputs['password']
    logger.info('script runing:{},{}'.format(account, password))
    try:
        # FB登录
        email_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))
        email_box.send_keys(account)
        time.sleep(3)
        password_box = driver.find_element_by_name("pass")
        password_tabindex = driver.find_elements_by_css_selector('input[tabindex^="-"]')
        if password_tabindex:
            login_btn = driver.find_element_by_css_selector('button[type="button"]')
            login_btn.click()
            time.sleep(2)
            old_url = driver.current_url
            password_box = driver.find_element_by_name("pass")
            password_box.send_keys(password)
            login_sbtu = driver.find_element_by_css_selector('button[data-sigil="touchable m_login_button"]')
            time.sleep(3)
            login_sbtu.click()
            print("第二次点击完成"+"#"*60)
            retry = 0
            while retry < 3:
                if driver.current_url == old_url:
                    login_btn.click()
                    retry += 1
                    time.sleep(1)
                else:
                    break
            return True, 0
        password_box.send_keys(password)
        # driver.get_screenshot_as_file('login.png')
        time.sleep(3)
        # login_img = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))
        # print(login_img)
        login_btn = driver.find_element_by_css_selector('button[type="button"]')
        print(login_btn)
        old_url = driver.current_url
        ret = login_btn.click()
        print("error click" + "#" * 60)
        # driver.implicitly_wait(10)
        retry = 0
        while retry < 3:
            time.sleep(1)
            if driver.current_url == old_url:
                login_btn.click()
                retry += 1
            else:
                break
        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="MComposer"]')))
        logger.info("login success！username={}, passwork={}".format(account, password))
        return True, 0
    except Exception as e:
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(2)

        # driver.find_element_by_css_selector('button[id="checkpointSubmitButton-actual-button"]')
        # time.sleep(5)
        # print("该账号已经被限制访问, 更改数据内容")
        # driver.delete_all_cookies()
        # driver.quit()
        # return False


def browse_page_js(driver):
    # 浏览页面js
    try:
        time.sleep(5)
        driver.execute_script("window.scrollTo(0,600)")
        time.sleep(4)
        driver.execute_script("window.scrollTo(0,1200)")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0,1800)")
        time.sleep(3)
        driver.execute_script("window.scrollTo(1800,0)")
        time.sleep(3)
        return True
    except Exception as E:
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def user_messages(driver):
    # 查看FB最新动态
    try:
        time.sleep(3)
        user_news = driver.find_element_by_css_selector('div[id="bookmarks_jewel"]')
        user_news.click()
        browse_page_js()
        driver.find_element_by_css_selector('span[data-sigil="most_recent_bookmark"]').click()
        browse_page_js()
        logger.info("View the latest news success driver={}".format(driver.name))
        return True, 0
    except:
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def local_surface(driver):
    # 浏览本地新闻
    try:
        time.sleep(3)
        user_news = driver.find_element_by_css_selector('div[id="bookmarks_jewel"]')
        user_news.click()
        browse_page_js()
        driver.get("https://m.facebook.com/local_surface/?query_type=HOME&ref=bookmarks")
        browse_page_js()
        logger.info("View the local news success driver={}".format(driver.name))
        return True
    except:
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def add_friends(driver):
    #添加朋友
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
        return True
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
        return True
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
        return True
    except:
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


if __name__ == '__main__':
    driver = start_chrom({'device': 'iPhone 6'})
    auto_login(driver, 'jonemarnug@hotmail.com', 'OA2TMcj8Fx')



