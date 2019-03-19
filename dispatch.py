#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-18
# Function:


import time
from apscheduler.schedulers.background import BackgroundScheduler
from tasks.feed_account import schedule_feed_account
from db.dao import TaskOpt, TaskAccountGroupOpt
from db.models import Job

scheduler = BackgroundScheduler()

TASK_MAP = {0: schedule_feed_account, 1: schedule_feed_account}


def schedule_job(task, account, func):
    # 先构建Job
    job = Job()
    job.task = task.id
    job.account = account.account
    job.password = account.password
    task_sch = TaskOpt.get_task_scheduler(task.id)
    if task_sch.category == 0:
        aps_job = scheduler.add_job(func, args=(task.id, account.account, account.password))
    elif task_sch.category == 1:
        aps_job = scheduler.add_job(func, 'interval', seconds=task_sch.interval, args=(task.id, account.account, account.password))
    elif task_sch.category == 2:
        func(task.id, account.account, account.password)
        aps_job = scheduler.add_job(func, 'interval', seconds=task_sch.interval, args=(task.id, account.account, account.password))
    elif task_sch.category == 3:
        print("date task...")
        aps_job = scheduler.add_job(func, 'date', run_date=task_sch.date, args=(task.id, account.account, account.password))

    # 将aps id 更新到数据库中
    TaskAccountGroupOpt.set_aps_id(task.id, account.id, aps_job.id)
    print(TaskAccountGroupOpt.get_aps_ids_by_task(task.id))


def main():
    try:
        scheduler.start()
        tasks = TaskOpt.get_all_need_restart_task()
        for task in tasks:
            print("process feed account task.")
            for account in task.accounts:
                schedule_job(task, account, TASK_MAP.get(task.category))

        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


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


if __name__ == '__main__':
    main()
