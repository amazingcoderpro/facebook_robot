#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-20
# Function: 任务的处理器，任务经由各处理器再发往任务队列, 处理器会被定时程序调用

import json
from .workers import app
from db import JobOpt
from config import logger
from util import RedisOpt

# TaskCategoryOpt.save_task_category(category=1, name=u'facebook自动养号', processor='fb_auto_feed')
# TaskCategoryOpt.save_task_category(category=2, name=u'facebook刷好评', processor='fb_click_farming')
# TaskCategoryOpt.save_task_category(category=3, name=u'facebook登录浏览', processor='fb_login')
# TaskCategoryOpt.save_task_category(category=4, name=u'facebook点赞', processor='fb_thumb')
# TaskCategoryOpt.save_task_category(category=5, name=u'facebook发表评论', processor='fb_comment')
# TaskCategoryOpt.save_task_category(category=6, name=u'facebook发表状态', processor='fb_post')
# TaskCategoryOpt.save_task_category(category=7, name=u'facebook聊天', processor='fb_chat')
# TaskCategoryOpt.save_task_category(category=8, name=u'facebook编辑个人信息', processor='fb_edit')


PROCESSOR_MAP = {
    'fb_auto_feed': 'tasks.tasks.fb_auto_feed',
    'fb_click_farming': 'tasks.tasks.fb_click_farming',
    # 'fb_login': 'tasks.tasks.fb_login',
    # 'fb_thumb': 'tasks.task.fb_thumb',
    # 'fb_comment': 'tasks.task.fb_comment'
}


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


def dispatch_processor(processor_name: str, inputs: dict)->bool:
    """

    :param processor_name:
    :param inputs:
    :return:
    """
    logger.info('dispatch_processor, processor_name={}'.format(dispatch_processor))
    agent_queue_name = inputs.get('agent_queue_name', 'default')
    task_id = inputs.get('task_id', '')
    account_id = inputs.get('account_id', '')
    agent_id = inputs.get('agent_id', '')
    if not all([task_id, account_id]):
        logger.error('params error in dispatch_processor.')
        return False

    if agent_queue_name:
        celery_task_name = PROCESSOR_MAP.get(processor_name)
        logger.info('dispatch_processor, send task name={}, queue={}, task id={}, account id={}'.format(celery_task_name, agent_queue_name, task_id, account_id))
        track = app.send_task(
            celery_task_name,
            args=(inputs, ),
            queue=agent_queue_name,
            routing_key=agent_queue_name
        )

        JobOpt.save_job(task_id, account_id, agent_id=agent_id, track_id=track.id, status='running')
        job_dict = {'task': task_id, 'account': account_id, 'agent': agent_id, 'status': 'running', 'track_id': track.id}

        RedisOpt.push_object('job_list', json.dumps(job_dict))
        # try:
        #     track.get(on_message=on_task_message, propagate=False, interval=1, timeout=1)
        # except Exception:
        #     logger.warning(111111111)

        # 任务被分解并分发到任务队列了
        # TaskOpt.set_task_status(task_id, status='running')
    else:
        logger.error('can not dispatch processor by agent_queue_name')
        logger.error('can not dispatch processor by agent_queue_name')
        return False

    return True

