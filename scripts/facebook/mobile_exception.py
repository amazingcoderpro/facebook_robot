#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import logger


class FacebookException(BaseException):
    """
    :MAP_EXP_PROCESSOR:
    异常分类--
    -1: 未知异常
    0：是否首页
    1：是否记住密码提示
    2：是否输入电话号码提示
    3：是否上传头像提示,
    4：是否下载app提示
    5：账号被禁用的提示
    6：上次登录机器&好友识别身份验证
    7：手机短信验证
    8：上传图象验证
    """
    MAP_EXP_PROCESSOR = {
        -1: {'name': 'unknown'},
        0: {'name': 'home', 'key_words': ['div[id="MComposer"]']},
        1: {'name': 'remember_password', 'key_words': ['a[href^="/login/save-device/cancel/?"]']},
        2: {'name': 'save_phone_number', 'key_words': ['div[data-sigil="mChromeHeaderRight"]']},
        3: {'name': 'upload_photo', 'key_words': ['div[data-sigil="mChromeHeaderRight"]']},
        4: {'name': 'download_app', 'key_words': ['div[data-sigil="mChromeHeaderRight"]']},
        5: {'name': 'account_invalid', 'key_words': ['div[class^="mvm uiP fsm"]'], 'account_status': 'invalid'},
        6: {'name': 'ask_question', 'key_words': ['div[id="checkpoint_subtitle"]'], 'account_status': 'verifying'},
        7: {'name': 'phone_sms_verify', 'key_words': ['option[value="US"]'], 'account_status': 'verifying'},
        8: {'name': 'photo_verify', 'key_words': ['button[data-store^="{"nativeClick":true}"]'], 'account_status': 'verifying'}
    }

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.exception_type = -1

    def auto_process(self, retry=1, wait=2):
        """
        自动处理异常，根据异常类型对症处理，
        :param retry: 重试次数
        :param wait: 重试间隔，单位秒
        :return: 元组 -- （结果, 异常码）
        """
        while retry > 0:
            exception_type = self.auto_check()

            # 如果已经在home页面或者是未知异常，不用处理
            if exception_type == 0:
                return True, 0
            elif exception_type == -1:
                return False, -1

            processor = 'process_{}'.format(self.MAP_EXP_PROCESSOR.get(exception_type, {}).get('name', ''))
            if hasattr(self, processor):
                ret, status = getattr(self, processor)()
            else:
                ret, status = False, -1

            # 如果无法处理，不用再重试
            if not ret:
                logger.error('auto process failed, return: {}, exception code: {}'.format(ret, status))
                return ret, status
            retry -= 1
            time.sleep(wait)

        logger.error('auto process succeed')
        return True, 0

    def auto_check(self):
        # 自动检查点, 返回相应的异常码
        for k, v in self.MAP_EXP_PROCESSOR.items():
            if k == -1:
                continue

            name = v.get('name', '')
            check_func = 'check_{}'.format(name)

            # 遍历所有异常， 如果有自己定义的检测函数则执行，如果没有，则调用通用检测函数
            if name and hasattr(self, check_func):
                if getattr(self, check_func)():
                    self.exception_type = k
                    break
            else:
                if self.check_func(v.get('key_words', [])):
                    self.exception_type = k
                    break
        else:
            self.exception_type = -1

        logger.info('auto_check get exception type={}, name={}'.format(self.exception_type, name))
        return self.exception_type

    def check_func(self, key_words, wait=2):
        """
        通用检测函数, 判断当前页面是存在指定的关键字集合
        :param key_words: 关键字集合, list或tuple, list代表各关键字之间是且的关系， tuple代表各关键字之间是或的关系
        :param wait: 查找关键字时的最大等待时间， 默认5秒
        :return: 成功返回 True, 失败返回 False
        """
        succeed_count = 0
        is_and_relation = isinstance(key_words, list)
        for key in key_words:
            try:
                WebDriverWait(self.driver, wait).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, key)))
            except:
                # 如是且的关系，任何一个异常， 即说明条件不满足
                if is_and_relation:
                    break
            else:
                succeed_count += 1
                if not is_and_relation:
                    break

        # 如果是或的关系， 只要有一个正常， 即说明条件满足
        if (is_and_relation and succeed_count == len(key_words)) or (not is_and_relation and succeed_count > 0):
            return True
        else:
            return False

    def process_remember_password(self):
        # 记住账号密码
        try:
            logger.info("处理理忽略保存账号密码")
            no_password = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(1)['key_word'])))
            no_password.click()

        except:
            return False, 1
        return True, 1

    def process_save_phone_number(self):
        # 忽略电话号码
        try:
            logger.info("忽略输入电话号码成功")
            tel_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(2)['key_word'])))
            tel_number.click()
        except:
            return False, 2
        return True, 2

    def process_upload_photo(self):
        # 忽略上传头像
        try:
            logger.info('忽略上传图像')
            tel_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(3)['key_word'])))
            tel_number.click()
        except:
            return False, 3
        return True, 3

    def process_download_app(self):
        # 下载APP
        time.sleep(3)
        try:
            logger.info('忽略下载app')
            never_save_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(4)['key_word'])))
            never_save_number.click()
        except:
            return False, 4
        return True, 4

    def process_account_invalid(self):
        # 过度页面点击
        try:
            logger.info('账号被封杀')
            never_save_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(5)['key_word'])))
            never_save_number.click()
        except:
            return False, 5
        return False, 5

    def process_ask_question(self):
        # 身份验证
        try:
            logger.info('处理身份验证问题')
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(6)['key_word'])))
        except:
            return False, 6
        return False, 6

    def process_phone_sms_verify(self):
        # 手机短信验证码验证
        try:
            logger.info("处理手机短信验证")
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(7)['key_word'])))
        except:
            return False, 7
        return False, 7

    def process_photo_verify(self):
        # 上传图片验证
        try:
            logger.info("处理上传图片验证的异常")
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(8)['key_word'])))
        except:
            return False, 8
        return False, 8




