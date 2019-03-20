#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 


import os
from datetime import timedelta
from celery import Celery, platforms
from kombu import Exchange, Queue
from config import get_broker_and_backend

# platforms.C_FORCE_ROOT = True

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
    CELERY_QUEUEs=(
        Queue('agent1', exchange=Exchange('agent1', type='direct'),
              routing_key='for_agent1'),
        Queue('agent2', exchange=Exchange('agent2', type='direct'),
              routing_key='for_agent2'),
    )
)

# CELERYBEAT_SCHEDULE={
#     'feed_account_task': {
#         'task': 'tasks.feed_account.execute_feed_account',
#         'schedule': timedelta(hours=4),
#         'options': {'queue': 'feed_account_queue', 'routing_key': 'for_feed_account'}
#     }
# }
#celery -A tasks.workers -Q feed_account_queue worker -l info -c 1 -Ofair
