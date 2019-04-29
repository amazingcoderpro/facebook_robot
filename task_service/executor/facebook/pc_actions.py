#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import logger
from executor.facebook.base_actions import FacebookActions
from executor.facebook.exception import FacebookExceptionProcessor
from selenium.webdriver.common.keys import Keys


class FacebookPCActions(FacebookActions):
    """
    Facebook m站操作类
    """
    def __init__(self, account_info, finger_print,
                 headless=False, start_url="https://www.facebook.com/"):
        """
        初始化
        :param account_info: 账号相关的信息，如账号、密码、性别等，必须是字典类型
        :param finger_print: 指定浏览器指纹，包括devices/user-agent
        :param headless: 是否指定浏览为无头浏览器
        :param start_url: 启动的URL
        """
        super(FacebookPCActions, self).__init__(account_info, finger_print, headless, start_url)

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
            logger.exception("login by cookies failed. continue use password, account={}, e={}".format(self.account, e))
            self.driver.delete_all_cookies()

        try:
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
            self.sleep()

            # 检查是否在首页
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="search_input"]')))
            logger.info("login success！username={}, password={}".format(self.account, self.password))
            return True, 0
        except Exception as e:
            logger.exception("login by cookies failed. continue use password, account={}, e={}".format(self.account, e))

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
            logger.info('增加好友: friends={}, limit={}'.format(search_keys, limit))
            for friend in search_keys:
                page_url = "https://www.facebook.com/search/people/?q={}&epa=SERP_TAB".format(friend)
                self.driver.get(page_url)

                # 判断是否进入了加好友页面
                search_inputs = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='FriendButton'")))

                # 找到新的好友列表
                self.browse_home(self.driver, browse_times=5, distance=0, interval=5, back_top=True)
                new_friends = self.driver.find_elements_by_css_selector("button[aria-label='Add Friend'")
                if not new_friends:
                    logger.warning('增加好友: can not find any friend. friend keyword={}'.format(friend))
                    continue

                # 组装要加的好友列表
                limit = limit if limit < len(new_friends) else len(new_friends)-1
                limit_friends = new_friends[:limit]

                # 循环加好友
                for idx in limit_friends:
                    try:
                        dig_alert = self.driver.switch_to.alert
                        dig_alert.dismiss()
                    except Exception as e:
                        logger.info(str(e))
                        pass
                    finally:
                        self.click(idx, self.driver)
                        time.sleep(3)
            logger.info("增加好友: add friend succeed.")
            self.driver.get(self.start_url)
            time.sleep(5)
            return True, 0
        except Exception as e:
            logger.error("增加好友功能: 出现异常，开始异常检测-->{}".format(str(e)))
            return self.fb_exp.auto_process(3)

    def chat(self, contents=["How are you?"], friends=2):
        """
        跟好友聊天功能
        :param contents: 聊天内容, 列表
        :param friends: 一共跟多少好友聊
        :return:
        """
        try:

            # 打开好友界面
            logger.info('好友聊天功能: begning friends={}, chat content={}'.format(friends, contents))
            message_url = "https://www.facebook.com/profile.php?sk=friends"
            self.driver.get(message_url)
            time.sleep(5)

            # 检查是否进入好友列表页面
            fridens_page = WebDriverWait(self.driver, 4).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="pagelet_main_column_personal"]')))
            if not fridens_page:
                logger.error("好友聊天功能: 该账户未进入好友界面")
                return None

            # 找到该用户的好友
            list_fridens = self.driver.find_elements_by_css_selector('div[class="fsl fwb fcb"]')
            if not list_fridens:
                logger.error("好友聊天功能: 该账户没有好友")
                return None

            # 列表打乱顺序后重新组装好友列表
            random.shuffle(list_fridens)
            list_fridens = list_fridens[:friends] if friends < len(list_fridens) else len(list_fridens)

            # 进入好友界面，开启聊天
            for friend_instance in list_fridens:

                # 进入某个好友页面
                friend_instance.click()
                time.sleep(3)

                # 打开聊天窗口
                message_page = self.driver.find_element_by_css_selector('a[role="button"][href^="/messages/t"]')
                self.click(message_page,self.driver)
                time.sleep(3)

                # 定位聊天内容窗口最上层的div属性
                message_info = self.driver.find_elements_by_xpath('//div[@role="presentation"]')
                for item in message_info:
                    if item.text == 'Type a message...\n\nThumbs Up Sign':
                        message_instance = item
                if not message_instance:
                    break

                # 循环div，聊天，如果有异常证明当前的div不是聊天的div，如果是跳出循环
                div_list = message_instance.find_elements_by_css_selector('div')
                for div_instance in div_list:
                    try:
                        # div.send_keys(keywords)
                        self.send_keys(div_instance, contents[0])
                        msg_instance = div_instance
                        break
                    except Exception as e:
                        pass
                # 开始发送消息
                for word in contents:
                    self.send_keys(msg_instance, word)
                    send_button = message_instance.find_element_by_css_selector('a[label="send"]')
                    send_button.click()

            self.driver.get(self.start_url)
            time.sleep(5)
            logger.error("好友聊天功能: send_messages succeed, limit={}, chat content={}".format(friends, contents))
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
            logger.info("发送状态功能: sentence={},".format(contents,))
            message_url = "https://www.facebook.com/home.php?sk=h_chr&ref=bookmarks"
            self.driver.get(message_url)

            # 检查发送状态的页面存在
            send_state = WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="linkWrap noCount"]')))
            if not send_state:
                logger.warning("发送状态功能: 没有进入到个人中心页面")
                return False, -1

            # 查找输入框单击弹出消息框
            time.sleep(2)
            send_state_page = self.driver.find_element_by_css_selector('div[id="feedx_sprouts_container"]')
            self.click(send_state_page)
            # 输入需要发送的文本
            time.sleep(1)

            # 找到输入框的对象
            message_info = self.driver.find_elements_by_xpath('//div[@role="presentation"]')
            for item in message_info:
                if "What\'s on your mind" in item.text:
                    div_info = item.find_elements_by_css_selector('div')
                    for row in div_info:
                        try:
                            if "What's on your mind" in row.text:
                                try:
                                    self.send_keys(row,contents)
                                except Exception as e:
                                    continue
                                else:
                                    message_instance = row
                                    break
                        except:
                            continue
                    break

            time.sleep(1)
            submit = None
            for i in message_info:
                try:
                    submit = i.find_element_by_css_selector('button[type="submit"]')
                    break
                except:
                    continue
            time.sleep(2)
            self.click(submit)

            self.driver.get('https://www.facebook.com')
            time.sleep(5)
            return True, 0
        except Exception as e:
            logger.exception('send post failed, post={}'.format(contents))
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


