#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-20
# Function: 任务的处理器，任务经由各处理器再发往任务队列, 处理器会被定时程序调用

from .workers import app
from db import JobOpt, TaskOpt, TaskCategoryOpt, AgentOpt
from config import logger
from db.basic import ScopedSession


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


def find_optimal_agent(account, agents):
    """
    找到最适合账号的agent
    :param account: 账号
    :param agents: 可用agents
    :return: agent实例
    """
    if account.active_area:
        for agent in agents:
            if account.active_area == agent.area:
                return agent

    return None


def send_task_2_worker(task_id):
    """
    定时任务响应函数，负责把任务按账号拆解成job, 并发送给最适合的队列
    :param task_id: 任务id
    :return: 成功返回True, 失败返回False
    """
    db_session = ScopedSession()
    task = TaskOpt.get_task_by_task_id(db_session, task_id)
    if not task:
        logger.error('send_task_2_worker can not find the task, id={}. '.format(task_id))
        return False

    # 根据task的类别，找到task对应的处理函数
    task_processor = TaskCategoryOpt.get_processor(db_session, task.category)

    # 每一个类型的任务都对应一个处理器
    if not task_processor:
        logger.error('Task(id={}) have no processor, ignore processing.'.format(task_id))
        return False

    logger.info('send_task_2_worker task id={}. '.format(task_id))

    agents = AgentOpt.get_enable_agents(db_session, status_order=True)

    # 一个任务会有多个账号， 按照账号对任务进行第一次拆分
    for account in task.accounts:
        if account.status != 'valid':
            logger.warning('account can not be used. task id={}, account id={}'.format(task_id, account.id))
            continue

        agent = find_optimal_agent(account=account, agents=agents)
        if agent:
            agent_id = agent.id
            agent_queue_name = agent.queue_name if agent.queue_name else agent.area.replace(' ', '_')
        else:
            logger.warning('There have no optimal agent for task, task id={}, account id={}, account_area={}'
                           .format(task_id, account.id, account.active_area))
            agent_id = None
            agent_queue_name = 'default'

        # 构建任务执行必备参数
        inputs = {
            'task_id': task_id,
            'task_configure': task.configure,
            'account': account.account,
            'password': account.password,
            'account_active_browser': account.active_browser
        }

        celery_task_name = "tasks.tasks.{}".format(task_processor)

        track = app.send_task(
            celery_task_name,
            args=(inputs, ),
            queue=agent_queue_name,
            routing_key=agent_queue_name
        )

        logger.info('send task name={}, queue={}, task id={}, account id={}, track id={}'.format(
            celery_task_name, agent_queue_name, task_id, account.id, track.id))

        JobOpt.save_job(db_session, task_id, account.id, agent_id=agent_id, track_id=track.id, status='running')

    # 更新任务状态为running
    TaskOpt.set_task_status(db_session, task_id, status='running')

    db_session.commit()
    ScopedSession.remove()

        # job_dict = {'task': task_id, 'account': account.id, 'agent': agent_id, 'status': 'running', 'track_id': track.id}
        # RedisOpt.push_object('job_list', json.dumps(job_dict))
        # try:
        #     track.get(on_message=on_task_message, propagate=False, interval=1, timeout=1)
        # except Exception:
        #     logger.warning(111111111)

    return True
