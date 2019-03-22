#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-18
# Function:


import time
from apscheduler.schedulers.background import BackgroundScheduler
from db.dao import TaskOpt, TaskAccountGroupOpt, TaskCategoryOpt, SchedulerOpt, AgentOpt
from tasks.processor import dispatch_processor
from config import logger

scheduler = BackgroundScheduler()


def schedule_job(scheduler_id, processor, inputs):

    task_sch = SchedulerOpt.get_scheduler(scheduler_id)

    # 根据任务计划模式的不同启动不同的定时任务
    # 执行模式：
    # 0 - 立即执行（只执行一次）， 1 - 间隔执行并不立即开始（间隔一定时间后开始执行，并按设定的间隔周期执行下去）
    # 2 - 间隔执行，但立即开始， 3 - 定时执行，指定时间执行
    dispatch_processor(processor, inputs)
    if task_sch.mode == 0:
        aps_job = scheduler.add_job(dispatch_processor, args=(processor, inputs))
    elif task_sch.mode == 1:
        aps_job = scheduler.add_job(dispatch_processor, 'interval', seconds=task_sch.interval, args=(processor, inputs))
    elif task_sch.mode == 2:
        dispatch_processor(processor, inputs)
        aps_job = scheduler.add_job(dispatch_processor, 'interval', seconds=task_sch.interval, args=(processor, inputs))
    elif task_sch.mode == 3:
        aps_job = scheduler.add_job(dispatch_processor, 'date', run_date=task_sch.date, args=(processor, inputs))

    return aps_job


def find_optimal_agent(account, agents=None):
    if not agents:
        agents = AgentOpt.get_enable_agents()
        if not agents:
            return None

    if account.active_ip:
        for agent in agents:
            if account.ip == agent.ip:
                return agent
    elif account.active_area:
        for agent in agents:
            if account.active_area == agent.area:
                return agent
    else:
        return agents[0]


def insert_tasks(tasks):
    for task in tasks:
        task_id = task.id
        task_configure = task.configure
        task_processor = TaskCategoryOpt.get_processor(task.category)
        scheduler_id = task.scheduler
        agents = AgentOpt.get_enable_agents(status_order=True)
        # 每一个类型的任务都对应一个处理器
        if not task_processor:
            continue

        # 一旦任务被加入到定时程序中，即等待分发执行
        TaskOpt.set_task_status(task_id, 'pending')

        # 一个任务会有多个账号， 按照账号对任务进行第一次拆分，针对每一个账号，启动一个定时任务，这样任务管理粒度更细，也更符合实际情况
        for account in task.accounts:
            agent = find_optimal_agent(account=account, agents=agents)
            if not agent:
                continue

            # 构建任务执行必备参数
            inputs = {
                'task_id': task_id,
                'account_id': account.id,
                'agent_id': agent.id,
                'account': account.account,
                'password': account.password,
                'agent_queue_name': agent.queue_name,
                'task_configure': task_configure
            }

            aps_job = schedule_job(scheduler_id=scheduler_id, processor=task_processor, inputs=inputs)

            # 将aps id 更新到数据库中, aps id 将用于任务的暂停、恢复
            TaskAccountGroupOpt.set_aps_info(task_id, account.id, aps_job.id,)#next_run_time=aps_job.trigger.run_date



    return True


def dispatch_test():
    logger.debug('aaaa')
    logger.info('tttt')
    logger.warning('wwww')
    return
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
    # tasks = TaskOpt.get_all_need_restart_task()
    # insert_tasks(tasks)
    # run()

    dispatch_test()
