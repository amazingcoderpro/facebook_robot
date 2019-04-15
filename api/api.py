#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-30
# Function: 


# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-18
# Function:


from datetime import timedelta, datetime
from collections import namedtuple
import json
from apscheduler.schedulers.base import JobLookupError
from db import TaskOpt, SchedulerOpt, JobOpt, AgentOpt, AccountOpt, Job, Task, Scheduler, Agent, Account
from tasks.processor import send_task_2_worker
from config import logger
from util import RedisOpt
from db.basic import ScopedSession
from sqlalchemy import and_


g_bk_scheduler = None
Result = namedtuple('Result', ['res', 'msg'])
last_check_time = datetime.now()


def scheduler_task(db_session, scheduler_id, *args):
    """
    启动任务的定时处理程序
    :param scheduler_id: 调度实例id
    :param args: 透传参数
    :return: 成功返回 APScheduler 任务id, 失败返回 None
    """
    status = ''
    # mode, interval, start_date, end_date = SchedulerOpt.get_scheduler(scheduler_id)
    mode, interval, start_date, end_date = db_session.query(Scheduler.mode, Scheduler.interval, Scheduler.start_date, Scheduler.end_date).filter(
        Scheduler.id == scheduler_id).first()
    # 判断任务是否已经过期
    if end_date and end_date <= datetime.now():
        logger.warning(
            'Task has expired, end_date={}, scheduler id={}, args={}'.format(end_date, scheduler_id, args))
        return None, status

    # 对于周期性任务, 最小时间间隔应该大于60秒
    if mode in [1, 2] and interval < 60:
        logger.warning(
            'Task scheduler interval is too short. interval={}, scheduler_id={}, ars={}'.format(interval,
                                                                                                scheduler_id, args))
        return None, status

    # 对于指定启动时间的任务, 启动时间应该大于当前时间, 对于1可以不指定start date
    if mode in [1, 3] and start_date and start_date < datetime.now():
        logger.warning('Timed task start date is null or earlier than now. start date={}, scheduler_id={}, args={}'.format(
            start_date, scheduler_id, args))
        return None, status

    # 根据任务计划模式的不同启动不同的定时任务
    # 执行模式：
    # 0 - 立即执行（只执行一次）, 此时会忽略start_date,end_date参数
    # 1 - 间隔执行并不立即开始（默认是间隔interval秒时间后开始执行,并按设定的间隔周期执行下去, 若指定start_date,则 在指定的start_date时间开始周期执行
    # 2 - 间隔执行且立即开始, 此时会忽略start_date, 直接开始周期任务, 直到达到task指定的次数,或者到达end_date时间结束
    # 3 - 定时执行,指定时间执行, 此时必须要指定start_date, 将在start_date时间执行一次
    # dispatch_processor(processor, inputs)

    if mode == 0:
        aps_job = g_bk_scheduler.add_job(send_task_2_worker, args=args)
    elif mode == 1:
        if start_date:
            aps_job = g_bk_scheduler.add_job(send_task_2_worker, 'interval', seconds=interval,
                                             start_date=start_date, args=args,
                                             misfire_grace_time=120, coalesce=False, max_instances=5)
        else:
            aps_job = g_bk_scheduler.add_job(send_task_2_worker, 'interval', seconds=interval, args=args,
                                             misfire_grace_time=120, coalesce=False, max_instances=5)
        status = 'pending'
    elif mode == 2:
        send_task_2_worker(args)
        aps_job = g_bk_scheduler.add_job(send_task_2_worker, 'interval', seconds=interval, args=args,
                                         misfire_grace_time=120, coalesce=False, max_instances=5)
    elif mode == 3:
        aps_job = g_bk_scheduler.add_job(send_task_2_worker, 'date', run_date=start_date, args=args,
                                         misfire_grace_time=120, coalesce=False, max_instances=5)
        status = 'pending'
    else:
        logger.error('can not processing scheduler mode={}.'.format(mode))
        return None, status

    return aps_job, status


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
    total_jobs_num = job_num + int(last_job_num) if last_job_num != -1 else job_num
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
    try:
        db_session = ScopedSession()
        running_tasks = db_session.query(Task).filter(Task.status == 'running').all()
        # running_tasks = TaskOpt.get_all_running_task()
        for task in running_tasks:

            failed_counts = db_session.query(Job.status).filter(and_(Job.task == task.id, Job.status == 'failed')).count()
            succeed_counts = db_session.query(Job.status).filter(
                and_(Job.task == task.id, Job.status == 'succeed')).count()

            task.succeed_counts = succeed_counts
            task.failed_counts = failed_counts
            logger.info('-----update_task_status task id={} status={}, succeed={}, failed={}'.
                        format(task.id, task.status, task.succeed_counts, task.failed_counts))

            # sch = SchedulerOpt.get_scheduler(task.scheduler)
            sch_mode, sch_end_date = db_session.query(Scheduler.mode, Scheduler.end_date)\
                .filter(Scheduler.id == task.scheduler).first()
            # 如果是一次性任务,只要所有job结果都返回了, task即结束
            if sch_mode in [0, 3]:
                running_jobs = db_session.query(Job.status).filter(
                and_(Job.task == task.id, Job.status == 'running')).count()
                if ((task.failed_counts + task.succeed_counts) >= task.real_accounts_num) \
                        or running_jobs == 0 or (task.start_time and task.start_time < datetime.now()-timedelta(days=3)):
                    if task.succeed_counts >= task.limit_counts:
                        task.status = 'succeed'
                    else:
                        task.status = 'failed'
            # 对于周期性任务, 如果成功次数达到需求最大值, 或者时间达到终止时间, 则任务置为结束, 并从scheduler中移除所有的aps job
            else:
                if task.succeed_counts >= task.limit_counts:
                    task.status = 'succeed'
                    task.end_time = datetime.now()
                elif sch_end_date and datetime.now() >= sch_end_date:
                    task.status = 'failed'
                else:
                    # 周期性任务的最长期限上限为120天, 超过120天自动关闭
                    if task.start_time < datetime.now()-timedelta(days=120):
                        task.status = 'failed'

            if task.status in ['succeed', 'failed']:
                task.end_time = datetime.now()
                # aps_id = TaskOpt.get_aps_ids_by_task_id(task.id)
                aps_id = db_session.query(Task.aps_id).filter(Task.id == task.id).first()[0]
                try:
                    g_bk_scheduler.remove_job(aps_id)
                except JobLookupError:
                    logger.warning('job have been removed. aps_id={}'.format(aps_id))
                logger.info('update_task_status task {} status={}, succeed={}, failed={}'.format(task.id, task.status,
                                                                                                 task.succeed_counts,
                                                                                                 task.failed_counts))
        db_session.commit()
    except Exception as e:
        logger.exception('update_task_status catch exception e={}'.format(e))
        db_session.rollback()
    finally:
        ScopedSession.remove()


