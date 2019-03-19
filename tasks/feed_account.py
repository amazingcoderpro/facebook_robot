#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 养号任务入口


import datetime
from .workers import app
import service
from db.dao import JobOpt


# @app.task(ignore_result=True)
@app.task
def feed_account(task_id, account):
    print("execute task task id={}, account={}".format(task_id, account.account))
    job = JobOpt.save_job(task_id, account.id, status=2, start_time=datetime.datetime.now())

    # 执行任务
    res = service.feed_account(account)

    # 更新job状态
    job.status = res[0]
    job.result = res[1]

    return res


# 处理beat的定时任务, 暂不用
@app.task(ignore_result=True)
def execute_feed_account():
    task_id, account, password = "", "", ""
    app.send_task('tasks.feed_account.feed_account', args=(account, password, ),
                  queue='feed_account', routing_key='for_feed_account')


def schedule_feed_account(task_id, account):
    print("{} send task: task_id:{} account:{} ".format(datetime.datetime.now(), task_id, account.account))
    app.send_task('tasks.feed_account.feed_account',
                  args=(task_id, account),
                  queue='feed_account_queue',
                  routing_key='for_feed_account')
