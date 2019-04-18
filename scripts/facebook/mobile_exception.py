#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15

import os, sys
import shutil
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import logger, get_account_args


class FacebookException(BaseException):
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
    15： 邮箱验证前的继续按钮
    """
    MAP_EXP_PROCESSOR = {
        -1: {'name': 'unknown'},
        0: {'name': 'home', 'key_words': ['div[id="MComposer"]']},
        1: {'name': 'remember_password', 'key_words': ['a[href^="/login/save-device/cancel/?"]', 'button[type="submit"]']},
        2: {'name': 'save_phone_number', 'key_words': ['div[data-sigil="mChromeHeaderRight"]']},
        3: {'name': 'upload_photo', 'key_words': ['div[data-sigil="mChromeHeaderRight"]']},
        4: {'name': 'download_app', 'key_words': ['div[data-sigil="mChromeHeaderRight"]']},
        5: {'name': 'account_invalid', 'key_words': ['div[class^="mvm uiP fsm"]'], 'account_status': 'invalid'},
        6: {'name': 'auth_button_two_verify', 'key_words': ['button[name="submit[Continue]', 'div[id="checkpoint_subtitle"]'], 'account_status': 'verifying_auth_button_two'},
        7: {'name': 'phone_sms_verify', 'key_words': ['option[value="US"]'], 'account_status': 'verifying_sms'},
        8: {'name': 'photo_verify', 'key_words': ['input[name="photo-input"]', 'input[id="photo-input"]'], 'account_status': 'verifying_photo'},
        9: {'name': 'auth_button_one_verify', 'key_words': ['button[name="submit[Secure Account]"]'], 'account_status': 'verifying_auth_button_one'},
        10: {'name': 'email_verify', 'key_words': ['input[placeholder="######"]'], 'account_status': 'verifying_email_code'},
        11: {'name': 'sms_verify', 'key_words': ['input[name="p_c"]'], 'account_status': 'verifying_sms_code'},
        12: {'name': 'wrong_password', 'key_words': ['a[href^="/recover/initiate/?ars=facebook_login_pw_error&lwv"]'], 'account_status': 'verifying_wrong_password'},
        13: {'name': 'shared_login', 'key_words': ['a[href^="https://facebook.com/mobile/click/?redir_url=https"]'], 'account_status': 'verifying_shared_login'},
        14: {'name': 'policy_clause', 'key_words': ['button[value="J’accepte"]'], 'account_status': 'verifying_policy_clause'},
    }

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.exception_type = -1

    def auto_process(self, retry=1, wait=2, **kwargs):
        """
        自动处理异常，根据异常类型对症处理，
        :param retry: 重试次数
        :param wait: 重试间隔，单位秒
        :return: 元组 -- （结果, 异常码）
        """
        logger.info('call auto process, retry={}, wait={}, kwargs={}'.format(retry, wait, kwargs))
        while retry > 0:
            exception_type = self.auto_check()

            # 如果已经在home页面或者是未知异常，不用处理
            if exception_type == 0:
                logger.info('auto process succeed, status==0')
                return True, 0
            elif exception_type == -1:
                logger.info('auto process failed, status==-1')
                return False, -1

            processor = 'process_{}'.format(self.MAP_EXP_PROCESSOR.get(exception_type, {}).get('name', ''))
            if hasattr(self, processor):
                ret, status = getattr(self, processor)(**kwargs)
            else:
                logger.error('auto_process can not find processor. processor={}'.format(processor))
                ret, status = False, -1

            # 如果无法处理，不用再重试
            if not ret:
                logger.error('auto process failed, return: {}, exception code: {}, name={}, account status={}'
                             .format(ret, status, self.MAP_EXP_PROCESSOR[status]['name'], self.MAP_EXP_PROCESSOR[status].get('account_status', '')))
                return ret, status
            retry -= 1
            time.sleep(wait)

        logger.error('auto process succeed')
        return ret, status

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

        logger.info('auto_check get exception type={}, name={}'.format(self.exception_type, self.MAP_EXP_PROCESSOR[self.exception_type]['name']))
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

    def process_remember_password(self, **kwargs):
        """
        # 记住账号密码
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("处理理忽略保存账号密码")
            no_password = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(1)['key_words'][1])))
            no_password.click()
        except Exception as e:
            logger.exception("处理理忽略保存账号密码失败, e={}".format(e))
            return False, 1

        logger.info("处理理忽略保存账号密码成功")
        return True, 1

    def process_save_phone_number(self, **kwargs):
        """
         # 忽略电话号码提示
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("忽略输入电话号码")
            tel_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(2)['key_words'][0])))
            tel_number.click()
            logger.info("忽略输入电话号码成功")
        except Exception as e:
            logger.exception("忽略输入电话号码失败, e={}".format(e))
            return False, 2
        return True, 2

    def process_upload_photo(self, **kwargs):
        """
        # 忽略上传头像提示
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info('忽略上传图像')
            tel_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(3)['key_words'][0])))
            tel_number.click()
            logger.info('忽略上传图像成功')
        except Exception as e:
            logger.info('忽略上传图像失败， e={}'.format(e))
            return False, 3
        return True, 3

    def process_download_app(self, **kwargs):
        """
         # 忽略下载APP提示
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """

        time.sleep(3)
        try:
            logger.info('忽略下载app')
            never_save_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(4)['key_words'][0])))
            never_save_number.click()
        except:
            return False, 4
        return True, 4

    def process_account_invalid(self, **kwargs):
        """
        # 过度页面点击
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info('账号被封杀')
            never_save_number = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(5)['key_words'][0])))
            never_save_number.click()
        except:
            return False, 5
        return False, 5

    def process_auth_button_two_verify(self, **kwargs):
        """
        身份验证类型二，跳转按钮
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info('身份验证类型二，跳转按钮')
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(6)['key_words'][0])))
        except:
            return False, 6
        return False, 6

    def process_phone_sms_verify(self, **kwargs):
        """
        # 手机短信验证码验证
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("处理手机短信验证")
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(7)['key_words'][0])))
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

        except:
            return False, 7
        return False, 7

    def process_photo_verify(self, **kwargs):
        """
        # 上传图片验证
        :param kwargs:
       :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("处理上传图片验证的异常")
            photo_upload = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(8)['key_words'][0])))
            account = ''
            gender = 1
            for k, v in kwargs.items():
                if k == 'account':
                    account = v
                elif k == 'gender':
                    gender = v
            photo_path = self.get_photo(account, gender)
            logger.info('process_photo_verify photo path={}'.format(photo))
            # photo_path = 'E:\\IMG_3563.JPG'
            # 上传图片
            photo_upload.send_keys(photo_path)
            # 点击继续
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[id="checkpointSubmitButton-actual-button"]'))).click()
            # 重新检查页面
            photo_btn = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[name="submit[OK]"]')))
            if photo_btn:
                logger.info("photo uploaded successfully!")
                account_photo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(photo_path))), "{}.jpg".format(account))
                shutil.move(photo_path, account_photo_path)
                logger.info("process photo verify succeed, photo path={}".format(account_photo_path))
                return True, 8
            else:
                logger.warning("process photo verify unfinished, photo path={}".format(photo_path))
                os.remove(photo_path)
        except:
            return False, 8
        return False, 8

    def process_auth_button_one_verify(self, **kwargs):
        """
        身份验证类型一，跳转按钮
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("身份验证类型一，跳转按钮")
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(9)['key_words'][0]))).click()
        except:
            return False, 9
        return False, 9

    def process_email_verify(self, **kwargs):
        """
        登录邮箱数字验证码验证
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("登录邮箱数字验证码验证")
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(10)['key_words'][0]))).click()
        except:
            return False, 10
        return False, 10

    def process_sms_verify(self, **kwargs):
        """
        短信验证码验证
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("登录短信验证码验证")
            WebDriverWait(self.driver, 6).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(11)['key_words'][0])))
            WebDriverWait(self.driver, 6).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[name="submit[Back]"]'))).click()
        except:
            return False, 11
        return False, 11

    def process_wrong_password(self, **kwargs):
        """
        账号密码不正确
        :param kwargs:
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("账号密码不正确")
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(12)['key_words'][0])))
        except:
            return False, -1
        return False, -1

    def process_shared_login(self, **kwargs):
        """
        移动端手机共享登录验证
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("移动端共享登录验证")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(13)['key_words'][0])))
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-sigil="MBackNavBarClick"]'))).click()
        except:
            return False, 13
        return False, 13

    def process_policy_clause(self, **kwargs):
        """
        条款和使用政策验证
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("条款和使用政策验证")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(14)['key_words'][0])))
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[value="J’accepte"]'))).click()
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[value="Revenir au fil d’actualité"]'))).click()
        except:
            return False, 14
        return False, 14

    def process_step_email_verify(self, **kwargs):
        """
        :action:  邮箱验证前的登录按钮处理  暂时没有做点击处理
        :return: 成功返回 True, 失败返回 False
        """
        try:
            logger.info("邮箱验证前的继续按钮处理")
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.MAP_EXP_PROCESSOR.get(15)['key_words'][0])))
        except:
            return False, 15
        return False, 15

    def download_photo(self, account, gender):
        logger.info('start download photo from server, account={}, gender={}'.format(account, gender))
        remote_photo_path = get_account_args()['remote_photo_path']
        local_photo_path = os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), get_account_args()['local_photo_path'])
        save_path = os.path.join(local_photo_path, "{}.jpg".format(account))
        # 下载保存到本地
        # do something

        # 测试阶段直接从本地拿图片, 根据性别请求一张图片
        if gender == 0:
            random_photo_dir = os.path.join(local_photo_path, 'female')
        else:
            random_photo_dir = os.path.join(local_photo_path, 'male')

        photos = os.listdir(random_photo_dir)
        rad_idx = random.randint(1, 10000) % len(photos)
        random_photo_name = os.path.join(random_photo_dir, photos[rad_idx])

        # 把照片从随机池中取到账号池中
        # shutil.move(random_photo_name, save_path)
        save_path = random_photo_name

        logger.info('download photo from server, account={}, gender={}, save_path={}'.format(account, gender, save_path))
        return save_path

    def get_photo(self, account, gender):
        try:
            local_photo_path = local_photo_path = os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), get_account_args()['local_photo_path'])

            # 先在本地找
            local_photo_name = os.path.join(local_photo_path, "{}.jpg".format(account))
            if os.path.exists(local_photo_name):
                logger.info('get photo from local path={}'.format(local_photo_name))
                return local_photo_name
            else:
                # 如果本地没有，则去下载
                return self.download_photo(account, gender)
        except Exception as e:
            logger.error('get photo failed. account={}, e={}'.format(account, e))
            return ''


if __name__ == '__main__':
    fbe = FacebookException(None)
    photo = fbe.get_photo('abc@com', 1)
    print(photo)
