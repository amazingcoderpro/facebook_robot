#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-04-15
# Function:

import os
import time
import random
from datetime import datetime, timedelta
from config import logger, get_account_args, get_fb_friend_keys, get_fb_posts, get_fb_chat_msgs, get_system_args
import scripts.facebook as fb


class TaskHelper:
    """
    任务配置及判断辅助类
    """
    def __init__(self, inputs):
        self.is_valid = True
        if not isinstance(inputs, dict):
            self.is_valid = False
            return
        self.task_info = inputs.get('task', None)
        if not self.task_info:
            self.is_valid = False
            return

        self.account_info = inputs.get('account', None)
        if not self.account_info:
            self.is_valid = False
            return

        self.system = inputs.get('system', {})
        self.headless = self.system.get('headless', True)
        self.task_id = self.task_info.get('task_id', -1)
        task_config = self.task_info.get('configure', {})
        self.is_post = task_config.get('is_post', False)
        self.post_content = task_config.get('post_content', '')
        self.is_add_friend = task_config.get('is_add_friend', False)
        self.friend_keys = task_config.get('friend_key', '')
        self.is_chat = task_config.get('is_chat', False)
        self.chat_content = task_config.get('chat_content', '')

        self.account = self.account_info.get('account')
        self.password = self.account_info.get('password')
        self.account_status = self.account_info.get('status')
        self.active_browser = self.account_info.get("active_browser")
        self.gender = self.account_info.get('gender', 0)
        self.email = self.account_info.get('email', '')
        self.email_pwd = self.account_info.get('email_pwd', '')
        self.phone_number = self.account_info.get('phone_number', '')
        self.birthday = self.account_info.get('birthday', '')
        self.national_id = self.account_info.get('national_id', '')
        self.name = self.account_info.get('name', '')
        self.active_area = self.account_info.get('active_area', '')
        self.profile_path = self.account_info.get('profile_path', '')

        account_configure = self.account_info.get("configure", {})
        self.last_login_time = account_configure.get('last_login', '')
        self.last_verifying_time = account_configure.get('last_verify', '')
        self.last_post_time = account_configure.get('last_post', '')
        self.last_add_friend_time = account_configure.get('last_add_friend', '')
        self.last_chat_time = account_configure.get('last_chat', '')

        self.login_interval = get_account_args().get('login_interval', 3600)
        self.verify_interval = get_account_args().get('verify_interval', 36000)
        self.post_interval = get_account_args().get('post_interval', 36000)
        self.add_friend_interval = get_account_args().get('add_friend_interval', 86400)

    def is_inputs_valid(self):
        return self.is_valid

    def is_should_login(self):
        """
        通过判断上次登录时间与当前时间间隔决定是否可以登录
        :return:
        """
        if self.last_login_time:
            dt_last_login = datetime.strptime(self.last_login_time, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - dt_last_login).total_seconds() < self.login_interval:
                logger.warning('Less than {} seconds before the last login, last login at: {}'.format(self.login_interval, self.last_login_time))
                return False

        return True

    def is_should_post(self):
        """
        通过判断上次发状态时间与当前时间间隔决定是否可以发状态
        :return:
        """
        if self.last_post_time:
            dt_last_post = datetime.strptime(self.last_post_time, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - dt_last_post).total_seconds() < self.post_interval:
                logger.warning('Less than {} seconds before the last post, last post at: {}'.format(self.post_interval, self.last_post_time))
                return False

        return True

    def is_should_add_friend(self):
        """
        通过判断上次发状态时间与当前时间间隔决定是否可以发状态
        :return:
        """
        if self.last_add_friend_time:
            dt_last_add = datetime.strptime(self.last_add_friend_time, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - dt_last_add).total_seconds() < self.add_friend_interval:
                logger.warning('Less than {} seconds before the last add friend, last add friend at: {}'.format(self.add_friend_interval, self.last_add_friend_time))
                return False

        return True

    def is_account_valid(self):
        """
        判断账号是否可用
        :return:
        """
        return self.account_status != 'invalid'

    def is_in_verifying(self):
        """
        通过判断上次提交验证时间与当前时间间隔决定账号是否还在验证中
        :return:
        """
        if self.last_verifying_time:
            dt_last_verify = datetime.strptime(self.last_verifying_time, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - dt_last_verify).total_seconds() < self.verify_interval:
                logger.warning(logger.error('Less than {} seconds before the last verify, last verify at: {}'.format(self.verify_interval, self.last_verifying_time)))
                return True

        return False

    def get_friend_keys(self, limit=1):
        """
        获取好友关键字
        :param limit: 关键字数量
        :return: list
        """
        if self.is_add_friend:
            fks = self.friend_keys.split(';')
            if fks:
                return fks
            else:
                return get_fb_friend_keys(limit)
        else:
            return []

    def get_posts(self, force=False):
        """
        获取要发布的状态
        :return: 字典
        """
        if force:
            return get_fb_posts(1)

        if self.is_post:
            if self.post_content:
                return {'post': self.post_content, 'img': []}
            else:
                return get_fb_posts(1)
        else:
            return {}

    def get_chat_msgs(self, limit=1):
        """
        获取聊天内容
        :param limit: 聊天条数
        :return: list
        """
        if self.is_chat:
            if self.chat_content:
                return self.chat_content.split(';')
            else:
                return get_fb_chat_msgs(limit)
        else:
            return []

    def random_sleep(self, lower=3, upper=10):
        """
        随机休眠
        :param lower: 最短休眠时间
        :param upper: 最长休眠时间
        :return:
        """
        if lower <= 0 or upper <= 0:
            return False

        if lower == upper:
            time.sleep(lower)
            return True

        if lower > upper:
            tmp = lower
            lower = upper
            upper = tmp

        rdn = random.randint(0, 10000)
        slt = rdn % upper + 1
        slt = lower if slt < lower else slt
        time.sleep(slt)
        return True

    def random_select(self):
        rdn = random.randint(0, 10000)
        if rdn % 2 == 0:
            return True

        return False

    def screenshots(self, driver, err_code=-1, force=False):
        if self.headless or force:
            try:
                screenshots_dir = get_system_args()['screenshots_dir']
                if not os.path.isdir(screenshots_dir):
                    os.mkdir(screenshots_dir)

                # 先删除5天前的截图，以免服务器磁盘超负荷
                photos = os.listdir(screenshots_dir)
                time_limit = (datetime.now() - timedelta(days=get_system_args()['screenshots_keep'])).strftime("%Y-%m-%d_%H_%M_%S")
                for ph in photos:
                    if ph[0:19] < time_limit:
                        os.remove("{}//{}".format(screenshots_dir, ph))

                path = "{}//{}_{}_{}_{}.png".format(screenshots_dir, datetime.now().strftime("%Y-%m-%d_%H_%M_%S"), self.account, self.password, err_code)
                logger.info("save screenshots, path={}".format(path))
                driver.get_screenshot_as_file(path)
            except Exception as e:
                logger.exception('screenshots exception={}'.format(e))

    def make_result(self, ret=False, err_code=-1, err_msg='', last_login=None, last_post=None, last_chat=None,
                    last_farming=None, last_comment=None, last_edit=None, last_verify=None, last_add_friend=None,
                    phone_number='', profile_path='', **kwargs):
        task_result = {
            'status': 'failed',  # 'failed', 'succeed'
            'err_msg': '',
            'account_status': '',  # valid, invalid, verifying
            'account_configure': {}
        }

        if ret:
            task_result['status'] = 'succeed'
        else:
            task_result['status'] = 'failed'
            account_status = fb.FacebookException.MAP_EXP_PROCESSOR.get(err_code, {}).get('account_status', '')  # valid, invalid, verifying
            task_result['account_status'] = account_status
            if 'verifying' in account_status and not last_verify:
                last_verify = datetime.now()

            task_result['err_msg'] = err_msg if err_msg else 'err_code={}'.format(err_code)

        task_result['account_configure'] = {
            'last_login': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_login, datetime) else '',
            'last_post': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_post, datetime) else '',
            'last_chat': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_chat, datetime) else '',
            'last_farming': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_farming, datetime) else '',
            'last_comment': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_comment, datetime) else '',
            'last_edit': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_edit, datetime) else '',
            'last_verify': last_verify.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_verify, datetime) else '',
            'last_add_friend': last_add_friend.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_add_friend, datetime) else '',
            'phone_number': phone_number,
            'profile_path': profile_path,
        }

        for k, v in kwargs.items():
            task_result['account_configure'][k] = v

        return task_result


if __name__ == '__main__':
    inputs = {
        'task': {
            'task_id': 1234,
            'configure': {},
        },
        'account': {
            'account': "abc@gmail.com",
            'password': "password",
            'email': '',
            'email_pwd': '',
            'gender': 0,
            'phone_number': "13991623651",
            'birthday': "1999-03-15",
            'national_id': '',
            'name': '',
            'active_area': 'China',
            'active_browser': {'device': 'iPhone 6'},
            'profile_path': '',
            'configure': {'last_login': '2019-04-20 19:20:20', 'last_verify': '2019-04-20 19:20:20'}
        }
    }

    th = TaskHelper(inputs)
    print(th.get_posts(True))
    th.is_in_verifying()