def update_agent_status():
    """
    根据运行结果实时更新agent的忙碌程度
    :return:
    """
    try:
        db_session = ScopedSession()
        agent_ids = db_session.query(Agent.id).filter(Agent.status != -1).all()
        for agent in agent_ids:
            agent_id = agent[0]
            running_jobs_num = db_session.query(Job).filter(Job.agent == agent_id, Job.status == 'running').count()
            db_session.query(Agent).filter(Agent.id == agent_id).update({Agent.status: running_jobs_num}, synchronize_session=False)
            logger.info('update_agent_status Agent id={}, status={}'.format(agent_id, running_jobs_num))
    except Exception as e:
        logger.exception('update_agent_status catch exception agent e={}'.format(e))
        db_session.rollback()
    finally:
        ScopedSession.remove()


def update_account_usage():
    """
    根據運行結果實時更新account的使用狀態
    :return:
    """
    try:

        db_session = ScopedSession()
        running_jobs = db_session.query(Job.account).filter(Job.status == 'running').all()
        logger.info('update_account_usage, running jobs={}'.format(len(running_jobs)))

        account_usage = {}
        for account in running_jobs:
            account_id = account[0]
            if account_id in account_usage:
                account_usage[account_id] += 1
            else:
                account_usage[account_id] = 1

        for account_id, using in account_usage.items():
            db_session.query(Account).filter(Account.id == account_id).update({Account.using: using, Account.last_update: datetime.now()})

        db_session.commit()
    except Exception as e:
        logger.exception('update_account_usage catch exception account id={}, e={}'.format(account_id, e))
        db_session.rollback()
    finally:
        ScopedSession.remove()


