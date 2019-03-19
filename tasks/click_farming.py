#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 刷好评任务入口


from .workers import app
# from service import feed_account


# @app.task(ignore_result=True)
@app.task
def click_farming(account, password, ads_code):
    print(locals())
