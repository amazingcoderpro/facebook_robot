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
from config import logger, get_account_args, get_fb_friend_keys
import scripts.facebook as fb
from util.task_help import make_result, TaskHelper


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


@app.task(base=BaseTask, bind=True, max_retries=1, time_limit=1200)
def fb_auto_feed(self, inputs):
    logger.info('----------fb_auto_feed task running, inputs=\r\n{}'.format(inputs))
    try:
        driver = None
        last_login = None
        tsk_hlp = TaskHelper(inputs)

        if not tsk_hlp.is_inputs_valid():
            logger.error('inputs not valid, inputs={}'.format(inputs))
            return make_result(err_msg='inputs invalid.')

        if not tsk_hlp.is_should_login():
            logger.warning('is_should_login return False, task id={}, account={}'.format(tsk_hlp.task_id, tsk_hlp.account))
            return make_result(err_msg='is_should_login return False')

        if tsk_hlp.is_in_verifying():
            logger.warning('is_in_verifying return True, task id={}, account={}'.format(tsk_hlp.task_id, tsk_hlp.account))
            return make_result(err_msg='is_in_verifying return True')

        # 分步执行任务
        # 启动浏览器
        driver, err_msg = fb.start_chrome(finger_print=tsk_hlp.active_browser, headless=True)
        if not driver:
            msg = 'start chrome failed. err_msg={}'.format(err_msg)
            logger.error(msg)
            return make_result(err_msg=err_msg)

        account = tsk_hlp.account
        password = tsk_hlp.password
        ret, err_code = fb.auto_login(driver=driver, account=account, password=password, gender=tsk_hlp.gender)
        if not ret:
            msg = 'login failed, account={}, password={}, err_code={}'.format(account, password, err_code)
            logger.error(msg)
            return make_result(err_code=err_code, err_msg=err_msg, last_verify=datetime.datetime.now())

        last_login = datetime.datetime.now()

        logger.info('login succeed. account={}, password={}'.format(account, password))
        ret, err_code = fb.user_messages(driver=driver)
        if not ret:
            msg = 'user_messages, account={}, err_code={}'.format(account, err_code)
            logger.error(msg)
            return make_result(err_code=err_code, err_msg=err_msg, last_verify=datetime.datetime.now())

        tsk_hlp.random_sleep()
        if tsk_hlp.random_select():
            ret, err_code = fb.local_surface(driver=driver)
            if not ret:
                err_msg = 'local_surface failed, err_code={}'.format(err_code)
                return make_result(err_code=err_code, err_msg=err_msg, last_verify=datetime.datetime.now())

        tsk_hlp.random_sleep()
        fks = tsk_hlp.get_friend_keys(1)
        if fks:
            ret, err_code = fb.add_friends(driver, search_keys=fks, limit=random.randint(1, 3))
            if not ret:
                err_msg = 'add_friends failed, err_code={}'.format(err_code)
                return make_result(err_code=err_code, err_msg=err_msg, last_verify=datetime.datetime.now())

        tsk_hlp.random_sleep(20, 100)
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


@app.task(base=BaseTask, bind=True, max_retries=3, time_limit=300)
def switch_vps_ip(self, inputs):
    logger.info('--------switch_vps_ip')
    try:
        subprocess.call("pppoe-stop", shell=True)
        # subprocess.Popen('pppoe-stop', shell=True, stdout=subprocess.PIPE, encoding='utf8')
        time.sleep(3)
        subprocess.call('pppoe-start', shell=True)
        time.sleep(3)
        pppoe_restart = subprocess.Popen('pppoe-status', shell=True, stdout=subprocess.PIPE)
        pppoe_restart.wait(timeout=5)
        pppoe_log = str(pppoe_restart.communicate()[0])
        adsl_ip = re.findall(r'inet (.+?) peer ', pppoe_log)[0]
        logger.info('switch_vps_ip succeed. New ip address : {}'.format(adsl_ip))
    except Exception as e:
        err_msg = 'switch_vps_ip catch exception={}'.format(str(e))
        logger.exception(err_msg)
        return make_result(err_msg=err_msg)

    logger.info('')
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

