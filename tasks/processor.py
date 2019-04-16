#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-20
# Function: 任务的处理器，任务经由各处理器再发往任务队列, 处理器会被定时程序调用
import json
import datetime
from .workers import app
from db import JobOpt, Job, Task, TaskCategory, Agent, TaskAccountGroup, Account, Scheduler, FingerPrint
from config import logger
from db.basic import ScopedSession
from sqlalchemy import and_


def on_task_message(msg):
    # 根据各agent的反馈结果，更新任务状态
    status_map = {'SUCCESS': 'succeed', 'FAILURE': 'failed', 'PENDING': 'pending', 'RUNNING': 'running'}
    status = msg.get('status', '')
    task_id = msg.get('task_id', '')
    result = msg.get('result', '')
    traceback = msg.get('traceback', '')
    logger.info('on_task_message: status={}, task id={}, result={}.'.format(status, task_id, result))
    JobOpt.set_job_by_track_id(track_id=task_id,
                               status=status_map.get(status, status),
                               result='' if not result else str(result)[0:2048],
                               traceback='' if not traceback else str(traceback)[0:2048])


def find_optimal_agent(area, agents=None):
    """
    根据地域找到最适合账号的agent
    :param area: 账号的地域
    :param agents: 备选agents
    :return: agent的id, 队列名, 地域
    """
    if not agents:
        db_scoped_session = ScopedSession()
        agents = db_scoped_session.query(Agent.id, Agent.queue_name, Agent.active_area).filter(Agent.status != -1).order_by(Agent.status).all()

    for agent_id, agent_queue_name, agent_area in agents:
        if area == agent_area:
            return agent_id, agent_queue_name, agent_area
    return None


