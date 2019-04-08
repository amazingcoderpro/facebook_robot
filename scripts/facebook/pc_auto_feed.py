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


def auto_feed_mobile(inputs):
    """
    养号任务实现
    :param account: Account类的实例，其中包含了账号相关的属性信息
    :param mode: 养号模式，0-代表自动模式，程序将会根据账号历史操作情况自动决定养号流程， 1-仅浏览 2-发状态 3-随机点赞 4-随机聊天
    :return: （code, result) code: 0-代表失败，1-代表成功， result： 处理结果描述
    """
    # 登录FB
    account_num = inputs['account']
    password = inputs['password']
    print('script runing:{},{}'.format(account_num, password))

    # 定制浏览器启动项
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--incognito") # 隐身模式
    # chrome_options.add_argument('lang=zh_CN.UTF-8')
    # chrome_options.add_argument('--headless')  # 设置为 headless 模式
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-popup-blocking')  # 禁止弹出拦截
    chrome_options.add_argument('--user-agent=iphone')
    chrome_options.add_argument("--ignore-certificate-errors")  # 忽略 Chrome 浏览器证书错误报警提示
    chrome_options.add_argument('lang=en_US')

    # 设置代理
    # PROXY = "47.52.42.24:8989"  # IP:PORT or HOST:PORT
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--proxy-server=http://%s' % PROXY)
    # chrome_options.add_argument("--disable-plugins-discovery")
    # chrome_options.add_argument("--start-maximized")

    # 移动设备仿真
    mobile_emulation = {
        'deviceName': 'iPhone 6',
        # "deviceMetrics": {"width": 600, "height":800, "pixelRatio": 4.0},
        # "userAgent": "Mozilla/5.0 (Linux; Android 8.0.0; XT1635-02 Build/OPNS27.76-12-22-9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36"
    }

    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.delete_all_cookies()
    driver.get('https://www.facebook.com/')
    driver.implicitly_wait(10)

    try:
        # FB登录
        email_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))
        email_box.send_keys(account_num)
        time.sleep(3)
        password_box = driver.find_element_by_name('pass')
        password_box.send_keys(password)
        # driver.get_screenshot_as_file('login.png')
        time.sleep(3)
        # login_img = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))
        # print(login_img)
        login_btn = driver.find_element_by_css_selector('button[type="button"]')
        print(login_btn)
        login_btn.click()
        # driver.implicitly_wait(10)
        time.sleep(2)

        # 检查页面是否存在
        fbexcept = FacebookException(driver)
        # fbexcept.check()
        # a = 1
        if not fbexcept.auto_process():
            return False
        # 检查是否在首页面
        try:
            WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="MComposer"]')))
        except:
            return False

        def browse_page():
            time.sleep(5)
            driver.execute_script("window.scrollTo(0,600)")
            time.sleep(4)
            driver.execute_script("window.scrollTo(0,1200)")
            time.sleep(3)
            driver.execute_script("window.scrollTo(1200,0)")
            time.sleep(3)
        # 首次登录页面取消弹窗
        # driver.switch_to_alert().accept()  # 接受警告（等于点了个确定）
        # message = driver.switch_to_alert().text
        # print(message)  # 得到弹窗的文本消息,比如得到：请输入用户名！'
        # driver.switch_to_alert().dismiss()  # 不接受警告（等于点了个取消）

        # 用户行为 查看最新动态
        time.sleep(3)
        user_news = driver.find_element_by_css_selector('div[id="bookmarks_jewel"]')
        user_news.click()
        browse_page()
        driver.find_element_by_css_selector('span[data-sigil="most_recent_bookmark"]').click()
        browse_page()

        time.sleep(3)
        user_news = driver.find_element_by_css_selector('div[id="bookmarks_jewel"]')
        user_news.click()
        browse_page()
        driver.get("https://m.facebook.com/local_surface/?query_type=HOME&ref=bookmarks")
        browse_page()

        # 搜索添加朋友
        time.sleep(3)
        driver.get("https://m.facebook.com/search/people/?q={}&source=filter&isTrending=0".format("xiaoning"))
        time.sleep(1000)

        add_search_fridens = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#u_1e_z > div > div')))
        add_search_fridens.cliick()
        add__fridens = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, 'a[data-sigil="touchable ajaxify"]')))
        add__fridens.click()


        # driver.get("https://m.facebook.com/home.php?soft=search")
        # add_search_fridens = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-sigil="search-small-box"]')))
        # add_search_fridens.send_keys("kkk")
        # time.sleep(3)
        # search_fridens = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-sigil="search-small-box"]')))
        # search_fridens.click()
        #
        # add_fridens = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="u_1v_10"]')))
        # add_fridens.click()

        # 添加好友
        # # driver.get('https://m.facebook.com/friends/center/requests/?mff_nav=1#!/friends/center/requests/?rfj&no_hist=1')
        # driver.find_element_by_css_selector('div[id="requests_jewel"]')
        # driver.implicitly_wait(10)
        # driver.find_element_by_css_selector('input[data-sigil="search-small-box"]').send_keys("mengxiaoning")
        # driver.implicitly_wait(10)

        # 账号被封杀标志
        # driver.implicitly_wait(10)
        # driver.find_element_by_css_selector('button[id="checkpointSubmitButton-actual-button"]')

        # add_friends = driver.find_element_by_css_selector('a[data-sigil^="friends-center-nav-item"]')
        # add_friends.click()
        # driver.implicitly_wait(10)
        # time.sleep(5)

    except Exception:
        driver.delete_all_cookies()
        driver.quit()
        # 登录账号记住密码
        # no_password = driver.find_element_by_css_selector('button[type="submit"]')
        # driver.implicitly_wait(10)
        # if no_password:
        #     pass
        #     # continue
        # else:
        #     print("没有找到记住账号密码的节点")

        # def capath_intercepty():
        #     driver.get_screenshot_as_file('screenshot.png')
        #     # 获取验证码位置
        #     element = driver.find_element_by_css_selector('#captcha > img')
        #     left = int(element.location['x'])
        #     top = int(element.location['y'])
        #     right = int(element.location['x'] + element.size['width'])
        #     bottom = int(element.location['y'] + element.size['height'])
        #
        #     # 通过Image处理验证码图像
        #     im = Image.open('screenshot.png')
        #     im = im.crop((left, top, right, bottom))
        #     im.save('code.png')
        #
        # def never_save_password():
        #     # 登录之后选择不保存密码
        #     no_password = driver.find_element_by_css_selector('a[name="login"]')
        #     no_password.click()


if __name__ == '__main__':
    auto_feed_mobile(inputs={'account': "bijupgnair@hotmail.com", 'password': "nandhu19"})