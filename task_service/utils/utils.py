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
    env = 'pro'                 # pro/test
    task_start_mode = 'new'     # new/restart
    if len(sys.argv) >= 3:
        env = sys.argv[1]
        task_start_mode = sys.argv[2]
    elif len(sys.argv) == 2:
        env = sys.argv[1]
    else:
        input_env = input("Please input task execute environment(pro/test):")
        if input_env and input_env in ["pro", "test"]:
            env = input_env

        input_mode = input("Please input task start mode(new/restart):")
        if input_mode and input_mode in ["new", "restart"]:
            task_start_mode = input_mode

    load_config(env)
    interval = get_task_args()['update_interval']
    logger.info("---Task module start args: env={}, task_start_mode={}, update_interval={}".format(env, task_start_mode, interval))
    return env, task_start_mode, interval
