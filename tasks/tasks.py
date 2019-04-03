#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 养号任务入口

import time
import random
from .workers import app
import scripts
from celery import Task
from config import logger


class BaseTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error('celery task on_failed, task_id={}, args={}, kwargs={}, exception={}, exception info={}. '
                     .format(task_id, args, kwargs, exc, einfo))

        # self.update_state(task_id=task_id, state='failed', meta={'exc': exc, 'einfo': einfo, 'args': args, 'kwargs': kwargs, 'tt':123})
        # JobOpt.set_job_by_track_id(task_id, status='failed', result=str(exec), traceback=str(einfo))

    def on_success(self, retval, task_id, args, kwargs):
        logger.info('celery task on_success, task_id={}, retval={}. '.format(task_id, retval))
        # self.update_state(task_id=task_id, state='succeed', meta={'retval': retval, 'args': args, 'kwargs':kwargs, 'tt':456})
        # JobOpt.set_job_by_track_id(task_id, status='succeed', result=str(retval))


# 处理beat的定时任务, 暂不用
# @app.task(ignore_result=True)
# def execute_fb_auto_feed():
#     inputs = {}
#     app.send_task('tasks.tasks.fb_auto_feed', args=(inputs,),
#                   queue='feed_account', routing_key='for_feed_account')


@app.task(base=BaseTask, bind=True, max_retries=1, time_limit=300)
def fb_auto_feed(self, inputs):
    logger.info('fb_auto_feed task running')

    # time.sleep(3)
    # 更新任务状态为running
    # self.update_state(state="running")

    # do something here
    time.sleep(60)

    a = random.randint(1, 100)
    if a % 3 == 1:
        return {'status': 'failed', 'err_msg': 'auto feed 3-1 failed'}
    if a % 2 == 0:
        logger.exception('fb_auto_feed')
        a = a/0

    return {'status': 'succeed', 'err_msg': 'auto feed good.'}

    try:
        # 执行任务
        res = scripts.auto_feed(inputs)
    except Exception as e:
        logger.exception('fb_auto_feed catch exception.')
        self.retry(countdown=10 ** self.request.retries)

    return 1


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

