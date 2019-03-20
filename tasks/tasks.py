#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 养号任务入口


import datetime
from .workers import app
import scripts
from db.dao import JobOpt, AccountOpt


# @app.task(ignore_result=True)
@app.task
def fb_auto_feed(task_id, account_id, agent_id):
    print("execute fb_auto_feed task id={}, account id ={}".format(task_id, account_id))
    job = JobOpt.save_job(task_id, account_id, agent_id=agent_id, status='running', start_time=datetime.datetime.now())

    # 执行任务
    res = scripts.auto_feed(AccountOpt.get_account(account_id))

    # 更新job状态
    job.status = res[0]
    job.result = res[1]

    return res


# 处理beat的定时任务, 暂不用
@app.task(ignore_result=True)
def execute_fb_auto_feed():
    task_id, account_id = "", ""
    app.send_task('tasks.tasks.fb_auto_feed', args=(task_id, account_id),
                  queue='feed_account', routing_key='for_feed_account')



