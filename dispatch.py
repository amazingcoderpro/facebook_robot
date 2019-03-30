#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-18
# Function:


import time
import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import JobLookupError
from db import TaskOpt, SchedulerOpt, JobOpt, AgentOpt
from tasks.processor import send_task_2_worker
from config import logger
from util import RedisOpt


g_bk_scheduler = BackgroundScheduler()


def scheduler_task(scheduler_id, *args):
    """
    启动任务的定时处理程序
    :param scheduler_id: 调度实例id
    :param args: 透传参数
    :return: 成功返回 APScheduler 任务id, 失败返回 None
    """
    task_sch = SchedulerOpt.get_scheduler(scheduler_id)
    # 判断任务是否已经过期
    if task_sch.end_date and task_sch.end_date <= datetime.datetime.now():
        logger.warning('Task has expired, end_date={}, scheduler id={}, args={}'.format(task_sch.end_date, scheduler_id, args))
        return None

    # 对于周期性任务, 最小时间间隔应该大于60秒
    if task_sch.mode in [1, 2] and task_sch.interval < 60:
        logger.error('Task scheduler interval is too short. interval={}, scheduler_id={}, ars={}'.format(task_sch.interval, scheduler_id, args))
        return None

    # 对于指定启动时间的任务, 启动时间应该大于当前时间 
    if task_sch.mode in [1, 3] and task_sch.start_date < datetime.datetime.now():
        logger.error('Timed task start date earlier than now. start date={}, scheduler_id={}, args={}'.format(task_sch.start_date, scheduler_id, args))
        return None
    
    # 根据任务计划模式的不同启动不同的定时任务
    # 执行模式：
    # 0 - 立即执行（只执行一次）, 此时会忽略start_date,end_date参数
    # 1 - 间隔执行并不立即开始（默认是间隔interval秒时间后开始执行,并按设定的间隔周期执行下去, 若指定start_date,则 在指定的start_date时间开始周期执行
    # 2 - 间隔执行且立即开始, 此时会忽略start_date, 直接开始周期任务, 直到达到task指定的次数,或者到达end_date时间结束
    # 3 - 定时执行,指定时间执行, 此时必须要指定start_date, 将在start_date时间执行一次
    # dispatch_processor(processor, inputs)
    if task_sch.mode == 0:
        aps_job = g_bk_scheduler.add_job(send_task_2_worker, args=args)
    elif task_sch.mode == 1:
        if task_sch.start_date and task_sch.start_date > datetime.datetime.now():
            aps_job = g_bk_scheduler.add_job(send_task_2_worker, 'interval', seconds=task_sch.interval,
                                             start_date=task_sch.start_date, args=args,
                                             misfire_grace_time=120, coalesce=False, max_instances=5)
        else:
            aps_job = g_bk_scheduler.add_job(send_task_2_worker, 'interval', seconds=task_sch.interval, args=args,
                                             misfire_grace_time=120, coalesce=False, max_instances=5)
    elif task_sch.mode == 2:
        send_task_2_worker(args)
        aps_job = g_bk_scheduler.add_job(send_task_2_worker, 'interval', seconds=task_sch.interval, args=args,
                                         misfire_grace_time=120, coalesce=False, max_instances=5)
    elif task_sch.mode == 3:
        aps_job = g_bk_scheduler.add_job(send_task_2_worker, 'date', run_date=task_sch.start_date, args=args,
                                         misfire_grace_time=120, coalesce=False, max_instances=5)
    else:
        logger.error('can not processing scheduler mode={}.'.format(task_sch.mode))
        return None

    return aps_job


def start_task(task_id) -> bool:
    """
    启动任务
    :param task_id: 任务id
    :return: 成功返回True, 失败返回False
    """
    task = TaskOpt.get_task_by_task_id(None, task_id)
    if not task:
        logger.error('start_task can not find the task, id={}. '.format(task_id))
        return False

    if task.status in ['succeed', 'failed']:
        logger.error('start_task task have been finished, id={}. '.format(task_id))
        return False

    aps_job = scheduler_task(task.scheduler, task_id)

    # 将aps id 更新到数据库中, aps id 将用于任务的暂停、恢复、终止
    if aps_job:
        TaskOpt.set_task_status(None, task_id, status='pending', aps_id=aps_job.id)
    else:
        logger.error('start_task can not scheduler task, task id={}'.format(task_id))
        return False

    logger.info('----start task succeed. task id={}-----'.format(task_id))
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
    """
    从redis中取出job转存到db
    :return:
    """
    jobs = RedisOpt.pop_all(key='job_list', is_delete=True)
    job_num = len(jobs)
    last_job_num = RedisOpt.read_object('total_job')
    total_jobs_num = job_num+int(last_job_num) if last_job_num != -1 else job_num
    RedisOpt.write_object(key='total_job', value=total_jobs_num)
    logger.info('save_jobs total number={}'.format(total_jobs_num))

    if jobs:
        jobs = [json.loads(job) for job in jobs]
        JobOpt.save_jobs(jobs)


