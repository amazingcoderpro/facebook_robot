#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-18
# Function:

import sys
import time
from apscheduler.schedulers.background import BackgroundScheduler
from config import logger
from api import clean_environment, update_results, start_all_new_tasks, restart_all_tasks

g_bk_scheduler = BackgroundScheduler()


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


def run(mode='new', update_interval=30):
    """
    启动任务调度系统
    :param mode: 'new':清空缓存,从头开始； 'restart': 则继续上一次结束点开始, 之前未处理完的任务将继续被执行
    :param update_interval: 结果更新周期,默认30秒
    :return:
    """
    try:
        logger.info('----------------Start Task Scheduler System.--------------------')
        bk_scheduler = BackgroundScheduler()
        if mode == 'restart':
            # restart模式会将之前所有没有结束的任务重新拉起执行
            restart_all_tasks(bk_scheduler)
        else:
            # new模式只会启动状态为new的任务, 默认
            logger.info('clean environment. ')
            clean_environment()
            start_all_new_tasks(bk_scheduler)

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
    logger.info('start command={}'.format(sys.argv))
    mode = 'restart'
    interval = 60
    if len(sys.argv) > 2:
        mode = sys.argv[1]
        try:
            interval = int(sys.argv[2])
        except:
            pass
    elif len(sys.argv) > 1:
        mode = sys.argv[1]

    run(mode=mode, update_interval=interval)

# pipenv run python3 main.py [new|restart] [30]

    # dispatch_test()
"""
update facebook.task set status='new' where id>0;
update facebook.task set failed_counts=0 where id>0;
update facebook.task set succeed_counts=0 where id>0;
update facebook.task set start_time=null where id>0;
update facebook.task set end_time=null where id>0;
"""
