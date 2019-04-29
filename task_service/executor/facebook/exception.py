#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15

import os
import traceback
import shutil
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import logger
from executor.utils.facebook_captcha import CaptchaVerify
from executor.utils.utils import get_photo
from executor.web_actions import WebActions


class FacebookExceptionProcessor(BaseException, WebActions):
    """
    Facebook异常处理类, 包括异常码的定义、异常检测与处理
    """

    """
    :MAP_EXP_PROCESSOR:
    异常分类--
    -1: 未知异常
    0： 是否首页
    1： 是否记住密码提示
    2： 是否输入电话号码提示
    3： 是否上传头像提示,
    4： 是否下载app提示
    5： 账号被停用提示
    6： 身份验证类型二，跳转按钮
    7： 手机短信验证
    8： 上传上传图片验证
    9： 身份验证类型一，跳转按钮
    10： 登录 邮箱数字验证码验证
    11:  登录 手机短信验证码验证
    12： 账号密码不正确
    13： 移动端共享登录验证
    14:  条款和使用政策验证
    15:  机器人验证
    """
    MAP_EXP_PROCESSOR = {
        -1: {'name': 'unknown'},
        0: {'name': 'home',
            'key_words': {'mobile': {"css": ['div[id="MComposer"]'], "xpath": []},
                          "pc": {"css": ['div[id="MComposerPC"]']}}},
        1: {'name': 'remember_password',
            'key_words': {"mobile": {"css": ['a[href^="/login/save-device/cancel/?"]', 'button[type="submit"]']},
                          "pc": {"css": []}}},
        2: {'name': 'save_phone_number',
            'key_words': {"mobile": {"css": ['div[data-sigil="mChromeHeaderRight"]']},
                          "pc": {"css": []}}},
        3: {'name': 'upload_photo',
            'key_words': {"mobile": {"css": ['div[data-sigil="mChromeHeaderRight"]']},
                          "pc": {"css": []}}},
        4: {'name': 'download_app',
            'key_words': {"mobile": {"css": ['div[data-sigil="mChromeHeaderRight"]']},
                          "pc": {"css": []}}},
        5: {'name': 'account_invalid',
            'key_words': {"mobile": {"css": ['div[class^="mvm uiP fsm"]']},
                          "pc": {"css": ['div[class^="mvm uiP fsm"]']}},
            'account_status': 'invalid'},
        6: {'name': 'auth_button_two_verify',
            'key_words': {"mobile": {"css": ('button[name="submit[Continue]', 'div[id="checkpoint_subtitle"]')},
                          "pc": {"css": []}},
            'account_status': 'verifying_auth_button_two'},
        7: {'name': 'phone_sms_verify',
            'key_words': {"mobile": {"css": ['option[value="US"]']},
                          "pc": {"css": ('input[name="phone-name"]', 'input[name="p_c"]')}},
            'account_status': 'verifying_sms'},
        8: {'name': 'photo_verify',
            'key_words': {"mobile": {"css": ['input[name="photo-input"]', 'input[id="photo-input"]']},
                          "pc": {"css": []}},
            'account_status': 'verifying_photo'},
        9: {'name': 'auth_button_one_verify',
            'key_words': {"mobile": {"css": ['button[name="submit[Secure Account]"]']},
                          "pc": {"css": []}},
            'account_status': 'verifying_auth_button_one'},
        10: {'name': 'email_verify',
             'key_words': {"mobile": {"css": ['input[placeholder="######"]']},
                           "pc": {"css": []}},
             'account_status': 'verifying_email_code'},
        11: {'name': 'sms_verify',
             'key_words': {"mobile": {"css": ['input[name="p_c"]']},
                           "pc": {"css": []}},
             'account_status': 'verifying_sms_code'},
        12: {'name': 'wrong_password',
             'key_words': {"mobile": {"css": ['a[href^="/recover/initiate/?ars=facebook_login_pw_error&lwv"]']},
                           "pc": {"css": []}},
             'account_status': 'verifying_wrong_password'},
        13: {'name': 'shared_login',
             'key_words': {"mobile": {"css": ['a[href^="https://facebook.com/mobile/click/?redir_url=https"]']},
                           "pc": {"css": []}},
             'account_status': 'verifying_shared_login'},
        14: {'name': 'policy_clause',
             'key_words': {"mobile": {"css": ['button[value="J’accepte"]']},
                           "pc": {"css": []}},
             'account_status': 'verifying_policy_clause'},
        15: {"name": 'robot_verify',
             'key_words': {"mobile": {"css": ['div[class="g-recaptcha"]'],'iframe': ["captcha-recaptcha"]},
                           "pc": {"css": ['div[class="recaptcha-checkbox-checkmark"]'], "iframe": ["captcha-recaptcha", 0]}},
             'account_status': 'verifying_robot'},
    }

    def __init__(self, driver: WebDriver, env="mobile", account="", gender=1):
        self.driver = driver
        self.exception_type = -1
        self.env = env
        tac = traceback.extract_stack()
        self.caller = tac[-2][2]
        self.account = account
        self.gender = gender
        self.trace_info = "[{}:env={}, caller={}, account={}]".format(
            self.__class__.__name__, self.env, self.caller, self.account)

    @property
    def exception_name(self):
        return self.MAP_EXP_PROCESSOR.get(self.exception_type, {}).get('name', 'unknown')

    @property
    def account_status(self):
        return self.MAP_EXP_PROCESSOR.get(self.exception_type, {}).get('account_status', '')

    def get_key_words(self, code, category='css', index=0):
        """
        根据异常码返回其关键字，
        :param code: 异常码
        :param category: 关键字类别， 可以为空，为空时返回正个keywords字典.
        :param index: 关键字索引， 小于零时反回整个关键字列表
        :return: 关键字（列表）
        """
        keywords_dict = self.MAP_EXP_PROCESSOR.get(code, {}).get('key_words', {}).get(self.env, {})
        if category:
            if index >= 0:
                return keywords_dict.get(category, [])[index]
            else:
                return keywords_dict.get(category, [])
        else:
            return keywords_dict

    def auto_process(self, retry=1, wait=3):
        """
        自动处理异常，根据异常类型对症处理，
        :param retry: 重试次数
        :param wait: 重试间隔，单位秒
        :return: 元组 -- （结果, 异常码）
        """
        logger.info('call auto process, retry={}, wait={}, trace_info={}'.format(retry, wait, self.trace_info))
        while retry > 0:
            self.exception_type = self.auto_check()

            # 如果已经在home页面或者是未知异常，不用处理
            if self.exception_type == 0:
                logger.info('auto process succeed, status==0')
                return True, 0
            elif self.exception_type == -1:
                logger.info('auto process failed, status==-1')
                return False, -1

            processor = 'process_{}_{}'.format(self.exception_name, self.env)
            if hasattr(self, processor):
                ret, status = getattr(self, processor)()
            else:
                logger.error('auto_process can not find processor. processor={}'.format(processor))
                ret, status = False, -1

            # 如果无法处理，不用再重试
            if not ret:
                logger.error('auto process failed, return: {}, exception code: {}, name={}, '
                             'account status={}, trace_info={}'.format(ret, status, self.exception_name,
                                                                       self.account_status, self.trace_info))
                return ret, status
            retry -= 1
            time.sleep(wait)

        logger.error('auto process succeed, status={}, trace_info={}'.format(status, self.trace_info))
        return ret, status

    def auto_check(self):
        # 自动检查点, 返回相应的异常码
        for k, v in self.MAP_EXP_PROCESSOR.items():
            if k == -1:
                continue

            name = v.get('name', '')
            check_func = 'check_{}_{}'.format(name, self.env)

            # 遍历所有异常， 如果有自己定义的检测函数则执行，如果没有，则调用通用检测函数
            if name and hasattr(self, check_func):
                if getattr(self, check_func)(v.get('key_words', {}).get(self.env, {})):
                    self.exception_type = k
                    break
                # else:
                #     logger.warning("auto_check invoke: {} return False, code={}, trace_info={}".format(check_func, k,
                #                                                                                        self.trace_info))
            else:
                if self.check_func(v.get('key_words', {}).get(self.env, {})):
                    self.exception_type = k
                    break
                # else:
                #     logger.warning(
                #         "auto_check invoke check_func return False, code={}, trace_info={}".format(k, self.trace_info))
        else:
            self.exception_type = -1
            logger.warning('auto_check failed exception=-1, trace_info={}'.format(self.trace_info))
            return self.exception_type

        logger.info(
            'auto_check succeed, exception type={}, name={}, trace_info={}'.format(self.exception_type, self.exception_name,
                                                                              self.trace_info))
        return self.exception_type

    def check_func(self, key_words, wait=3):
        """
        通用检测函数, 判断当前页面是存在指定的关键字集合
        :param key_words: 关键字集合, 字典类型, 目前支持css和xpath, css或xpath内部为list或tuple, list代表各关键字之间是且的关系， tuple代表各关键字之间是或的关系
        :param wait: 查找关键字时的最大等待时间， 默认3秒
        :return: 成功返回 True, 失败返回 False
        """
        print(key_words)
        css_keywords = key_words.get("css", [])
        xpath_keywords = key_words.get("xpath", [])
        iframe = key_words.get("iframe", None)  # 查找关键字之前需要切换至的iframe, 类型为list, 其中元素可以为int或str, int代表iframe的索引, str-代表iframe的id.
        if not any([css_keywords, xpath_keywords]):
            self.exception_type = -1
            logger.error("check func keywords is empty.")
            return False

        key_words_type = By.CSS_SELECTOR
        key_words = css_keywords
        if not css_keywords:
            key_words = xpath_keywords
            key_words_type = By.XPATH

        succeed_count = 0
        is_and_relation = isinstance(key_words, list)
        for key in key_words:
            try:
                if iframe:
                    for ifa in iframe:
                        self.driver.switch_to.frame(ifa)
                        time.sleep(1)

                WebDriverWait(self.driver, wait).until(
                    EC.presence_of_element_located((key_words_type, key)))
            except Exception as e:
                # 如是且的关系，任何一个异常， 即说明条件不满足
                # logger.warning("check_func e={}, key={}, trace_info={}".format(e, key, self.trace_info))
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

    def process_remember_password_mobile(self):
        """
        # 记住账号密码
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("忽略保存账号密码处理中")
            no_password = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.get_key_words(1, index=1))))
            self.click(no_password)
        except Exception as e:
            logger.exception("忽略保存账号密码处理异常, e={}".format(e))
            return False, 1

        logger.info("忽略保存账号密码成功")
        return True, 1

    def process_save_phone_number_mobile_mobile(self):
        """
         # 忽略电话号码提示
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("忽略输入电话号码处理中")
            tel_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.get_key_words(2))))
            self.click(tel_number)
            time.sleep(3)
        except Exception as e:
            logger.exception("忽略输入电话号码处理异常, e={}".format(e))
            return False, 2
        logger.info("忽略输入电话号码成功")
        return True, 2

    def process_upload_photo_mobile(self):
        """
        # 忽略上传头像提示
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info('忽略上传图像处理中')
            tel_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.get_key_words(3))))
            self.click(tel_number)
        except Exception as e:
            logger.info('忽略上传图像处理异常， e={}'.format(e))
            return False, 3
        logger.info('忽略上传图像成功')
        return True, 3

    def process_download_app_mobile(self):
        """
         # 忽略下载APP提示
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """

        time.sleep(3)
        try:
            logger.info('忽略下载app处理中')
            never_save_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.get_key_words(4))))
            self.click(never_save_number)
        except Exception as e:
            logger.exception("忽略下载app提示处理异常, e={}".format(e))
            return False, 4
        logger.info('忽略下载app提示处理成功')
        return True, 4

    def process_account_invalid_mobile(self):
        """
        # 账号被封杀
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info('账号被封杀处理中')
            never_save_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.get_key_words(5))))
            self.click(never_save_number)
        except Exception as e:
            logger.exception("账号被封杀处理异常, e={}".format(e))
            return False, 5
        logger.info("账号被封杀")
        return False, 5

    def process_auth_button_two_verify_mobile(self):
        """
        身份验证类型二，跳转按钮
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        将两步验证的函数设置为False
        """
        try:
            logger.info('身份验证类型二，跳转按钮,处理中')
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.get_key_words(6))))
        except Exception as e:
            logger.exception("身份验证类型二,跳转按钮, e={}".format(e))
            return False, 6
        logger.info('身份验证类型二，跳转按钮,处理成功')
        return False, 6

    def process_phone_sms_verify_mobile(self):
        """
        # 手机短信验证码验证
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        提示  为了调试方便 调整为FALSE
        """
        try:
            logger.info("手机短信验证处理中")
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.get_key_words(7))))
            # # 操作下拉列表
            # s1 = Select(self.driver.find_element_by_name('p_pc'))
            # s1.select_by_value('CN')
            # # 输入电话号码
            # WebDriverWait(self.driver, 6).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="tel"]'))).send_keys('18000000000')
            # # 点击继续
            # WebDriverWait(self.driver, 6).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, 'button[id="checkpointSubmitButton-actual-button"]'))).click()
            # email_code = WebDriverWait(self.driver, 6).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocorrect="off"]')))
            # if email_code:
            #     logger.info("The mailbox verification code has been sent successfully")
            #     email_code.send_keys('456895')

        except Exception as e:
            logger.exception("处理手机短信验证处理异常, e={}".format(e))
            return False, 7
        logger.info("处理手机短信验证处理完成")
        return False, 7

    def process_phone_sms_verify_pc(self):
        """
        # 手机短信验证码验证
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        提示  为了调试方便 调整为FALSE
        """
        try:
            logger.info("手机短信验证处理中")
            try:
                tel_code = self.driver.find_element_by_css_selector(self.get_key_words(7, "css", 1))
                if tel_code:
                    sub_button = self.driver.find_element_by_css_selector('button[id="checkpointSecondaryButton"]')
                    self.click(sub_button)
            except:
                pass
            rtime = random.randint(2, 4)
            try:
                tel_button = self.driver.find_elements_by_css_selector('i[class^="img sp_"]')
                if not tel_button:
                    return False, -1
            except:
                pass
            self.click(tel_button[3])
            tel_stutas = self.driver.find_elements_by_css_selector('a[role="menuitemcheckbox"]')
            self.click(tel_stutas[45])

            time.sleep(rtime)
            send_tel = self.driver.find_element_by_css_selector('input[type="tel"]')
            self.send_keys(send_tel, "16500000000")

            time.sleep(rtime)
            submit_button = self.driver.find_element_by_css_selector('button[id="checkpointSubmitButton"]')
            self.click(submit_button)

            # 提交失败
            try:
                submit_error = WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-xui-error-position="above"]')))
                if submit_error:
                    logger.error("请填写正确的手机号码")
                    return False, 7
            except:
               pass
            # 短信验证码
            time.sleep(rtime)
            tel_code = self.driver.find_element_by_css_selector('input[name="p_c"]')
            self.send_keys(tel_code, "414141")

            time.sleep(rtime)
            submit_button = self.driver.find_element_by_css_selector('button[id="checkpointSubmitButton"]')
            self.click(submit_button)

        except Exception as e:
            logger.exception("处理手机短信验证处理异常, e={}".format(e))
            return False, 7
        logger.info("处理手机短信验证处理完成")
        return False, 7

    def process_photo_verify_mobile(self):
        """
        # 上传图片验证
        :param kwargs:
       :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("处理上传图片验证处理中")
            photo_upload = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.get_key_words(8))))

            photo_path = get_photo(self.account, self.gender)
            logger.info('process_photo_verify photo path={}'.format(photo_path))
            if not photo_path:
                return False, 8
            # photo_path = 'E:\\IMG_3563.JPG'
            # 上传图片
            self.send_keys(photo_upload, photo_path)
            # photo_upload.send_keys(photo_path)
            # 点击继续
            phone_button = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[id="checkpointSubmitButton-actual-button"]')))
            self.click(phone_button)
            # 重新检查页面
            photo_btn = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="submit[OK]"]')))
            if photo_btn:
                logger.info("photo uploaded successfully!")
                account_photo_path = os.path.join(os.path.dirname(os.path.dirname(photo_path)),
                                                  "{}.jpg".format(self.account))
                shutil.move(photo_path, account_photo_path)
                logger.info("process photo verify succeed, photo path={}".format(account_photo_path))
            else:
                logger.warning("process photo verify unfinished, photo path={}".format(photo_path))
                os.remove(photo_path)
        except Exception as e:
            logger.exception("上传照片验证异常, e={}".format(e))
            return False, 8
        logger.info("处理上传图片验证的完成")
        return True, 8

    def process_auth_button_one_verify_mobile(self):
        """
        身份验证类型一，跳转按钮
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("身份验证类型一，跳转按钮处理中")
            check_button = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.get_key_words(9))))
            self.click(check_button)
        except Exception as e:
            logger.exception("身份验证类型一，跳转按钮处理异常, e={}".format(e))
            return False, 9
        logger.info("身份验证类型一，跳转按钮处理完成")
        return True, 9

    def process_email_verify_mobile(self):
        """
        登录邮箱数字验证码验证
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("登录邮箱数字验证码验证处理中")
            check_button =WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.get_key_words(10))))
            self.click(check_button)
        except Exception as e:
            logger.exception("登录邮箱数字验证码验证处理异常, e={}".format(e))
            return False, 10
        logger.info("登录邮箱数字验证码验证处理完成")
        return True, 10

    def process_sms_verify_mobile(self):
        """
        短信验证码验证
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("登录短信验证码验证处理中")
            WebDriverWait(self.driver, 6).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(11)['key_words'][0])))
            check_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[name="submit[Back]"]')))
            self.click(check_button)
        except Exception as e:
            logger.exception("手机短信验证码验证处理异常, e={}".format(e))
            return False, 11
        logger.info("登录短信验证码验证处理完成")
        return True, 11

    def process_wrong_password_mobile(self):
        """
        账号密码不正确
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("账号密码不正确 处理中")
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.get_key_words(12))))
        except Exception as e:
            logger.exception("账号密码不正确处理异常, e={}".format(e))
            return False, -1
        logger.info("账号密码不正确")
        return False, -1

    def process_shared_login_mobile(self):
        """
        移动端手机共享登录验证
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("移动端共享登录验证处理中")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.get_key_words(13))))
            check_button = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-sigil="MBackNavBarClick"]')))
            self.click(check_button)

        except Exception as e:
            logger.exception("移动端手机共享登录验证处理异常, e={}".format(e))
            return False, 13
        logger.info("移动端共享登录验证")
        return False, 13

    def process_policy_clause_mobile(self):
        """
        条款和使用政策验证
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("条款和使用政策验证处理中")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.get_key_words(14))))
            check_button = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[value="J’accepte"]')))
            self.click(check_button)
            check_revenir = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[value="Revenir au fil d’actualité"]')))
            self.click(check_revenir)
        except Exception as e:
            logger.exception("条款和使用政策验证处理异常, e={}".format(e))
            return False, 14

        logger.info("条款和使用政策验证处理完成")
        return True, 14

    def process_robot_verify_mobile(self):
        """
        机器人验证
        :param kwargs:
        :return:
        """
        try:
            logger.info("机器人验证: beginning")
            result = CaptchaVerify(self.driver).handle_verify()
            logger.info("机器人验证: endding")
        except Exception as e:
            logger.error("机器人验证: 异常-->{}".format(str))
            return False, 15
        if not result:
            return False, 15
        return True, 15

    def process_robot_verify_pc(self):
        """
        PC端机器人验证
        :param kwargs:
        :return:
        """
        try:
            logger.info("机器人验证begning")
            result = CaptchaVerify(self.driver).handle_verify()
            logger.info("机器人验证: endding")
        except Exception as e:
            logger.error("机器人验证: 异常-->{}".format(str))
            return False, 15
        if not result:
            return False, 15
        return True, 15


def test():
    fbe = FacebookExceptionProcessor(None, env='pc', account="a@b.com", gender=1)
    print(fbe.caller)
    print(fbe.exception_name)


if __name__ == '__main__':
    test()
