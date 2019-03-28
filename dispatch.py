#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-18
# Function:


import time
import json
from apscheduler.schedulers.background import BackgroundScheduler
from db import Task, TaskOpt, TaskAccountGroupOpt, TaskCategoryOpt, SchedulerOpt, AgentOpt, JobOpt
from tasks.processor import dispatch_processor
from config import logger
from util import RedisOpt


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
        aps_job = scheduler.add_job(dispatch_processor, 'interval', seconds=task_sch.interval, args=(processor, inputs),
                                    misfire_grace_time=120, coalesce=False, max_instances=5)
    elif task_sch.mode == 2:
        dispatch_processor(processor, inputs)
        aps_job = scheduler.add_job(dispatch_processor, 'interval', seconds=task_sch.interval, args=(processor, inputs),
                                    misfire_grace_time=120, coalesce=False, max_instances=5)
    elif task_sch.mode == 3:
        aps_job = scheduler.add_job(dispatch_processor, 'date', run_date=task_sch.date, args=(processor, inputs),
                                    misfire_grace_time=120, coalesce=False, max_instances=5)

    return aps_job


def find_optimal_agent(account, agents=None):
    if not agents:
        agents = AgentOpt.get_enable_agents()
        if not agents:
            return None

    if account.active_area:
        for agent in agents:
            if account.active_area == agent.area:
                return agent

    return None


def process_task(task: Task) -> bool:
    agents = AgentOpt.get_enable_agents(status_order=True)
    if not agents:
        logger.error('There have no available agent.')
        return False

    task_id = task.id
    task_configure = task.configure
    task_processor = TaskCategoryOpt.get_processor(task.category)
    scheduler_id = task.scheduler
    # 每一个类型的任务都对应一个处理器
    if not task_processor:
        logger.warning('Task(id={}) have no processor, ignore processing.'.format(task_id))
        return False

    logger.info(u'Start processing task, task id={}, task configure={}'.format(task_id, task.configure))
    # 一旦任务被加入到定时程序中，即等待分发执行
    TaskOpt.set_task_status(task_id, 'pending')

    # 一个任务会有多个账号， 按照账号对任务进行第一次拆分，针对每一个账号，启动一个定时任务，这样任务管理粒度更细，也更符合实际情况
    for account in task.accounts:
        agent = find_optimal_agent(account=account, agents=agents)
        if agent:
            agent_id = agent.id
            agent_queue_name = agent.queue_name if agent.queue_name else agent.area.replace(' ', '_')
        else:
            logger.warning('There have no optimal agent for task, task id={}, account id={}, account_area={}'.format(task_id, account.id, account.active_area))
            agent_id = None
            agent_queue_name = 'default'

        # 构建任务执行必备参数
        inputs = {
            'task_id': task_id,
            'account_id': account.id,
            'agent_id': agent_id,
            'account': account.account,
            'password': account.password,
            'agent_queue_name': agent_queue_name,
            'task_configure': task_configure
        }

        logger.info('Start scheduling job, task id={}, account id={}, scheduler id={}, processor={}, agent_id={}.'.format(
                        task_id, account.id, scheduler_id, task_processor, agent_id))

        aps_job = schedule_job(scheduler_id=scheduler_id, processor=task_processor, inputs=inputs)

        # 将aps id 更新到数据库中, aps id 将用于任务的暂停、恢复
        TaskAccountGroupOpt.set_aps_info(task_id, account.id, aps_job.id,)  # next_run_time=aps_job.trigger.run_date
        logger.info('Scheduling job succeed, task id={}, account id={}, aps_job_id={}.'
                    .format(task_id, account.id, aps_job.id))
    else:
        logger.warning('Task has no accounts assigned. task id={}'.format(task_id))
        return False

    return True


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


def save_jobs():
    jobs = RedisOpt.pop_all(key='job_list', is_delete=True)
    job_num = len(jobs)
    last_job_num = RedisOpt.read_object('total_job')
    total_jobs_num = job_num+int(last_job_num) if last_job_num != -1 else job_num
    RedisOpt.write_object(key='total_job', value=total_jobs_num)
    logger.info('save_jobs total number={}'.format(total_jobs_num))

    if jobs:
        jobs = [json.loads(job) for job in jobs]
        JobOpt.save_jobs(jobs)


def update_results():
    results = RedisOpt.pop_all_backend(pattern='celery-task-meta*', is_delete=True)
    results_num = len(results)
    last_results_num = RedisOpt.read_object('total_num')
    total_result_num = results_num+int(last_results_num) if last_results_num != -1 else results_num
    RedisOpt.write_object(key='total_num', value=total_result_num)
    logger.info('update_results total number={}'.format(total_result_num))

    status_map = {'SUCCESS': 'succeed', 'FAILURE': 'failed', 'PENDING': 'pending', 'RUNNING': 'running'}
    track_ids = []
    values = {}
    for res in results:
        dict_res = json.loads(res)
        status = dict_res.get('status')
        track_id = dict_res.get('task_id', '')
        job_res = dict_res.get('result', '')
        job_res = json.dumps(job_res) if isinstance(job_res, dict) else str(job_res)

        track_ids.append(track_id)
        values[track_id] = {
            'track_id': track_id,
            'status': status_map.get(status, status),
            'result': job_res,
            'traceback': str(dict_res.get('traceback', ''))
        }

    return JobOpt.set_job_by_track_ids(track_ids=track_ids, values=values)


def run():
    try:
        RedisOpt.clean_cache_db()
        RedisOpt.clean_backend_db()
        # RedisOpt.clean_broker_db()

        save_job = scheduler.add_job(save_jobs, 'interval', seconds=60, misfire_grace_time=10, max_instances=5)
        update_job = scheduler.add_job(update_results, 'interval', seconds=60, misfire_grace_time=20, max_instances=5)
        scheduler.start()
        logger.info('Start scheduling.')
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        logger.warning('Scheduler have been stopped.')
        scheduler.shutdown()


if __name__ == '__main__':
    logger.info('Start run..')
    tasks = TaskOpt.get_all_need_restart_task()
    if not isinstance(tasks, list):
        raise TypeError('tasks must be a list.')
    for t in tasks:
        process_task(t)

    run()

    # dispatch_test()
