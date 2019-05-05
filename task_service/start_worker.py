#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: worker注册

"""
负责worker的注册和启动
"""
import os
import sys
import datetime
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
worker_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)) + '/logs', 'celery_{}.log'.format(datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")))
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
#celery -A start_worker -Q default,China,American,Japan worker -l info -c 4 -Ofair -f logs/celery.log -env pro

if __name__ == '__main__':
    import subprocess
    env = "pro"
    save_log = True
    queue_names = "default"
    concurrent = 4
    input_env = input("Please input execute environment(pro/test):")
    if input_env and input_env in ["pro", 'test']:
        env = input_env
    else:
        print("use default env: {}".format(env))

    queue_names_input = input("Please input queue name(separate multiples with commas):")
    if queue_names_input:
        queue_names = queue_names_input
        queue_names = queue_names.replace(' ', '')
    else:
        print("use default queue: {}".format(queue_names))

    concurrent_input = input("Please input concurrent numbers(default:4):")
    try:
        concurrent = int(concurrent_input)
    except:
        print("use default concurrent: {}".format(concurrent))

    is_log_file = input("Is save log to file(yes/no):")
    if is_log_file and is_log_file in ["yes", 'no']:
        if "no" in is_log_file:
            save_log = False
            print("don't save log in file")
        else:
            print("Save log in file")
    else:
        print("Save log in file")

    if save_log:
        celery_cmd = "celery -A start_worker -Q {} worker -l info -c {} -Ofair -f logs/celery_{}.log -env {}".format(
            queue_names, concurrent, datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S"), env)
    else:
        celery_cmd = "celery -A start_worker -Q {} worker -l info -c {} -Ofair -env {}".format(
            queue_names, concurrent, env)

    print("Celery cmd: {}".format(celery_cmd))
    subprocess.call(celery_cmd, shell=True)