def update_results():
    """
    根据backend中的值更新数据库中job的状态, 每次只更新运行超过5分钟的job, 同时逆向更新task状态
    :return:
    """
    status_map = {'SUCCESS': 'succeed', 'FAILURE': 'failed', 'PENDING': 'pending', 'RUNNING': 'running'}
    del_keys = []
    is_exception = False
    time_it_beg = datetime.now()
    try:
        updated_jobs_num = 0
        failed_jobs_num = 0
        succeed_jobs_num = 0
        db_session = ScopedSession()
        # 取出5分钟前启动且没有执行完毕的job, 去redis中查询结果是否已经出来了
        job_start_time = datetime.now()-timedelta(seconds=300)
        need_update_jobs = db_session.query(Job.id, Job.track_id, Job.account).filter(and_(Job.status == 'running', Job.start_time <= job_start_time)).all()
        logger.info('-------need update jobs num={}'.format(len(need_update_jobs)))

        for job_id, track_id, account_id in need_update_jobs:
            key_job = 'celery-task-meta-{}'.format(track_id)
            result = RedisOpt.read_backend(key=key_job)
            if result:
                dict_res = json.loads(result)
                status = status_map.get(dict_res.get('status'), dict_res.get('status'))
                job_res = dict_res.get('result', '')
                str_job_res = ''

                # 除了任务本身的成败外,还需要关注实际返回的结果
                if isinstance(job_res, dict):
                    if job_res.get('status', '') == 'failed':
                        status = 'failed'

                    account_status = job_res.get('account_status', '')
                    account_config = job_res.get('account_configure', {})
                    if account_status:
                        logger.info('update account status={}'.format(account_status))
                        db_session.query(Account).filter(Account.id == account_id).update({Account.status: account_status,
                                                                                           Account.last_update: datetime.now()})
                    if account_config:
                        logger.info('update account config={}'.format(account_config))
                        db_session.query(Account).filter(Account.id == account_id).update(
                            {Account.configure: json.dumps(account_config), Account.last_update: datetime.now()})

                    str_job_res = json.dumps(job_res)
                else:
                    str_job_res = str(job_res)

                db_session.query(Job).filter(Job.id == job_id).update(
                    {Job.status: status, Job.result: str_job_res, Job.traceback: str(dict_res.get('traceback', '')),
                     Job.end_time: datetime.now()},
                    synchronize_session=False)

                del_keys.append(key_job)
                updated_jobs_num += 1
                if status == 'succeed':
                    succeed_jobs_num += 1
                else:
                    failed_jobs_num += 1

        db_session.commit()
        logger.info('-------actually update jobs num={}'.format(updated_jobs_num))
    except Exception as e:
        is_exception = True
        logger.exception('--------update_results catch exception e={}'.format(e))
        db_session.rollback()
    finally:
        ScopedSession.remove()

    # 将落盘成功的数据从缓存区清掉
    if not is_exception:
        if updated_jobs_num > 0:
            # RedisOpt.delete_backend_more(*del_keys)
            last_num = RedisOpt.read_object('total_updated_jobs_num')
            last_succeed_num = RedisOpt.read_object('succeed_jobs_num')
            last_failed_num = RedisOpt.read_object('failed_jobs_num')

            total_updated_jobs_num = updated_jobs_num + int(last_num) if last_num != -1 else updated_jobs_num
            succeed_jobs_num = succeed_jobs_num + int(last_succeed_num) if last_succeed_num != -1 else succeed_jobs_num
            failed_jobs_num = failed_jobs_num + int(last_failed_num) if last_failed_num != -1 else failed_jobs_num

            RedisOpt.write_object(key='total_updated_jobs_num', value=total_updated_jobs_num)
            RedisOpt.write_object(key='succeed_jobs_num', value=succeed_jobs_num)
            RedisOpt.write_object(key='failed_jobs_num', value=failed_jobs_num)

    # 根据更新后的job状态,逆向更新任务状态
    update_task_status()

    # 根据运行结果实时更新agent的忙碌程度
    update_agent_status()

    # 根據運行結果實時更新account的使用狀態
    update_account_usage()

    # 处理任务状态变更
    process_updated_tasks()

    # 启动所有新建任务
    start_all_new_tasks()

    logger.info('update results used {} seconds.'.format((datetime.now()-time_it_beg).seconds))