# if __name__ == '__main__':
    # filename = '../../resource/facebook_account.txt'
    # with open(filename, 'r') as line:
    #     all_readline = line.readlines()
    #     for date in all_readline:
    #         str_info = date.split('---')
    #         user_account = str(str_info[0]).strip()
    #         user_password = str(str_info[1]).strip()
    #
    #         # 登陆
    #         fma = FacebookPCActions(account_info={"account": user_account, "password": user_password}, finger_print={"user_agent": ""}, headless=False)
    #         if not fma.start_chrome():
    #             print("start chrome failed")
    #         fma.set_exception_processor(
    #             FacebookExceptionProcessor(fma.driver, env="pc", account=fma.account, gender=fma.gender))
    #         # fma.set_exception_processor()
    #         res, status = fma.login()
    #         if not res:
    #             continue
    #         cookies = fma.get_cookies()
    #         print(cookies)
    #         fma.browse_user_center(3)
    #         time.sleep(100)

if __name__ == '__main__':
    user_account = str(17610069110)
    user_password = str("sanmang111..fb").strip()

    # 登陆
    fma = FacebookPCActions(account_info={"account": user_account, "password": user_password}, finger_print={"user_agent": ""}, headless=False)
    if not fma.start_chrome():
        print("start chrome failed")
    fma.set_exception_processor(
        FacebookExceptionProcessor(fma.driver, env="pc", account=fma.account, gender=fma.gender))
    res, status = fma.login()
