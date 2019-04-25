#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config.config import get_support_args
import time
from urllib import parse
import requests

captcha_arg = get_support_args()


class CaptchaVerify:

    key_str = "data-sitekey"
    element_id = "recaptcha-demo"
    current_url = "https://www.facebook.com/checkpoint/block/"
    captcha_in_api = None
    captcha_res_api = None
    captcha_api_key = None

    def __init__(self, driver):
        CaptchaVerify.set_captcha_arg()
        self.driver = driver

    @classmethod
    def set_captcha_arg(cls):
        cls.captcha_in_api = captcha_arg.get("captcha_in_api")
        cls.captcha_res_api = captcha_arg.get("captcha_res_api")
        cls.captcha_api_key = captcha_arg.get("captcha_api_key")

    def handle_verify(self):
        """
        机器人验证，获取页面的特定字符串，向2captcha的API发送两次请求，最终将获取到的字符串提交到页面提交。
        """
        try:
            ele = self.driver.find_element_by_id()
            value = ele.get_attribute(CaptchaVerify.element_id)
            captcha_id = CaptchaVerify.get_captcha_id(value)
            captcha_str = CaptchaVerify.get_captcha_str(captcha_id)
            if not captcha_str:
                return False
            self.driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML="{}"'.format(captcha_str))
            self.driver.find_element_by_css_selector("button[id='checkpointSubmitButton']").click()
        except Exception as e:
            return False
        return True

    @classmethod
    def get_captcha_id(cls, value):
        """
        获取2capcha第一次请求的结果

        :param value: 页面data-sitekey的值
        :return: captcha_id
        """
        parameter = {
            "key": cls.captcha_api_key,
            "googlekey": cls.captcha_api_key,
            "pageurl": cls.current_url,
            "method": "userrecaptcha"
        }
        url = cls.current_url + "?" + parse.urlencode(parameter)
        result = requests.get(url)
        return result.text.split('|')[1]

    @classmethod
    def get_captcha_str(cls, captcha_id):
        """
        获取2capcha第二次请求的结果

        :param captcha_id: 2captcha第一次返回的captcha_id
        :return: 返回 2captcha字符串
        """
        parameter = {
            "key": cls.captcha_api_key,
            "action": "get",
            "id": captcha_id
        }
        url = cls.captcha_res_api + "?" + parse.urlencode(parameter)
        time.sleep(90)
        result = requests.get(url)
        count = 0
        while "CAPCHA_NOT_READY" in result.text and count < 20:
            result = requests.get(url)
            time.sleep(5)
            count += 1
        if "ERROR_CAPTCHA_UNSOLVABLE" in result.text:
            return False
        return result.text.split('|')[1]

