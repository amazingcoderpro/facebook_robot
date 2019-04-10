#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 养号任务入口

import time
import random
from .workers import app
from celery import Task
from config import logger
import subprocess
import time
import re
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

TaskResult = {
    'status': 'failed',        # 'failed', 'succeed'
    'err_msg': '',
    'account_status': '',  # valid, invalid, verifying
    'account_configure': {}         # {
    #     'last_post': '',
    #     'last_login': '',
    #     'last_chat': '',
    #     'last_farming': '',
    #     'last_comment': '',
    #     'last_edit': '',
    #     'phone_number': '',
    #     'profile_path': ''
    # }
}

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


@app.task(base=BaseTask, bind=True, max_retries=1, time_limit=1200)
def fb_auto_feed(self, inputs):
    logger.info('----------fb_auto_feed task running, inputs=\r\n{}'.format(inputs))
    logger.info(inputs)
    try:
        driver = None
        account = inputs.get('account')
        account_ = account.get('account')
        # account = inputs['account']['account']
        password = account.get('password')
        active_browser = account.get("active_browser")
        account_configure = account.get("account_configure", {})

        # 分步执行任务
        driver = fb.start_chrom(finger_print=active_browser)

        if not driver:
            TaskResult['err_msg'] = 'start chrome failed. driver is None'
            return TaskResult

        ret = fb.auto_login(driver=driver, account=account_, password=password)
        if not ret:
            TaskResult['err_msg'] = 'login failed.'
            return TaskResult

        time.sleep(10)
        ret, status = fb.user_messages(driver=driver)
        if not ret:
            TaskResult['err_msg'] = 'login failed.'
            TaskResult['account_status'] = fb.FacebookException.MAP_EXP_PROCESSOR.get(status, {}).get('account_status', 'valid')
            return TaskResult

        time.sleep(10)
        fb.local_surface(driver=driver)
        TaskResult['status'] = 'succeed'
        TaskResult['account_configure'] = account_configure
        return TaskResult
    except Exception as e:
        logger.exception('fb_auto_feed catch exception.')
        # self.retry(countdown=10 ** self.request.retries)
        TaskResult['status'] = 'failed'
        TaskResult['err_msg'] = str(e)
    finally:
        print(dir(driver))
        if driver:
            driver.quit()
    return TaskResult


@app.task(base=BaseTask, bind=True, max_retries=1, time_limit=300)
def change_ip_vps(self, inputs):
    logger.info('----------fb_auto_feed task running, inputs=\r\n{}'.format(inputs))
    logger.info(inputs)
    try:
        subprocess.call("pppoe-stop", shell=True)
        # subprocess.Popen('pppoe-stop', shell=True, stdout=subprocess.PIPE, encoding='utf8')
        time.sleep(2)
        subprocess.call('pppoe-start', shell=True)
        time.sleep(2)
        pppoe_restart = subprocess.call('pppoe-status', shell=True)
        pppoe_restart.wait()
        pppoe_log = pppoe_restart.communicate()[0]
        adsl_ip = re.findall(r'inet (.+?) peer ', pppoe_log)[0]
        print('[*] New ip address : ' + adsl_ip)
        # return True
        TaskResult['status'] = 'success'
        return TaskResult
    except Exception as e:
        TaskResult['err_msg'] = str(e)

        # change_ip_for_vps()
    return TaskResult


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

    return {'status': 'succeed', 'err_msg': 'click farming good'}


# from celery import chain, signature
# r = chain(fb_auto_feed.s({}), fb_click_farming.s({}))
# r.apply_async()

