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
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="search_input"]')))
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
            logger.warning('auto_login exception, stat process..\r\ne={}'.format(e))
            return self.fb_exp.auto_process(4, wait=2)

    def browse_home(self):
        """
        首页内容浏览
        :return: Ture/False
        """
        try:
            logger.info('首页浏览功能: home_browsing start.')
            self.driver.get(self.start_url)
            self.sleep()
            self.browse_page()
            logger.info("首页浏览功能: home_browsing success")
            return True, 0
        except Exception as e:
            logger.exception('首页浏览功能: home_browsing error-->{}'.format(e))
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
            logger.info('增加好友功能: friends={}, limit={}'.format(search_keys, limit))
            result = {item: 0 for item in search_keys}
            for friend in search_keys:
                page_url = "https://www.facebook.com/search/people/?q={}&epa=SERP_TAB".format(friend)
                self.driver.get(page_url)

                # 判断是否进入了加好友页面
                search_inputs = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='FriendButton'")))

                # 找到新的好友列表
                self.browse_page(browse_times=5, distance=100, interval=5, back_top=True)
                new_friends = self.driver.find_elements_by_css_selector("button[aria-label='Add Friend'")
                new_friends = [item for item in new_friends if item.text == "Add Friend"]
                if not new_friends:
                    logger.warning('增加好友功能: can not find any friend. friend keyword={}'.format(friend))
                    continue

                # 组装要加的好友列表
                limit = limit if limit < len(new_friends) else len(new_friends)-1
                limit_friends = new_friends[:limit]

                # 循环加好友
                for idx in limit_friends:
                    self.click(idx, self.driver)
                    self.sleep()
                    try:
                        alert_ele = self.driver.find_element_by_link_text('Cancel')
                        if alert_ele:
                            self.click(alert_ele)
                            continue
                    except:
                        pass
                    time.sleep(3)
                    result[friend] += 1

            logger.info("增加好友功能: 增加结果为-->{}".format(result))
            self.driver.get(self.start_url)
            time.sleep(5)
            return True, 0
        except Exception as e:
            logger.error("增加好友功能: 出现异常，error-->{}".format(str(e)))
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
            self.sleep()

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

            already_chart_friends = []
            count = 0
            while count < friends:
                list_fridens = self.driver.find_elements_by_css_selector('div[class="fsl fwb fcb"]')
                # 已经聊过天的好友不再聊天
                filter_fridends = [item for item in list_fridens if item.text not in already_chart_friends]
                # 随机取一个好友聊天
                random.shuffle(filter_fridends)
                if not filter_fridends: break
                friend_instance = filter_fridends[0]
                already_chart_friends.append(friend_instance.text)

                # 进入某个好友页面
                self.click(friend_instance)
                self.sleep()

                # 打开聊天窗口
                try:
                    message_page = self.driver.find_element_by_css_selector('a[role="button"][href^="/messages/t"]')
                    self.click(message_page, self.driver)
                    self.sleep()
                except:
                    logger.info("好友聊天功能: 该好友不能聊天，重新选择好友")
                    self.driver.get(message_url)
                    self.sleep()
                    continue

                # 发送消息
                message_instance = None
                message_info = self.driver.find_elements_by_css_selector('div[role="presentation"] span div div div')
                for item in message_info:
                    try:
                        item.send_keys(contents[0])
                        self.sleep()
                        send_button = self.driver.find_element_by_css_selector('a[data-tooltip-content="Press Enter to send"]')
                        send_button.click()
                        message_instance = item
                        self.sleep()
                        break
                    except Exception as e:
                        pass

                if len(contents) == 1:
                    count += 1
                    self.driver.get(message_url)
                    continue

                for word in contents[1:]:
                    self.sleep()
                    message_instance.send_keys(word)
                    self.sleep()
                    send_button = self.driver.find_element_by_css_selector('a[data-tooltip-content="Press Enter to send"]')
                    send_button.click()
                    self.sleep()
                self.driver.get(message_url)
                count += 1

            self.driver.get(self.start_url)
            time.sleep(5)
            logger.info("好友聊天功能: send_messages succeed, limit={}, chat content={}".format(friends, contents))
            return True, 0
        except Exception as e:
            logger.exception('好友聊天功能: send_messages failed, friends={}, chat content={}'.format(friends, contents))
            return self.fb_exp.auto_process(3)

    def post_status(self, contents):
        """
        发送facebook状态
        :contents 发送的内容及图片, 字典形式{‘post’:'', 'img':[]}
        :images 图片的路径, list
        :return:
        """

        try:

            logger.info("发送状态功能: contents={},".format(contents, ))

            # 检查发送状态的页面存在
            send_state = WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'textarea')))
            if not send_state:
                logger.warning("发送状态功能: 没有进入到个人中心页面")
                return False, -1
            self.sleep()
            textarea = self.driver.find_element_by_css_selector('textarea')
            # self.send_keys(textarea, contents)
            self.sleep()
            textarea.send_keys(contents)
            self.sleep()
            # 选择share
            share_list = self.driver.find_elements_by_css_selector('button[type="submit"] span')
            for row in share_list:
                if row.text and row.text == "Share":
                    row.click()
                    self.sleep()
                    break
            self.driver.get(self.start_url)
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
            logger.info("用户中心浏览功能: browsing beginning")
            message_url = "https://www.facebook.com/profile.php"
            self.driver.get(message_url)

            user_lines = self.driver.find_elements_by_css_selector('div[id="fbTimelineHeadline"] li a')[1:4]
            random.shuffle(user_lines)
            for row in user_lines:
                self.click(row)
                self.browse_page()
                self.sleep()
            logger.info("用户中心浏览功能: browsing completed")
            return True, 0
        except Exception as e:
            logger.exception("用户中心浏览功能: browsing failed error-->{}".format(e))
            return self.fb_exp.auto_process(3)

    def browse_page(self, browse_times=0, distance=0, interval=0, back_top=True):
        """
        浏览页面
        :param driver: 浏览器驱动
        :param browse_times: 浏览次数
        :param distance: 每次间隔距离，默认为零，代表使用随机距离
        :param interval: 间隔时间， 单位秒, 默认为零，代表使用随机停顿时间
        :param back_top: 是否回到顶点
        :return:
        """
        # 浏览页面js
        try:
            logger.info('浏览页面功能: browse_page start.')
            y_dis = 0
            if browse_times <= 0:
                browse_times = random.randint(3, 15)

            for i in range(browse_times):
                if interval <= 0:
                    time.sleep(random.randint(1, 10))
                else:
                    time.sleep(interval)

                if distance > 0:
                    y_dis += distance
                else:
                    y_dis += random.randint(20, 200)

                self.driver.execute_script("window.scrollTo(0,{})".format(y_dis))

            if back_top:
                self.driver.execute_script("window.scrollTo(0,0)")
            return True
        except Exception as e:
            logger.exception('浏览页面功能: browse_page error={}'.format(e))
            return self.fb_exp.auto_process(3)


