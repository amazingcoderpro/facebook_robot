#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-04-27
# Function: 
from executor.facebook.exception import FacebookExceptionProcessor
from config import logger
from executor.web_actions import WebActions


class FacebookActions(WebActions):
    """
    Facebook 各种操作的基类, 封装通用的操作函数
    """
    def __init__(self, account_info, finger_print={},
                 headless=False, start_url="https://www.facebook.com/"):
        """
        初始化
        :param account_info: 账号相关的信息，如账号、密码、性别等，必须是字典类型
        :param finger_print: 指定浏览器指纹，包括devices/user-agent
        :param headless: 是否指定浏览为无头浏览器
        :param start_url: 启动的URL
        """
        assert isinstance(account_info, dict), "账号信息必须是字典类型"
        assert isinstance(finger_print, dict), "浏览器指纹"

        self.account = account_info.get("account", "")
        self.password = account_info.get("password", "")
        self.gender = account_info.get("gender", 1)
        self.phone_number = account_info.get("phone_number", "")
        self.cookies = account_info.get("cookies", "")
        self.start_url = start_url
        self.fb_exp = None
        super(FacebookActions, self).__init__(finger_print=finger_print, headless=headless)
        logger.info("FacebookActions init, account_info={}, device={}, user_agent={}, headless={}, "
                    "start_url={}".format(account_info, self.device, self.user_agent, headless, start_url))

    def start_chrome(self):
        if super(FacebookActions, self).start_chrome():
            self.fb_exp = FacebookExceptionProcessor(self.driver, env="mobile", account=self.account, gender=self.gender)
            return True
        else:
            return False

    def login(self):
        raise NotImplementedError("login must be implemented!")

    def browse_home(self):
        raise NotImplementedError("browse_home must be implemented!")

    def add_friends(self, search_keys, limit=2):
        raise NotImplementedError("add_friends must be implemented!")

    def chat(self, contents=["How are you?"], friends=2):
        pass

    def post_status(self, contents):
        pass

    def browse_user_center(self, limit=3):
        pass