def update_task_status():
    """
    更新任务状态
    :return:
    """
    running_tasks = TaskOpt.get_all_running_task()
    for task in running_tasks:

        failed_counts = 0
        succeed_counts = 0
        jobs = JobOpt.get_jobs_by_task_id(task.id)
        for j in jobs:
            if j[0] == 'succeed':
                succeed_counts += 1
            elif j[0] == 'failed':
                failed_counts += 1

        task.succeed_counts = succeed_counts
        task.failed_counts = failed_counts
        logger.info('update_task_status task {} status={}, succeed={}, failed={}'.
                    format(task.id, task.status, task.succeed_counts, task.failed_counts))

        sch = SchedulerOpt.get_scheduler(task.scheduler)
        # 如果是一次性任务,只要所有job结果都返回了, task即结束
        if sch.mode in [0, 3]:
            if (task.failed_counts + task.succeed_counts) >= task.accounts_num:
                if task.succeed_counts >= task.limit_counts:
                    task.status = 'succeed'
                else:
                    task.status = 'failed'
        # 对于周期性任务, 如果成功次数达到需求最大值, 或者时间达到终止时间, 则任务置为结束, 并从scheduler中移除所有的aps job
        else:
            if task.succeed_counts >= task.limit_counts:
                task.status = 'succeed'
                task.end_time = datetime.datetime.now()
            elif sch.end_date and datetime.datetime.now() >= sch.end_date:
                task.status = 'failed'
            else:
                pass

        if task.status in ['succeed', 'failed']:
            task.end_time = datetime.datetime.now()
            aps_id = TaskOpt.get_aps_ids_by_task_id(task.id)
            try:
                g_bk_scheduler.remove_job(aps_id)
            except JobLookupError:
                logger.warning('job have been removed. aps_id={}'.format(aps_id))
            logger.info('update_task_status task {} status={}, succeed={}, failed={}'.format(task.id, task.status, task.succeed_counts,
                                                                                          task.failed_counts))


def update_agent_status():
    """
    根据运行结果实时更新agent的忙碌程度
    :return:
    """
    agents = AgentOpt.get_enable_agents(None)
    for agent in agents:
        running_jobs_num = JobOpt.count_jobs_by_agent_id(agent.id, status='running')
        agent.status = running_jobs_num
        logger.info('Agent id={},  status={}'.format(agent.id, agent.status))


def update_results():
    """
    根据backend中的值更新数据库中job的状态, 同时逆向更新task状态
    :return:
    """
    results = RedisOpt.pop_all_backend(pattern='celery-task-meta*', is_delete=False)
    if not results:
        logger.warning('have no results to update.')
        return

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
        status = status_map.get(dict_res.get('status'), dict_res.get('status'))
        track_id = dict_res.get('task_id', '')
        job_res = dict_res.get('result', '')

        # 除了任务本身的成败外,还需要关注实际返回的结果
        if isinstance(job_res, dict) and job_res.get('status', '') == 'failed':
            status = 'failed'

        job_res = json.dumps(job_res) if isinstance(job_res, dict) else str(job_res)
        track_ids.append(track_id)
        values[track_id] = {
            'track_id': track_id,
            'status': status,
            'result': job_res,
            'traceback': str(dict_res.get('traceback', ''))
        }

    logger.info('update_results track ids={}'.format(track_ids))
    unfinished_track_ids = JobOpt.set_job_by_track_ids(track_ids=track_ids.copy(), values=values)
    logger.info('update_results update num={}, unfinished num={}. unfinished track ids={}'
                .format(len(track_ids), len(unfinished_track_ids), unfinished_track_ids))

    # 将落盘成功的数据从缓存区清掉
    for track_id in track_ids:
        if track_id not in unfinished_track_ids:
            RedisOpt.delete_backend('*{}'.format(track_id))

    # 根据更新后的job状态,逆向更新任务状态
    update_task_status()

    # 根据运行结果实时更新agent的忙碌程度
    update_agent_status()


def clean_environment():
    RedisOpt.clean_cache_db()
    RedisOpt.clean_backend_db()
    RedisOpt.clean_broker_db()


def start(start_new=True, update_interval=30):
    """
    启动任务调度系统
    :param start_new: 是否全新开始,若是则清空缓存,从头开始； 若否,则继续上一次结束点开始,之前未处理完的任务将继续被执行
    :param update_interval: 结果更新周期,默认30秒
    :return:
    """
    try:
        logger.info('----Start Task Scheduler System.----')
        if start_new:
            logger.info('clean environment. ')
            clean_environment()
        else:
            need_restart_tasks = TaskOpt.get_all_need_restart_task()
            for task in need_restart_tasks:
                logger.info('need restart task id={}, status={}.'.format(task.id, task.status))
                start_task(task.id)

        # 启动定时结果更新
        g_bk_scheduler.add_job(update_results, 'interval', seconds=update_interval, misfire_grace_time=20, max_instances=5)
        g_bk_scheduler.start()

        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        g_bk_scheduler.shutdown()
        logger.warning('Scheduler have been stopped.')
    finally:
        if g_bk_scheduler.running:
            g_bk_scheduler.shutdown()
    logger.info('----Stop Task Scheduler System.----')


if __name__ == '__main__':
    clean_environment()
    start(start_new=False)


    # dispatch_test()
"""
update facebook.task set status='new' where id>0;
update facebook.task set failed_counts=0 where id>0;
update facebook.task set succeed_counts=0 where id>0;
update facebook.task set start_time=null where id>0;
update facebook.task set end_time=null where id>0;
"""
