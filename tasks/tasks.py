#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 养号任务入口

import time
import datetime
import random
import subprocess
import re
from celery import Task
from .workers import app
from config import logger, get_account_args
import scripts.facebook as fb


class BaseTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error('celery task on_failed, task_id={}, args={}, kwargs={}, exception={}, exception info={}. '
                     .format(task_id, args, kwargs, exc, einfo))

    def on_success(self, retval, task_id, args, kwargs):
        logger.info('celery task on_success, task_id={}, retval={}. '.format(task_id, retval))


# 处理beat的定时任务, 暂不用
# @app.task(ignore_result=True)
# def execute_fb_auto_feed():
#     inputs = {}
#     app.send_task('tasks.tasks.fb_auto_feed', args=(inputs,),
#                   queue='feed_account', routing_key='for_feed_account')


# inputs = {
#     'task': {
#         'task_id': task_id,
#         'configure': json.loads(task_configure) if task_configure else {},
#     },
#     'account': {
#         'account': account,
#         'password': password,
#         'email': email,
#         'email_pwd': email_pwd,
#         'gender': gender,
#         'phone_number': phone_number,
#         'birthday': birthday,
#         'national_id': national_id,
#         'name': name,
#         'active_area': active_area,
#         'active_browser': active_browser,
#         'profile_path': profile_path,
#         'configure': json.loads(account_configure) if account_configure else {}
#     }
# }


def make_result(ret=False, err_code=-1, err_msg='', last_login=None, last_post=None, last_chat=None, last_farming=None,
                last_comment=None, last_edit=None, phone_number='', profile_path=''):
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
        account_status = fb.FacebookException.MAP_EXP_PROCESSOR.get(err_code, {}).get('account_status', '')    # valid, invalid, verifying
        task_result['account_status'] = account_status
        task_result['err_msg'] = err_msg if err_msg else 'err_code={}'.format(err_code)

    task_result['account_configure'] = {
        'last_login': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_login, datetime.datetime) else '',
        'last_post': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_post, datetime.datetime) else '',
        'last_chat': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_chat, datetime.datetime) else '',
        'last_farming': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_farming, datetime.datetime) else '',
        'last_comment': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_comment, datetime.datetime) else '',
        'last_edit': last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_edit, datetime.datetime) else '',
        'phone_number': phone_number,
        'profile_path': profile_path,
    }

    return task_result


@app.task(base=BaseTask, bind=True, max_retries=1, time_limit=1200)
def fb_auto_feed(self, inputs):
    logger.info('----------fb_auto_feed task running, inputs=\r\n{}'.format(inputs))
    try:
        driver = None
        last_login = None
        account_info = inputs.get('account', None)
        if not isinstance(account_info, dict):
            logger.error('inputs not valid.')
            return make_result(err_msg='inputs not valid.')

        account = account_info.get('account')
        password = account_info.get('password')
        active_browser = account_info.get("active_browser")
        account_configure = account_info.get("account_configure", {})
        last_login_time = account_configure.get('last_login', '')
        if last_login_time:
            dt_last_login = datetime.strptime(last_login_time, "%Y-%m-%d %H:%M:%S")
            if (datetime.datetime.now() - dt_last_login).total_seconds() < get_account_args().get('login_interval', 3600):
                err_msg = 'Less than an hour before the last login, last login={}'.format(last_login_time)
                logger.error(err_msg)
                return make_result(err_msg=err_msg)

        # 分步执行任务
        # 启动浏览器
        driver, err_msg = fb.start_chrome(finger_print=active_browser, headless=False)
        if not driver:
            msg = 'start chrome failed. err_msg={}'.format(err_msg)
            logger.error(msg)
            return make_result(err_msg=err_msg)

        ret, err_code = fb.auto_login(driver=driver, account=account, password=password, gender=account_info.get('gender', 1))
        if not ret:
            msg = 'login failed, account={}, password={}, err_code={}'.format(account, password, err_code)
            logger.error(msg)
            return make_result(err_code=err_code, err_msg=err_msg)

        last_login = datetime.datetime.now()

        logger.info('login succeed. account={}, password={}'.format(account, password))
        random_num = random.randint(0, 100)
        if random_num/2 == 0 or random_num / 3 == 0:
            ret, err_code = fb.user_messages(driver=driver)
            if not ret:
                msg = 'user_messages, account={}, err_code={}'.format(account, err_code)
                logger.error(msg)
                return make_result(err_code=err_code, err_msg=err_msg)

        time.sleep(random_num % 5)
        if random_num / 2 != 0 or random_num / 3 == 0:
            ret, err_code = fb.local_surface(driver=driver)
            if not ret:
                err_msg = 'local_surface failed, err_code={}'.format(err_code)
                return make_result(err_code=err_code, err_msg=err_msg)

        time.sleep(60)
        logger.info('task fb_auto_feed succeed. account={}'.format(account))
    except Exception as e:
        err_msg = 'fb_auto_feed catch exception. e={}'.format(str(e))
        logger.exception(err_msg)
        # self.retry(countdown=10 ** self.request.retries)
        return make_result(err_msg=err_msg)
    finally:
        if driver:
            driver.quit()
    return make_result(True, last_login=last_login)


@app.task(base=BaseTask, bind=True, max_retries=1, time_limit=300)
def switch_vps_ip(self, inputs):
    logger.info('switch_vps_ip')
    try:
        subprocess.call("pppoe-stop", shell=True)
        # subprocess.Popen('pppoe-stop', shell=True, stdout=subprocess.PIPE, encoding='utf8')
        time.sleep(3)
        subprocess.call('pppoe-start', shell=True)
        time.sleep(3)
        pppoe_restart = subprocess.call('pppoe-status', shell=True)
        pppoe_restart.wait()
        pppoe_log = pppoe_restart.communicate()[0]
        adsl_ip = re.findall(r'inet (.+?) peer ', pppoe_log)[0]
        logger.info('[*] New ip address : ' + adsl_ip)
    except Exception as e:
        err_msg = 'switch_vps_ip catch exception={}'.format(str(e))
        logger.error(err_msg)
        return make_result(err_msg=err_msg)

    return make_result(ret=True)


@app.task(base=BaseTask, bind=True, max_retries=1, time_limit=300)
def fb_click_farming(self, inputs):
    logger.info('fb_click_farming task running')

    # time.sleep(3)
    # 更新任务状态为running
    # self.update_state(state="running")

    # do something here
    time.sleep(70)

    a = random.randint(1, 100)
    if a % 3 == 2:
        return {'status': 'failed', 'err_msg': 'click farming 3-2 failed'}

    if a % 3 == 1:
        logger.exception('fb_auto_feed')
        a = a/0

    return make_result(ret=True)


# from celery import chain, signature
# r = chain(fb_auto_feed.s({}), fb_click_farming.s({}))
# r.apply_async()

