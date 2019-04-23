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
from scripts.utils import super_click


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


def auto_login(driver, account, password, gender=1):
    """
     登录facebook平台
    :param driver:  浏览器驱动
    :param account: FB账号
    :param password: FB密码
    :param gender: 账号性别
    :return:
    """
    # 登录FB
    # driver.delete_all_cookies()
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


def browse_page(driver, browse_times=10, distance=0, interval=0, return_top=True):
    """
    浏览页面
    :param driver: 浏览器驱动
    :param browse_times: 浏览次数
    :param distance: 每次间隔距离，默认为零，代表使用随机距离
    :param interval: 间隔时间， 单位秒, 默认为零，代表使用随机停顿时间
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
            if interval <= 0:
                time.sleep(random.randint(2, 10))
            else:
                time.sleep(interval)
        if return_top:
            driver.execute_script("window.scrollTo(0,0)")

        return True
    except Exception as e:
        logger.exception('browse_page exception. e={}'.format(e))
        fb_exp = FacebookException(driver)
        return fb_exp.auto_process(3)


def user_messages(driver):
    """
    查看FB最新动态
    :param driver: 浏览器驱动
    :return:
    """
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
    """
    浏览本地新闻
    :param driver:
    :return: 浏览器驱动
    """
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
        logger.error('local_surface catch exception. start process..')
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def add_friends(driver:WebDriver, search_keys, limit=2):
    """
    添加朋友
    :param driver: 浏览器驱动
    :param search_keys: 搜索关键字集合.list
    :param limit: 每个关键字添加好好的个数上限
    :return:
    """
    try:
        limit = 1 if limit <= 0 else limit
        logger.info('start add friends, friends={}, limit={}'.format(search_keys, limit))
        for friend in search_keys:
            page_url = "https://m.facebook.com/search/people/?q={}&source=filter&isTrending=0".format(friend)
            driver.get(page_url)

            # 判断是否进入了加好友页面
            search_inputs = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='main-search-input'")))

            # 找到所有相关人员图像元素
            new_friends_avatar = driver.find_elements_by_css_selector("img[src^='https://scontent'")
            if not new_friends_avatar:
                logger.warning('can not find any friend avatar. friend keyword={}'.format(friend))
                continue

            i = 1
            add_friends_index = [0]
            limit = limit if limit < len(new_friends_avatar) else len(new_friends_avatar)-1
            while i < limit:
                idx = random.randint(1, 1000) % len(new_friends_avatar)
                if idx == 0:
                    continue
                add_friends_index.append(idx)
                i += 1

            for idx in add_friends_index:
                if not new_friends_avatar or idx >= len(new_friends_avatar):
                    continue

                # 点击对应好友的图像，进入其profile页面
                super_click(new_friends_avatar[idx], driver)
                time.sleep(3)

                if 'id=' not in driver.current_url:
                    continue

                profile_id = driver.current_url.split("id=")[1]
                # 获取添加好友或者点赞的按钮
                # add_btn = driver.find_element_by_css_selector("a[href^='/a/mobile/friends/'")
                # add_btn_1 = driver.find_element_by_css_selector("a[href*='{}'".format(profile_id))
                add_btn = driver.find_element_by_css_selector("div[data-store*='{}'".format(profile_id))
                if not add_btn:
                    add_btn = driver.find_element_by_css_selector("a[href^='https://static.xx'")
                    if not add_btn:
                        driver.back()
                        continue

                super_click(add_btn, driver)
                logger.info('add friend succeed, key word={}, new friend id={}'.format(friend, profile_id))
                time.sleep(2)
                # 回到好友列表页面，继续添加好友
                if driver.current_url != page_url:
                    driver.back()
                    time.sleep(3)
                new_friends_avatar = driver.find_elements_by_css_selector("img[src^='https://scontent'")
        driver.get('https://m.facebook.com')
        return True, 0
    except Exception as e:
        logger.error('add friends failed, page url={}, e={}'.format(page_url, e))
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def send_messages(driver:WebDriver, keywords, limit=2):
    """
    跟好友聊天功能
    :param driver:
    :param keywords: ；聊天内容
    :param limit: 一共跟好友聊多少条
    :return:
    """
    try:
        # 1.检查该账号是否存在好友
        # 2.向好友发送消息
        for i in range(1, limit + 1):
            message_url = "https://m.facebook.com/friends/center/friends"
            driver.get(message_url)

            # 检查是否进入好友列表页面
            fridens_page = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="friends_center_main"]')))
            if fridens_page:
                logger.info('enter friends list page.')
                # 查找所有相关好友的属性
                list_fridens = driver.find_elements_by_css_selector('i[class="img profpic"]')
                if not list_fridens:
                    logger.warning('can not find any friend')
                    continue

                idx_friends = random.randint(0, len(list_fridens)-1)
                list_fridens[idx_friends].click()
                # 打开聊天 注意：这里内容加载较慢需要时间等待
                time.sleep(3)
                message_page = driver.find_elements_by_css_selector("span[data-sigil='m-profile-action-button-label']")[2]
                super_click(message_page, driver)
                time.sleep(3)
                # 出现下载Messenager 选择关闭
                try:
                    install_messenger = driver.find_element_by_css_selector('div[data-sigil="m-promo-interstitial"]')
                    if install_messenger:
                        close_btn = driver.find_element_by_css_selector('img[data-nt^="NT:IMAGE"]')
                        super_click(close_btn, driver)
                except:
                    pass

                logger.info('start chat.')
                for keys in keywords:
                    # 输入聊天内容
                    browse_page(driver, 3)
                    time.sleep(1)
                    message_info = driver.find_element_by_css_selector('textarea[data-sigil^="m-textarea-input"]')
                    message_info.send_keys(keys)
                    time.sleep(2)

                    # 发送聊天内容
                    send_info = driver.find_element_by_css_selector('button[name$="end"]')

                    super_click(send_info, driver, double=True)
                    time.sleep(3)

                    try:
                        install_messenger = driver.find_element_by_css_selector(
                            'div[data-sigil="m-promo-interstitial"]')
                        if install_messenger:
                            close_btn = driver.find_element_by_css_selector('img[data-nt^="NT:IMAGE"]')
                            super_click(close_btn, driver)
                    except Exception as e:
                        pass

            return True, 0
    except Exception as e:
        print(e)
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def send_facebook_state(driver:WebDriver, keywords):
    """
    发送facebook状态
    :param driver:
    :keyword 发送的内容
    :return:
    """
    try:
        # 1.检查该账号是否存在好友
        # 2.向好友发送消息
        message_url = "https://m.facebook.com/home.php?sk=h_chr&ref=bookmarks"
        driver.get(message_url)
        # 检查发送状态的页面存在
        send_state = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[id="MComposer"]')))
        if not send_state:
            logger.warning('can not find send state page')
        # 查找输入框
        time.sleep(6)
        send_state_page = driver.find_element_by_css_selector('div[role="textbox"]')
        send_state_page.click()
        # 输入需要发送的文本
        time.sleep(10)
        send_info_state = driver.find_element_by_css_selector('textarea[class="composerInput mentions-input"]')
        print(send_info_state)
        send_info_state.send_keys("HELLO WORLD")
        time.sleep(10)
        release_state_button = driver.find_element_by_css_selector('button[data-sigil="touchable submit_composer"]')
        release_state_button.click()
        return True, 0
    except:
        fbexcept = FacebookException(driver)
        return fbexcept.auto_process(3)


def user_home(driver):
    """
    # 用户中心浏览
    :param driver:
    :return:
    """
    try:
        driver.get("https://m.facebook.com/bertoualocal.miners?ref=bookmarks")
        browse_page(driver)
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
    filename = 'accont_info.txt'
    with open(filename, 'r') as line:
        all_readline = line.readlines()
        for date in all_readline:
            str_info = date.split()
            user_account = str(str_info[0])
            user_password = str(str_info[1])
            driver, msg = start_chrome({'device': 'iPhone 6'}, headless=False)
            res, statu = auto_login(driver, user_account, user_password)
            if not res:
                continue
            # add_friends(driver, ["xiaoning"], 2)
            # send_facebook_state(driver, "xiaoning")
            send_messages(driver, ["hello?", "how are you!"], 2)
            # send_messages(driver)
            # user_messages(driver)
            # local_surface(driver)
            time.sleep(6)
            # driver.quit()






