#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-04-16
# Function: 

import sys
from config import logger, load_config, get_task_args


def parse_args():
    """
    解析命令行参数
    :return:
    """
    logger.info('start command={}'.format(sys.argv))
    env = 'pro'        # new/restart
    task_start_mode = 'new'
    if len(sys.argv) >= 3:
        env = sys.argv[1]
        task_start_mode = sys.argv[2]
    elif len(sys.argv) == 2:
        env = sys.argv[1]

    load_config(env)
    interval = get_task_args()['update_interval']
    logger.info("start args: env={}, task_start_mode={}, update_interval={}".format(env, task_start_mode, interval))
    return env, task_start_mode, interval
