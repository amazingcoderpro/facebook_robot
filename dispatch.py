#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-18
# Function:


import time
from apscheduler.schedulers.background import BackgroundScheduler
from db.dao import TaskOpt, TaskAccountGroupOpt, TaskCategoryOpt, SchedulerOpt
from tasks.processor import *

scheduler = BackgroundScheduler()


def schedule_job(task_id, account_id, processor):

    task_sch = SchedulerOpt.get_scheduler(TaskOpt.get_task(task_id).scheduler)

    # 根据任务计划模式的不同启动不同的定时任务
    # 执行模式：
    # 0 - 立即执行（只执行一次）， 1 - 间隔执行并不立即开始（间隔一定时间后开始执行，并按设定的间隔周期执行下去）
    # 2 - 间隔执行，但立即开始， 3 - 定时执行，指定时间执行
    processor_func = eval(processor)
    if task_sch.mode == 0:
        aps_job = scheduler.add_job(processor_func, args=(task_id, account_id))
    elif task_sch.mode == 1:
        processor_func(task_id, account_id)
        aps_job = scheduler.add_job(processor_func, 'interval', seconds=task_sch.interval, args=(task_id, account_id))
    elif task_sch.mode == 2:
        processor_func(task_id, account_id)
        aps_job = scheduler.add_job(processor_func, 'interval', seconds=task_sch.interval, args=(task_id, account_id))
    elif task_sch.mode == 3:
        print("date task...")
        aps_job = scheduler.add_job(processor_func, 'date', run_date=task_sch.date, args=(task_id, account_id))

    # 将aps id 更新到数据库中, aps id 将用于任务的暂停、恢复
    TaskAccountGroupOpt.set_aps_id(task_id, account_id, aps_job.id)

    # 一旦任务被加入到定时程序中，即使没有立即执行，但任务的状也是running, 代表也已经在处理中了
    TaskOpt.set_task_status(task_id, 'running')

    print(TaskAccountGroupOpt.get_aps_ids_by_task(task_id))

    return True


def insert_tasks(tasks):
    for task in tasks:
        task_processor = TaskCategoryOpt.get_processor(task.category)
        if not task_processor:
            continue

        for account in task.accounts:
            schedule_job(task.id, account.id, task_processor)


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


def run():
    try:
        scheduler.start()
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == '__main__':
    tasks = TaskOpt.get_all_need_restart_task()
    insert_tasks(tasks)
    run()