if __name__ == '__main__':
    filename = '../../resource/facebook_account.txt'
    with open(filename, 'r') as line:
        all_readline = line.readlines()
        for date in all_readline:
            str_info = date.split('---')
            user_account = str(str_info[0]).strip()
            user_password = str(str_info[1]).strip()

            # 初始化
            cookies=[{'domain': '.facebook.com', 'httpOnly': False, 'name': 'presence', 'path': '/', 'secure': True, 'value': 'EDvF3EtimeF1556521496EuserFA21B35381807782A2EstateFDt3F_5b_5dG556521496536CEchFDp_5f1B35381807782F2CC'}, {'domain': '.facebook.com', 'expiry': 1564297494.289986, 'httpOnly': True, 'name': 'fr', 'path': '/', 'secure': True, 'value': '14Cgytn5XS9ADvrMS.AWWAmG4Z8RUATBEoDXsVDoRqB1g.BcxqHO.Is.FzG.0.0.BcxqIW.AWVueXRy'}, {'domain': '.facebook.com', 'expiry': 1564297485.612012, 'httpOnly': True, 'name': 'xs', 'path': '/', 'secure': True, 'value': '31%3AzbNHAuA7vvOB-Q%3A2%3A1556521482%3A-1%3A-1'}, {'domain': '.facebook.com', 'expiry': 1557126281, 'httpOnly': False, 'name': 'dpr', 'path': '/', 'secure': True, 'value': '2'}, {'domain': '.facebook.com', 'expiry': 1619593469.742837, 'httpOnly': True, 'name': 'datr', 'path': '/', 'secure': True, 'value': 'zqHGXKNTrxN8ELHDhr2hXAEo'}, {'domain': '.facebook.com', 'expiry': 1564297485.611967, 'httpOnly': False, 'name': 'c_user', 'path': '/', 'secure': True, 'value': '100035381807782'}, {'domain': '.facebook.com', 'expiry': 1556611487.566037, 'httpOnly': True, 'name': 'spin', 'path': '/', 'secure': True, 'value': 'r.1000651590_b.trunk_t.1556521485_s.1_v.2_'}, {'domain': '.facebook.com', 'expiry': 1557126293, 'httpOnly': False, 'name': 'wd', 'path': '/', 'secure': True, 'value': '1200x754'}, {'domain': '.facebook.com', 'expiry': 1619593485.611922, 'httpOnly': True, 'name': 'sb', 'path': '/', 'secure': True, 'value': 'zqHGXDSVQ0-0sXJTMh0cHnju'}]
            fma = FacebookPCActions(account_info={"account": user_account, "password": user_password, "cookies": cookies}, finger_print={"user_agent": ""}, headless=False)
            if not fma.start_chrome():
                print("start chrome failed")
            fma.set_exception_processor(
                FacebookExceptionProcessor(fma.driver, env="pc", account=fma.account, gender=fma.gender))
            # 登陆
            res, status = fma.login()

            # 浏览页面
            # fma.browse_home()
            # 增加好友
            # fma.add_friends(["James","Jolin"], 2)
            # 发送状态

            fma.post_status("Today is a sun day!")

            #fma.post_status("Jesus conquered death, so that through him, we can conquer life. Happy Easter!")
            # 用户中心浏览
            # fma.browse_user_center()
            # 好友聊天
            # fma.chat(contents=["Hello", "Hi", "you good"], friends=2)

            #fma.chat(contents=["Hello", "Hi", "you good"], friends=2)

            #
            break


