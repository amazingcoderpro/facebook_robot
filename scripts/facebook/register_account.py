#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15


import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scripts.facebook.mobile_exception import FacebookException
from config import logger


def start_chrome(finger_print, headless=True):
    """
    启动 配置浏览器
    :param finger_print: 指定浏览器的devices
    :param headless: 是否指定浏览为无头浏览器
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

        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        logger.info('chrome options={}'.format(chrome_options.arguments))

        driver = webdriver.Chrome(chrome_options=chrome_options)
        time.sleep(1)
        driver.delete_all_cookies()
        # driver.get_screenshot_as_file("")
        return driver, ''
    except Exception as e:
        logger.error("The browser did not start successfully driver:{}".format(str(e)))
        return None, str(e)


def sign_up(driver, account, password, gender=1):
    """
     登录facebook平台
    :param driver:  浏览器驱动
    :param account: FB账号
    :param password: FB密码
    :param gender: 账号性别
    :return:
    """
    # 登录FB
    'https://m.facebook.com/reg/'
    driver.get('https://www.facebook.com/')
    try:
        # FB登录
        email_box = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.NAME, 'email')))
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
        # wrong_password = driver.find_elements_by_css_selector('a[href^="/recover/initiate/?ars=facebook_login_pw_error&lwv"]')
        while retry < 3:
            now_url = driver.current_url
            if now_url == old_url:
                password_box.send_keys(Keys.ENTER)
                time.sleep(2)
                wrong_password = driver.find_elements_by_css_selector(
                    'a[href^="/recover/initiate/?ars=facebook_login_pw_error&lwv"]')
                if wrong_password:
                    break
                retry += 1
            else:
                break

        # 检查是否在首页
        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="MComposer"]')))
        logger.info("login success！username={}, password={}".format(account, password))
        return True, 0
    except Exception as e:
        logger.error('auto_login exception, stat process..\r\ne={}'.format(e))
        fb_exp = FacebookException(driver)
        return fb_exp.auto_process(4, wait=2, account=account, gender=gender)


def email_login(driver:WebDriver, account, password):
    """
    126邮箱登录验证
    :param driver:
    :return:
    """
    url ="https://passport.126.com/ydzj/maildl?product=mail126&pdconf=yddl_mail126_conf&mc=146E1F&curl=https%3A%2F%2Fmail.126.com%2Fentry%2Fcgi%2Fntesdoor%3Ffrom%3Dsmart%26language%3D0%26style%3D11%26destip%3D192.168.202.48%26df%3Dsmart_ios"
    driver.get(url)
    emial_account = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="account"]')))
    emial_account.send_keys(account)
    email_password = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
    email_password.send_keys(password)

    login_email = WebDriverWait(driver, 6).until(
             EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
    login_email.send_keys(Keys.ENTER)

    # 处理弹框
    time.sleep(30)
    alter_info = WebDriverWait(driver, 6).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="msgbox-simpleText "]')))
    if alter_info:
        alter_button = driver.find_elements_by_css_selector('span[class="btn-inner"]')
        alter_button[2].click()
    handles = driver.window_handles
    print(handles)
    driver.switch_to_window(handles[0])  # 切换回原来页面

    search_button = driver.find_element_by_css_selector('div[class="toolbar-optItem "]')
    search_button.click()

    send_info = driver.find_element_by_css_selector('input[class="ipt-input"]')
    send_info.send_keys("facebook")
    send_info.send_keys(Keys.ENTER)



    pass


if __name__ == '__main__':
    driver, msg = start_chrome({'device': 'iPhone 6'}, headless=False)
    email_login(driver, "twobercancan", "13209334446")