def process_updated_tasks():
    """
    处理任务状态变更
    :return:
    """
    global last_check_time
    logger.info('process_updated_tasks, last check time={}'.format(last_check_time))
    # tasks = TaskOpt.get_all_need_check_task(last_time=last_check_time-timedelta(seconds=1))
    try:
        db_session = ScopedSession()
        last_time = last_check_time - timedelta(seconds=1)
        tasks = db_session.query(Task.id, Task.status, Task.last_update) \
            .filter(and_(Task.status.in_(('pausing', 'running', 'cancelled')), Task.last_update >= last_time)).all()
        last_check_time = datetime.now()
        for task_id, status, last_update in tasks:
            logger.info('process_updated_tasks task id={}, status={}, last_update={}'.format(task_id, status, last_update))
            if last_update >= last_check_time:
                if status == 'cancelled':
                    cancel_task(task_id)
                elif status == 'pausing':
                    pause_task(task_id)
                elif status == 'running':
                    resume_task(task_id)

    except Exception as e:
        logger.exception('process_updated_tasks catch exception e={}'.format(e))
        db_session.rollback()
    finally:
        ScopedSession.remove()


def start_all_new_tasks(scheduler=None):
    """
    检测新建任务, 并加入执行
    :return:
    """
    if scheduler:
        global g_bk_scheduler
        g_bk_scheduler = scheduler

    # tasks = TaskOpt.get_all_new_task()
    db_session = ScopedSession()
    tasks = db_session.query(Task.id, Task.status).filter(Task.status == 'new').all()
    db_session.commit()
    ScopedSession.remove()
    logger.info('start_all_new_tasks, tasks={}'.format(tasks))
    for task_id, status in tasks:
        logger.info('begin start task id={}, status={}'.format(task_id, status))
        start_task(task_id)


def restart_all_tasks(scheduler=None):
    """
    重新启动所有需要重新运行的任务, 可用于系统宕机后的重启
    :return:
    """
    if scheduler:
        global g_bk_scheduler
        g_bk_scheduler = scheduler

    need_restart_tasks = TaskOpt.get_all_need_restart_task()
    logger.info('restart_all_tasks, need_restart_tasks={}'.format(need_restart_tasks))
    for task_id, status in need_restart_tasks:
        logger.info('need restart task id={}, status={}.'.format(task_id, status))
        start_task(task_id, force=True)

    return Result(res=True, msg='')


def clean_environment():
    """
    清空缓存
    :return:
    """
    RedisOpt.clean_cache_db()
    RedisOpt.clean_backend_db()
    RedisOpt.clean_broker_db()


