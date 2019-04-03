#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-20
# Function: 任务的处理器，任务经由各处理器再发往任务队列, 处理器会被定时程序调用
import datetime
from .workers import app
from db import JobOpt, Job, Task, TaskCategory, Agent, TaskAccountGroup, Account
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
        task = db_scoped_session.query(Task.category, Task.configure).filter(Task.id == task_id).first()
        if not task:
            logger.error('send_task_2_worker can not find the task, id={}. '.format(task_id))
            return False

        category, configure = task

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
        accounts = db_scoped_session.query(Account.id, Account.status, Account.account, Account.password,
                                           Account.configure, Account.active_area, Account.active_browser).filter(
            Account.id.in_(account_ids)).all()

        agents = db_scoped_session.query(Agent.id, Agent.queue_name, Agent.area).filter(Agent.status != -1).order_by(Agent.status).all()

        # 一个任务会有多个账号， 按照账号对任务进行第一次拆分
        real_accounts_num = 0
        for acc in accounts:
            acc_id, status, account, password, configure, active_area, active_browser = acc
            if status != 'valid':
                logger.warning('account can not be used. task id={}, account id={}'.format(task_id, acc_id))
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

            # 构建任务执行必备参数
            inputs = {
                'task_id': task_id,
                'task_configure': configure,
                'account': account,
                'password': password,
                'account_active_browser': active_browser
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

        # 更新任务状态为running
        # task实际可用的账号数目, 会根据每次轮循时account状态的不同而变化

        db_scoped_session.query(Task).filter(and_(Task.id == task_id, Task.status.in_(['new', 'pending'])))\
            .update({Task.status: "running", Task.start_time: datetime.datetime.now(),
                     Task.real_accounts_num: real_accounts_num}, synchronize_session=False)

        if jobs:
            db_scoped_session.add_all(jobs)

        db_scoped_session.commit()

        logger.info('time it end, send task {}, used {} seconds'.format(task_id, (
                datetime.datetime.now() - time_it_beg).seconds))
    except BaseException as e:
        logger.exception('send_task_2_worker exception task id={}, e={}'.format(task_id, e))
        db_scoped_session.rollback()
    finally:
        ScopedSession.remove()

    return True
