#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15


import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import logger
from executor.facebook.base_actions import FacebookActions
from executor.facebook.exception import FacebookExceptionProcessor


class FacebookMobileActions(FacebookActions):
    """
    Facebook m站操作类
    """
    def __init__(self, account_info, finger_print,
                 headless=False, start_url="https://m.facebook.com/"):
        """
        初始化
        :param account_info: 账号相关的信息，如账号、密码、性别等，必须是字典类型
        :param finger_print: 指定浏览器指纹，包括devices/user-agent
        :param headless: 是否指定浏览为无头浏览器
        :param start_url: 启动的URL
        """
        super(FacebookMobileActions, self).__init__(account_info, finger_print, headless, start_url)

    def login(self):
        """
         登录facebook平台
        :return:
        """
        # 登录FB
        assert self.driver, "Driver is not valid! Please invoke start_chrome before login!"
        self.driver.get(self.start_url)
        self.sleep()
        try:
            # 先用cookies登录
            if self.cookies:
                logger.info("login by cookies start！ account={}".format(self.account))
                for item in self.cookies:
                    self.driver.add_cookie(item)

                self.driver.get(self.start_url)

                WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="MComposer"]')))
                logger.info("login success by cookies！ account={}".format(self.account))
                return True, 0
        except Exception as e:
            logger.exception("login failed by cookies! continue use password, account={}, e={}".format(self.account, e))
            self.driver.delete_all_cookies()

        try:
            self.driver.get(self.start_url)
            # FB登录
            email_box = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.NAME, 'email')))
            # email_box.send_keys(account)
            self.send_keys(email_box, self.account)
            self.sleep()

            password_tabindex = self.driver.find_elements_by_css_selector('input[tabindex^="-"]')
            # 代表没有密码输入框
            if password_tabindex:
                login_btn = self.driver.find_element_by_css_selector('button[type="button"]')
                login_btn.send_keys(Keys.ENTER)
                self.sleep()

            password_box = self.driver.find_element_by_name("pass")
            # password_box.send_keys(password)
            self.send_keys(password_box, self.password)

            self.sleep()
            password_box.send_keys(Keys.ENTER)
            old_url = self.driver.current_url
            self.sleep()
            retry = 0
            # wrong_password = driver.find_elements_by_css_selector('a[href^="/recover/initiate/?ars=facebook_login_pw_error&lwv"]')
            while retry < 3:
                now_url = self.driver.current_url
                if now_url == old_url:
                    password_box.send_keys(Keys.ENTER)
                    self.sleep()
                    wrong_password = self.driver.find_elements_by_css_selector(
                        'a[href^="/recover/initiate/?ars=facebook_login_pw_error&lwv"]')
                    if wrong_password:
                        break
                    retry += 1
                else:
                    break

            # 检查是否在首页
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="MComposer"]')))
            logger.info("login success！username={}, password={}".format(self.account, self.password))
            return True, 0
        except Exception as e:
            logger.warning('auto_login exception, stat process..\r\ne={}'.format(e))
            return self.fb_exp.auto_process(4, wait=2)

    def browse_home(self):
        """
        首页内容浏览
        :return: Ture/False
        """
        try:
            logger.info('home_browsing start.')
            self.driver.get(self.start_url)
            self.sleep()
            self.browse_page()
            logger.info("home_browsing success")
            return True, 0
        except Exception as e:
            logger.exception('home_browsing exception.e={}'.format(e))
            return self.fb_exp.auto_process(3)

    def add_friends(self, search_keys, limit=2):
        """
        添加朋友
        :param search_keys: 搜索关键字集合.list
        :param limit: 每个关键字添加好好的个数上限
        :return:
        """
        try:
            limit = 1 if limit <= 0 else limit
            logger.info('start add friends, friends={}, limit={}'.format(search_keys, limit))
            for friend in search_keys:
                page_url = "https://m.facebook.com/search/people/?q={}&source=filter&isTrending=0".format(friend)
                self.driver.get(page_url)

                # 判断是否进入了加好友页面
                search_inputs = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='main-search-input'")))

                # 找到所有相关人员图像元素
                new_friends_avatar = self.driver.find_elements_by_css_selector("img[src^='https://scontent'")
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
                    self.click(new_friends_avatar[idx])
                    self.sleep()

                    if 'id=' not in self.driver.current_url:
                        continue

                    profile_id = self.driver.current_url.split("id=")[1]
                    # 获取添加好友或者点赞的按钮
                    # add_btn = driver.find_element_by_css_selector("a[href^='/a/mobile/friends/'")
                    # add_btn_1 = driver.find_element_by_css_selector("a[href*='{}'".format(profile_id))
                    add_btn = self.driver.find_element_by_css_selector("div[data-store*='{}'".format(profile_id))
                    if not add_btn:
                        add_btn = self.driver.find_element_by_css_selector("a[href^='https://static.xx'")
                        if not add_btn:
                            self.driver.back()
                            continue

                    self.click(add_btn)
                    logger.info('add friend succeed, key word={}, new friend id={}'.format(friend, profile_id))
                    self.sleep()
                    # 回到好友列表页面，继续添加好友
                    if self.driver.current_url != page_url:
                        self.driver.back()
                        self.sleep()
                    new_friends_avatar = self.driver.find_elements_by_css_selector("img[src^='https://scontent'")
            logger.info("add friend succeed.")
            self.driver.get(self.start_url)
            self.sleep(3, 6)
            return True, 0
        except Exception as e:
            logger.error('add friends failed, page url={}, e={}'.format(page_url, e))
            return self.fb_exp.auto_process(3)

    def chat(self, contents=["How are you?"], friends=2):
        """
        跟好友聊天功能
        :param contents: 聊天内容, 列表
        :param friends: 一共跟多少好友聊
        :return:
        """
        try:
            # 1.检查该账号是否存在好友
            # 2.向好友发送消息
            logger.info('start send_messages, friends={}, chat content={}'.format(friends, contents))
            for i in range(1, friends + 1):
                message_url = "https://m.facebook.com/friends/center/friends"
                self.driver.get(message_url)

                # 检查是否进入好友列表页面
                fridens_page = WebDriverWait(self.driver, 4).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="friends_center_main"]')))
                if fridens_page:
                    logger.info('enter friends list page.')
                    # 查找所有相关好友的属性
                    list_fridens = self.driver.find_elements_by_css_selector('i[class="img profpic"]')
                    if not list_fridens:
                        logger.warning('can not find any friend')
                        continue

                    idx_friends = random.randint(0, len(list_fridens)-1)
                    list_fridens[idx_friends].click()
                    # 打开聊天 注意：这里内容加载较慢需要时间等待
                    self.sleep()
                    message_page = self.driver.find_elements_by_css_selector("span[data-sigil='m-profile-action-button-label']")[2]
                    self.click(message_page)
                    self.sleep()
                    # 出现下载Messenager 选择关闭
                    try:
                        install_messenger = self.driver.find_element_by_css_selector('div[data-sigil="m-promo-interstitial"]')
                        if install_messenger:
                            close_btn = self.driver.find_element_by_css_selector('img[data-nt^="NT:IMAGE"]')
                            self.click(close_btn)
                    except:
                        pass

                    logger.info('start chat.')
                    for keys in contents:
                        # 输入聊天内容
                        self.browse_page(3, distance=50, interval=2, back_top=False)
                        self.sleep()
                        message_info = self.driver.find_element_by_css_selector('textarea[data-sigil^="m-textarea-input"]')
                        # message_info.send_keys(keys)
                        self.send_keys(message_info, keys)
                        self.sleep()

                        # 发送聊天内容
                        send_info = self.driver.find_element_by_css_selector('button[name$="end"]')

                        self.click(send_info, double=True)
                        self.sleep()

                        try:
                            install_messenger = self.driver.find_element_by_css_selector(
                                'div[data-sigil="m-promo-interstitial"]')
                            if install_messenger:
                                close_btn = self.driver.find_element_by_css_selector('img[data-nt^="NT:IMAGE"]')
                                self.click(close_btn)
                        except Exception as e:
                            pass

            self.driver.get(self.start_url)
            self.sleep()
            logger.info('send_messages succeed, friends={}, chat content={}'.format(friends, contents))
            return True, 0
        except Exception as e:
            logger.exception('send_messages failed, friends={}, chat content={}'.format(friends, contents))
            return self.fb_exp.auto_process(3)

    def post_status(self, contents):
        """
        发送facebook状态
        :contents 发送的内容及图片, 字典形式{‘post’:'', 'img':[]}
        :images 图片的路径, list
        :return:
        """
        try:
            # 1.检查该账号是否存在好友
            # 2.向好友发送消息
            logger.info("start posts, keywords={}".format(contents))
            message_url = "https://m.facebook.com/home.php?sk=h_chr&ref=bookmarks"
            self.driver.get(message_url)
            # 检查发送状态的页面存在
            send_state = WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[id="MComposer"]')))
            if not send_state:
                logger.warning('can not find send state page')
                return False, -1

            # 查找输入框
            self.sleep(4, 6)
            send_state_page = self.driver.find_element_by_css_selector('div[role="textbox"]')
            send_state_page.click()
            # 输入需要发送的文本
            self.sleep(6, 10)
            send_info_state = self.driver.find_element_by_css_selector('textarea[class="composerInput mentions-input"]')

            post_content = contents.get('post')
            # send_info_state.send_keys(post_content)
            self.send_keys(send_info_state, post_content)
            self.sleep(6, 10)
            release_state_button = self.driver.find_element_by_css_selector('button[data-sigil="touchable submit_composer"]')
            self.click(release_state_button)
            logger.info('send post success, post={}'.format(post_content))
            self.driver.get(self.start_url)
            self.sleep(4, 8)
            return True, 0
        except:
            logger.exception('send post failed, post={}'.format(post_content))
            return self.fb_exp.auto_process(3)

    def browse_user_center(self, limit=3):
        """
        # 用户中心浏览
        :param limit: 浏览的项目数
        :return:
        """
        try:
            logger.info("user_home start, limit={}".format(limit))
            self.driver.get(self.start_url)
            # browse_page(driver)
            user_news = self.driver.find_element_by_css_selector('div[id="bookmarks_jewel"]')
            self.click(user_news)

            self.sleep(3, 6)
            self.browse_page(browse_times=random.randint(1, 3))
            # 个人中心全部的菜单栏
            user_list = self.driver.find_elements_by_css_selector('div[data-sigil="touchable"]')
            list_rang = range(len(user_list))
            # 随机浏览limit个个人中心页面
            slice = random.sample(list_rang, limit)
            for i in slice:
                user_list = self.driver.find_elements_by_css_selector('div[data-sigil="touchable"]')
                # user_list[i].click()
                self.click(user_list[i])
                self.browse_page(browse_times=random.randint(3, 5))
                self.driver.back()
                self.browse_page(browse_times=random.randint(1, 3))
                user_news = self.driver.find_element_by_css_selector('div[id="bookmarks_jewel"]')
                self.click(user_news)
                self.browse_page(browse_times=random.randint(3, 5))
            logger.info("user_home browsing completed")
            return True, 0
        except Exception as e:
            logger.exception("user_home browsing failed  error ={}".format(e))
            return self.fb_exp.auto_process(3)


if __name__ == '__main__':
    filename = '../../resource/facebook_account.txt'

    with open(filename, 'r') as line:
        all_readline = line.readlines()
        for date in all_readline:
            str_info = date.split('---')
            user_account = str(str_info[0]).strip()
            user_password = str(str_info[1]).strip()
            fma = FacebookMobileActions(account_info={"account": user_account, "password": user_password}, finger_print={"device":"iPhone 6"}, headless=False)
            if not fma.start_chrome():
                print("start chrome failed")

            fma.set_exception_processor(FacebookExceptionProcessor(fma.driver, env="mobile", account=fma.account, gender=fma.gender))

            res, status = fma.login()
            # if not res:
            #     continue
            cookies = fma.get_cookies()
            print(cookies)
            fma.browse_user_center(3)
            time.sleep(100)







