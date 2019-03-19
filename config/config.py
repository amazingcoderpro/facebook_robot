#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-15
# Function: 


import os
from yaml import load, FullLoader

config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, encoding='utf-8') as f:
    content = f.read()

cfg = load(content, Loader=FullLoader)


def get_redis_args():
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
    return cfg.get('db')
