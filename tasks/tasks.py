#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 养号任务入口

import time
from .workers import app
import scripts


@app.task(bind=True)
def fb_auto_feed(self, inputs):
    # 更新任务状态为running
    self.update_state(state="running")

    # 执行任务
    res = scripts.auto_feed(inputs)

    self.update_state(state="succeed", meta={'result': res})
    return res


# 处理beat的定时任务, 暂不用
@app.task(ignore_result=True)
def execute_fb_auto_feed():
    inputs = {}
    app.send_task('tasks.tasks.fb_auto_feed', args=(inputs, ),
                  queue='feed_account', routing_key='for_feed_account')


@app.task(bind=True)
def fb_click_farming(self, inputs):
    self.update_state(state="running")

    # 执行任务
    time.sleep(2)
    self.update_state(state="succeed", meta={'progress': 100})


@app.task(bind=True)
def fb_login(self, inputs):
    self.update_state(state="running")

    # 执行任务
    time.sleep(2)
    self.update_state(state="succeed", meta={'progress': 100})
