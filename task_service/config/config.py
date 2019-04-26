#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 


import os
import logging
import json
import random
from yaml import load, FullLoader
from log_config import log_config

cfg = None
facebook_cfg = None
log_config.init_log_config(file_prefix='facebook_auto', console_level=logging.INFO, backup_count=50)
logger = logging.getLogger()
environment = 'pro'


def load_config(env='pro'):
    global cfg
    if cfg:
        return True

    try:
        if env == 'test':
            config_file = 'config_test.yaml'
            global environment
            environment = 'test'
        else:
            config_file = 'config.yaml'

        config_path = os.path.join(os.path.dirname(__file__), config_file)
        logger.info("load config: {}".format(config_path))
        with open(config_path, encoding='utf-8') as f:
            content = f.read()

        cfg = load(content, Loader=FullLoader)

        load_facebook_json()

    except Exception as e:
        logger.exception('load config catch exception, e={}'.format(e))
        return False

    return True


def load_facebook_json():
    global facebook_cfg
    facebook_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resource//facebook.json')
    with open(facebook_json, encoding='utf-8') as f:
        fb_json = f.read()
    facebook_cfg = json.loads(fb_json)


def get_redis_args():
    if not cfg:
        load_config()
    return cfg.get('redis')


def get_broker_and_backend():
    redis_info = cfg.get('redis')
    password = redis_info.get('password')
    sentinel_args = redis_info.get('sentinel', '')
    db = redis_info.get('broker', 5)
    if sentinel_args:
        broker_url = ";".join('sentinel://:{}@{}:{}/{}'.format(password, sentinel['host'], sentinel['port'], db) for
                              sentinel in sentinel_args)
        return broker_url
    else:
        host = redis_info.get('host')
        port = redis_info.get('port')
        backend_db = redis_info.get('backend', 6)
        broker_url = 'redis://:{}@{}:{}/{}'.format(password, host, port, db)
        backend_url = 'redis://:{}@{}:{}/{}'.format(password, host, port, backend_db)
        return broker_url, backend_url


def get_db_args():
    if not cfg:
        load_config()
    return cfg.get('db')


def get_account_args():
    if not cfg:
        load_config()
    return cfg.get('account')


def get_task_args():
    return cfg.get('task')


def get_system_args():
    return cfg.get('system')


def get_fb_friend_keys(limit=1):
    fks = facebook_cfg.get('friend_search_keys')
    if limit <= 0:
        return fks
    else:
        return random.sample(fks, limit)


def get_fb_posts(limit=1):
    posts = facebook_cfg.get('posts')
    if limit <= 0:
        return posts
    else:
        return random.sample(posts, limit)


def get_fb_chat_msgs(limit=1):
    msgs = facebook_cfg.get('chat_msgs')
    if limit <= 0:
        return msgs
    else:
        return random.sample(msgs, limit)


def get_support_args():
    if not cfg:
        load_config()
    return cfg.get('support')


def get_environment():
    global environment
    return environment