def start_task(task_id, force=False):
    """
    启动任务
    :param task_id: 任务id
    :param force: 是否强制启动国（若是， 所有未完成的任务都将重新启动，用于系统重启）
    :return: 成功返回True, 失败返回False
    """
    # res = TaskOpt.get_task_status_apsid(task_id)
    try:
        db_session = ScopedSession()
        res = db_session.query(Task.status, Task.aps_id, Task.scheduler).filter(Task.id == task_id).first()
        if not res:
            logger.error('start_task can not find the task id={}. '.format(task_id))
            return Result(res=False, msg='can not find the task')

        status, aps_id, scheduler = res
        # 已经完成或失败的任务不再重新启动
        if status in ['succeed', 'failed', 'cancelled']:
            logger.warning("task is finished. task id={}, status={}".format(task_id, status))
            return Result(res=False, msg='task is finished.')

        # 强制状态下，可以启动所有new, pending, pausing, running状态的任务,
        if force:
            # 如果task已经启动，先移除(用于系统重启）
            if status in ['pending', 'pausing', 'running']:
                try:
                    g_bk_scheduler.remove_job(aps_id)
                except JobLookupError:
                    logger.warning('job have been removed.')

                db_session.query(Task).filter(Task.id == task_id). \
                    update({Task.status: "new", Task.aps_id: '', Task.start_time: None, Task.last_update: datetime.now()}, synchronize_session=False)
                db_session.commit()
        else:
            # 非强制状态只能启动new任务
            if status != 'new':
                logger.warning('start_task task is not a new task, task id={} status={}. '.format(task_id, status))
                return Result(res=False, msg='is not a new task')

        # 开始启动任务调度
        aps_job, status_new = scheduler_task(db_session, scheduler, task_id)

        # 将aps id 更新到数据库中, aps id 将用于任务的暂停、恢复、终止
        if aps_job:
            if status_new:
                # 如果任务调度开始执行了, task状态会被置为running,就不用再改回pending
                db_session.query(Task).filter(Task.id == task_id). \
                    update({Task.status: status_new, Task.aps_id: aps_job.id, Task.last_update: datetime.now()}, synchronize_session=False)
            else:
                db_session.query(Task).filter(Task.id == task_id). \
                    update({Task.aps_id: aps_job.id, Task.status: 'running', Task.start_time: datetime.now(), Task.last_update: datetime.now()}, synchronize_session=False)

            db_session.commit()
            logger.info('----start task succeed. task id={}, aps id={}, status={}-----'.format(task_id, aps_job.id, status_new))

            # TaskOpt.set_task_status(None, task_id, status='pending', aps_id=aps_job.id)
        else:
            logger.error('start task can not scheduler task, task id={}, status={}, scheduler={}'.format(task_id, status, scheduler))
            return Result(res=False, msg='scheduler task failed')
    except Exception as e:
        db_session.rollback()
        logger.exception('start_task catch exception task id={}, e={}'.format(task_id, e))
    finally:
        ScopedSession.remove()
    return Result(res=True, msg='start task succeed. id={}'.format(task_id))


def pause_task(task_id):
    """
    暂停任务
    :param task_id:
    :return:
    """
    task = TaskOpt.get_task_by_task_id(None, task_id)
    if not task:
        logger.error('pause_task can not find the task, task id={}. '.format(task_id))
        return Result(res=False, msg='can not find the task')

    if task.status not in ['pausing', 'pending', 'running']:
        logger.error('pause_task but task is not running, task id={}. '.format(task_id))
        return Result(res=False, msg='task have is not running')

    logger.info('pause_task task id={}'.format(task_id))
    try:
        g_bk_scheduler.pause_job(task.aps_id)
    except JobLookupError:
        logger.exception('pause_task, job have been removed.')
        return Result(res=False, msg='pause_task, job have been removed.')

    task.status = 'pausing'
    return Result(res=True, msg='')


def resume_task(task_id):
    """
    恢复任务
    :param task_id:
    :return:
    """
    task = TaskOpt.get_task_by_task_id(None, task_id)
    if not task:
        logger.error('resume_task can not find the task, task id={}. '.format(task_id))
        return Result(res=False, msg='can not find the task')

    if task.status not in ['pausing', 'pending', 'running']:
        logger.error('resume_task task is not running, task id={}'.format(task_id))
        return Result(res=False, msg='task is not running')

    logger.info('resume_task task id={}'.format(task_id))
    try:
        ret = g_bk_scheduler.resume_job(task.aps_id)
    except JobLookupError:
        logger.exception('resume_task, job have been removed.')
        return Result(res=False, msg='job have been removed.')

    # 如果任务已经过期则ret会是null
    if ret:
        task.status = 'running'
        return Result(res=True, msg='')
    else:
        task.status = 'failed'
        return Result(res=False, msg='task has already expired')


def cancel_task(task_id):
    """
    取消任务
    :param task_id: 任务id
    :return: Result
    """
    task = TaskOpt.get_task_by_task_id(None, task_id)
    if not task:
        logger.error('cancel_task can not find the task, id={}. '.format(task_id))
        return Result(res=False, msg='can not find the task')

    if task.status in ['succeed', 'failed']:
        logger.error('cancel_task but task have been finished, id={}. '.format(task_id))
        return Result(res=False, msg='task have been finished')

    logger.info('cancel_task task id={}'.format(task_id))
    try:
        g_bk_scheduler.remove_job(task.aps_id)
    except JobLookupError:
        pass

    task.status = 'cancelled'
    return Result(res=True, msg='')
