#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FacebookException(BaseException):
    """
    :action: 0 检查首页是否存在, 1 是否记住密码页面, 2 忽略电话号码, 3 忽略上传头像, 4 忽略app下载
    """
    MAP_EXP_PROCESSOR = {0: {'key_word': 'div[id="MComposer"]', 'check': 'check_is_home', 'process': 'process_home'},
                         1: {'key_word': 'a[href^="/login/save-device/cancel/?"]', 'check': 'check_remember_password', 'process': 'process_add_password'},
                         2: {'key_word': 'div[data-sigil="mChromeHeaderRight"]', 'check': 'check_save_telnumber', 'process': 'process_img_verify'},
                         3: {'key_word': 'div[data-sigil="mChromeHeaderRight"]', 'check': 'check_add_imge', 'process': 'process_tel_verify'},
                         4: {'key_word': 'div[data-sigil="mChromeHeaderRight"]', 'check': 'check_load_app', 'process': 'process_load_app'},
                         5: {'key_word': 'button[id="nnn"]', 'check': 'check_verification', 'process': 'process_verification'}
                         }

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.exception_type = -1

    def auto_process(self, retry=1):
        while retry > 0:
            self.check()

            # 如果已经在home页面，不用处理
            if self.exception_type == 0:
                return True

            processor = self.MAP_EXP_PROCESSOR.get(self.exception_type, {}).get('process', '')
            if processor:
                if hasattr(self, processor):
                    ret = getattr(self, processor)()
            else:
                ret = False

            # 如果无法处理，不用再重试
            if not ret:
                return False
            retry -= 1
        return True

    def check(self):
        # 检查点
        self.exception_type = -1
        for k, v in self.MAP_EXP_PROCESSOR.items():
            check_func = v.get('check', '')
            if check_func and hasattr(self, check_func):
                if getattr(self, check_func)():
                    self.exception_type = k
                    break
        return self.exception_type

    def check_is_home(self):
        # 检查是否是首页
        try:
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(0)['key_word'])))
        except:
            return False
        return True

    def check_remember_password(self):
        # 记住账号密码
        try:
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(1)['key_word'])))
        except:
            return False
        return True

    def check_save_telnumber(self):
        # 首次登录电话号码验证略过
        try:
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(2)['key_word'])))
        except:
            return False
        return True

    def check_add_imge(self):
        # 上传头像
        try:
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(3)['key_word'])))
        except:
            return False
        return True

    def check_load_app(self):
        # 忽略下载ap也页面
        try:
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(4)['key_word'])))
        except:
            return False
        return True

    def check_verification(self):
        # 好友验证页面
        try:
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(5)['key_word'])))
        except:
            return False
        return True

    def process_home(self):
        # 处理是否在HOME页面
        processor = self.MAP_EXP_PROCESSOR.get(self.exception_type)
        if not processor:
            print("未检测到Home页面")
            return False

        if hasattr(self, self.processor):
            return getattr(self, processor)()
        return False

    def process_add_password(self):
        # 记住账号密码
        try:
            no_password = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(1)['key_word'])))
            no_password.click()
        except:
            return False
        return True

    def process_tel_verify(self):
        # 忽略电话号码
        try:
            tel_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(2)['key_word'])))
            tel_number.click()
        except:
            return False
        return True

    def process_img_verify(self):
        # 忽略上传头像
        try:
            tel_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(3)['key_word'])))
            tel_number.click()
        except:
            return False
        return True

    def process_load_app(self):
        # 上传头像
        time.sleep(3)
        try:
            never_save_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(4)['key_word'])))
            never_save_number.click()
        except:
            return False
        return True

    def process_verification(self):
        # 处理好友验证
        try:
            never_save_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(5)['key_word'])))
            never_save_number.click()
        except:
            return False
        return True


# if __name__ == '__main__':
#     fb = FacebookException(None)
#     fb.check()
#     fb.auto_process(6)


