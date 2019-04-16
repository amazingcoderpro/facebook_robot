#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-18
# Function:

import sys
import time
from apscheduler.schedulers.background import BackgroundScheduler
from config import logger
from utils.utils import parse_args
env, task_start_mode, interval = parse_args()
from api import clean_environment, update_results, start_all_new_tasks, restart_all_tasks


def dispatch_test():
    import time
    from tasks.workers import app
    account_list = [("eddykkqf56@outlook.com", "nYGcEXNjGY")]
    for i in range(3):
        for acc in account_list:
            app.send_task('tasks.feed_account.feed_account',
                          args=(acc[0], acc[1]),
                          queue='feed_account_queue',
                          routing_key='for_feed_account')
        time.sleep(600)


def run(task_start_mode='new', update_interval=30):
    """
    启动任务调度系统
    :param task_start_mode: 'new':清空缓存,从头开始； 'restart': 则继续上一次结束点开始, 之前未处理完的任务将继续被执行
    :param update_interval: 结果更新周期,默认30秒
    :return:
    """
    try:
        logger.info('----------------Start Task Scheduler System. task_start_mode={}, interval={}--------------------'.format(task_start_mode, update_interval))
        bk_scheduler = BackgroundScheduler()
        print(id(bk_scheduler))
        if task_start_mode == 'restart':
            # restart模式会将之前所有没有结束的任务重新拉起执行
            restart_all_tasks(scheduler=bk_scheduler)
        else:
            # new模式只会启动状态为new的任务, 默认
            logger.info('clean environment. ')
            clean_environment()
            start_all_new_tasks(scheduler=bk_scheduler)

        # 启动定时结果更新
        bk_scheduler.add_job(update_results, 'interval', seconds=update_interval, misfire_grace_time=20, max_instances=5)
        bk_scheduler.start()

        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        bk_scheduler.shutdown()
        logger.warning('Scheduler have been stopped.')
    finally:
        if bk_scheduler.running:
            bk_scheduler.shutdown()
    logger.info('-------------------Stop Task Scheduler System.-------------------')


if __name__ == '__main__':
    run(task_start_mode=task_start_mode, update_interval=interval)

# pipenv run python3 main.py [test|pro] [new|restart]
# eg: python3 main.py test new

