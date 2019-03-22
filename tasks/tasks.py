#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 养号任务入口

import time
from .workers import app
import scripts
from celery import Task
from config import logger
from db.dao import JobOpt

class BaseTask(Task):
    # @classmethod
    # def on_bound(cls, app):
    #     logger.info('task is bound')
    #     pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error('celery task on_failed, task_id={}, exception={}, exception info={}. '.format(task_id, exc, einfo))
        JobOpt.set_job_by_track_id(task_id, status='failed', result=str(exec), traceback=str(einfo))

    def on_success(self, retval, task_id, args, kwargs):
        logger.info('celery task on_success, task_id={}, retval={}. '.format(task_id, retval))
        JobOpt.set_job_by_track_id(task_id, status='succeed', result=str(retval))


@app.task(base=BaseTask, bind=True, max_retries=2, time_limit=30)
def fb_auto_feed(self, inputs):
    # 更新任务状态为running
    # self.update_state(state="running")
    time.sleep(3)
    try:
        # 执行任务
        res = scripts.auto_feed(inputs)
    except Exception as e:
        logger.exception('fb_auto_feed catch exception.')
        self.retry(countdown=10 ** self.request.retries)

    # self.update_state(state="succeed", meta={'result': res})
    return res


# 处理beat的定时任务, 暂不用
@app.task(ignore_result=True)
def execute_fb_auto_feed():
    inputs = {}
    app.send_task('tasks.tasks.fb_auto_feed', args=(inputs,),
                  queue='feed_account', routing_key='for_feed_account')


@app.task(base=BaseTask)
def fb_click_farming(inputs):
    # 执行任务
    time.sleep(2)
    return 1


@app.task(bind=True)
def fb_login(self, inputs):
    self.update_state(state="running")

    # 执行任务
    time.sleep(2)
    self.update_state(state="succeed", meta={'progress': 100})
