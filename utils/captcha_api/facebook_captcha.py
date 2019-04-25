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
    current_url = "https://www.google.com/recaptcha/api2/demo"
    captcha_in_api = None
    captcha_res_api = None
    captcha_api_key = None

    def __init__(self ,driver):
        CaptchaVerify.set_captcha_arg()
        self.driver = driver

    @classmethod
    def set_captcha_arg(cls):
        cls.captcha_in_api = captcha_arg.get("captcha_in_api")
        cls.captcha_res_api = captcha_arg.get("captcha_res_api")
        cls.captcha_api_key = captcha_arg.get("captcha_api_key")

    def handle_verify(self):
        try:
            ele = self.driver.find_element_by_id()
            value = ele.get_attribute(CaptchaVerify.element_id)
            captcha_id = CaptchaVerify.get_captcha_id(value)
            captcha_str = CaptchaVerify.get_captcha_str(captcha_id)
            self.driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML="{}"'.format(captcha_str))
            self.driver.find_element_by_css_selector('input[id="recaptcha-demo-submit"]').click()
        except Exception as e:
            return False
        return True

    @classmethod
    def get_captcha_id(cls, value):
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
        parameter = {
            "key": cls.captcha_api_key,
            "action": "get",
            "id": captcha_id
        }
        url = cls.captcha_res_api + "?" + parse.urlencode(parameter)
        result = requests.get(url)
        while 'CAPCHA_NOT_READY' in result:
            result = requests.get(url).text
            time.sleep(5)
        return result.text.split('|')[1]
