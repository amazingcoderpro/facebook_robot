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
def feed_account(task_id, account, password, to_post=False):
    print("execute task")
    job = JobOpt.save_job(task_id, account, password, status=2, start_time=datetime.datetime.now())
    res = service.feed_account(account, password, to_post)
    if res:
        job.status = 1
    else:
        job.status = 0


# 处理beat的定时任务, 暂不用
@app.task(ignore_result=True)
def execute_feed_account():
    task_id, account, password = "", "", ""
    app.send_task('tasks.feed_account.feed_account', args=(account, password, ),
                  queue='feed_account', routing_key='for_feed_account')


def schedule_feed_account(task_id, account, password):
    print("{} send task: task_id:{} account:{}, password:{}".format(datetime.datetime.now(), task_id, account, password))
    app.send_task('tasks.feed_account.feed_account',
                  args=(task_id, account, password),
                  queue='feed_account_queue',
                  routing_key='for_feed_account')
