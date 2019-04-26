#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: worker注册

"""
负责worker的注册和启动
"""
import os
import sys
from datetime import timedelta
from celery import Celery, platforms
from kombu import Exchange, Queue
from config import load_config, get_broker_and_backend

# platforms.C_FORCE_ROOT = True

env = 'pro'
for idx, arg in enumerate(sys.argv):
    if arg == '-env':
        env = sys.argv[idx+1]
        sys.argv.pop(idx)
        sys.argv.pop(idx)
        break

load_config(env=env)

tasks = [
    'tasks.tasks'
]

broker, backend = get_broker_and_backend()
worker_log_path = ''
beat_log_path = ''
worker_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/logs', 'celery.log')
beat_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/logs', 'beat.log')


app = Celery('facebook_task', include=tasks, broker=broker, backend=backend)
app.conf.update(
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,
    CELERY_LOG_FILE=worker_log_path,
    CELERYBEAT_LOG_FILE=beat_log_path,
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    # CELERYD_MAX_TASKS_PER_CHILD=2,
    # CELERYD_TASK_SOFT_TIME_LIMIT=99999,
    CELERY_QUEUES=(
        Queue('default', exchange=Exchange('default', type='direct'),
              routing_key='default'),
        Queue('China', exchange=Exchange('China', type='direct'),
              routing_key='China'),
    )
)

# CELERYBEAT_SCHEDULE={
#     'feed_account_task': {
#         'task': 'tasks.feed_account.execute_feed_account',
#         'schedule': timedelta(hours=4),
#         'options': {'queue': 'feed_account_queue', 'routing_key': 'for_feed_account'}
#     }
# }
#celery -A tasks.workers -Q default,China,American,Japan worker -l info -c 4 -Ofair -f logs/celery.log -env pro
