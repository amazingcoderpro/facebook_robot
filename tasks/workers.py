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
    'tasks.feed_account', 'tasks.click_farming'
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
        Queue('feed_account_queue', exchange=Exchange('feed_account', type='direct'),
              routing_key='for_feed_account'),
        Queue('click_farming_queue', exchange=Exchange('click_farming_queue', type='direct'),
              routing_key='for_click_farming'),
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