def send_task_2_worker(task_id):
    """
    定时任务响应函数，负责把任务按账号拆解成job, 并发送给最适合的队列
    :param task_id: 任务id
    :return: 成功返回True, 失败返回False
    """
    try:
        jobs = []
        time_it_beg = datetime.datetime.now()
        db_scoped_session = ScopedSession()
        task = db_scoped_session.query(Task.category, Task.configure, Task.limit_counts, Task.succeed_counts, Task.scheduler).filter(Task.id == task_id).first()
        if not task:
            logger.error('send_task_2_worker can not find the task, id={}. '.format(task_id))
            return False

        category, task_configure, limit_counts, succeed_counts, sch_id = task

        sch_mode = db_scoped_session.query(Scheduler.mode).filter(Scheduler.id == sch_id).first()

        # 对于周期性任务,每次产生的job会严格控制, 但对于一次性任务, 用户指定多少个账号，就用多少个账号
        if sch_mode[0] in [1, 2]:
            if limit_counts:
                # 如果当前任务的成功数大于需求数, 或者成功数加上正在运行的job数目大于用于需求数110%, 则不需要继续产生job
                if succeed_counts >= int(limit_counts*1.2):
                    logger.error('send_task_2_worker ignore, task already finished, task id={}, succeed jobs({}) >= limit counts({})*1.2'.format(task_id, succeed_counts, limit_counts))
                    return True

                task_running_jobs = db_scoped_session.query(Job).filter(and_(Job.task == task_id, Job.status == 'running')).count()
                if task_running_jobs + succeed_counts >= int(limit_counts*1.2):
                    logger.error('send_task_2_worker ignore, task will finish, task id={}, succeed jobs({})+running jobs({})  >= limit counts({})*1.2'.format(task_id, succeed_counts, task_running_jobs, limit_counts))
                    return True

                # 一个任务正在运行job积压过多时, 暂时停止产生新的jobs
                if task_running_jobs >= 10000:
                    logger.error('task({}) jobs num={} has reached jobs limit 10000'.format(task_id, task_running_jobs))
                    return True

        # 根据task的类别，找到task对应的处理函数
        tcg = db_scoped_session.query(TaskCategory.processor).filter(TaskCategory.category == category).first()
        if not tcg:
            return False

        # 每一个类型的任务都对应一个处理器
        task_processor = tcg[0]
        if not task_processor:
            logger.error('Task(id={}) have no processor, ignore processing.'.format(task_id))
            return False

        logger.info('---------send_task_2_worker task id={}. --------'.format(task_id))

        # 找到任务的所有账号
        res = db_scoped_session.query(TaskAccountGroup.account_id).filter(TaskAccountGroup.task_id == task_id).all()
        account_ids = [x[0] for x in res]
        accounts = db_scoped_session.query(Account.id, Account.status, Account.account, Account.password, Account.email,
                                           Account.email_pwd, Account.gender, Account.phone_number, Account.birthday,
                                           Account.national_id, Account.name, Account.active_area, Account.active_browser,
                                           Account.profile_path, Account.configure).filter(
            Account.id.in_(account_ids)).all()

        agents = db_scoped_session.query(Agent.id, Agent.queue_name, Agent.area).filter(Agent.status != -1).order_by(Agent.status).all()

        # 一个任务会有多个账号， 按照账号对任务进行第一次拆分
        real_accounts_num = 0
        for acc in accounts:
            acc_id, status, account, password, email, email_pwd, gender, phone_number, birthday, national_id, name, \
            active_area, active_browser_id, profile_path, account_configure = acc

            if status == 'invalid':
                logger.warning('account status in invalid. task id={}, account id={}'.format(task_id, acc_id))
                continue

            agent = find_optimal_agent(area=active_area, agents=agents)
            if agent:
                agent_id, agent_queue_name, agent_area = agent
                if not agent_queue_name:
                    agent_queue_name = agent_area.replace(' ', '_')
            else:
                logger.warning('There have no optimal agent for task, task id={}, account id={}, account_area={}'
                               .format(task_id, acc_id, active_area))
                agent_id = None
                agent_queue_name = 'default'

            active_browser = db_scoped_session.query(FingerPrint.value).filter(FingerPrint.id == active_browser_id).first()

            # 构建任务执行必备参数
            inputs = {
                'task': {
                    'task_id': task_id,
                    'configure': json.loads(task_configure) if task_configure else {},
                },
                'account': {
                    'account': account,
                    'password': password,
                    'status': status,
                    'email': email,
                    'email_pwd': email_pwd,
                    'gender': gender,
                    'phone_number': phone_number,
                    'birthday': birthday,
                    'national_id': national_id,
                    'name': name,
                    'active_area': active_area,
                    'active_browser': json.loads(active_browser[0]) if active_browser else {},
                    'profile_path': profile_path,
                    'configure': json.loads(account_configure) if account_configure else {}
                }
            }

            celery_task_name = "tasks.tasks.{}".format(task_processor)
            real_accounts_num += 1

            track = app.send_task(
                celery_task_name,
                args=(inputs, ),
                queue=agent_queue_name,
                routing_key=agent_queue_name
            )

            logger.info('-----send sub task to worker, celery task name={}, queue={}, '
                        'task id={}, account id={}, track id={}'.format(celery_task_name, agent_queue_name, task_id, acc_id, track.id))

            job = Job()
            job.task = task_id
            job.task = task_id
            job.account = acc_id
            job.agent = agent_id
            job.status = 'running'
            job.track_id = track.id
            job.start_time = datetime.datetime.now()
            jobs.append(job)

            if sch_mode[0] in [1, 2]:
                # 如果已经在运行的jobs,加上当前产生的jobs数量超过用户需求数量,则break, 停止生产jobs, 下个调度周期重新检测再试
                total_running_jobs = task_running_jobs + real_accounts_num
                if (limit_counts and total_running_jobs >= int(limit_counts*1.2)) or total_running_jobs >= 10000:
                    logger.warning('task({}) total running jobs num({}) is already more than limit counts({})*1.2'.format(task_id, total_running_jobs, limit_counts))
                    break

        # 更新任务状态为running
        # task实际可用的账号数目, 会根据每次轮循时account状态的不同而变化
        db_scoped_session.query(Task).filter(and_(Task.id == task_id, Task.status.in_(['new', 'pending'])))\
            .update({Task.status: "running", Task.start_time: datetime.datetime.now(),
                     Task.real_accounts_num: real_accounts_num, Task.last_update: datetime.datetime.now()}, synchronize_session=False)

        if jobs:
            db_scoped_session.add_all(jobs)

        db_scoped_session.commit()

        logger.info('----send_task_2_worker send task {}, produce jobs={}, used {} seconds. '.format(task_id, real_accounts_num, (
                datetime.datetime.now() - time_it_beg).seconds))
    except BaseException as e:
        logger.exception('send_task_2_worker exception task id={}, e={}'.format(task_id, e))
        db_scoped_session.rollback()
    finally:
        ScopedSession.remove()

    return True
