#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-27
# Function: 

import redis
from config import get_redis_args
redis_info = get_redis_args()
pool_broker = redis.ConnectionPool(host=redis_info.get('host', '127.0.0.1'), port=redis_info.get('port', 6379),
                                   password=redis_info.get('password'), db=redis_info.get('broker', 5), decode_responses=True)
pool_backend = redis.ConnectionPool(host=redis_info.get('host'), port=redis_info.get('port'),
                                    password=redis_info.get('password'), db=redis_info.get('backend', 6), decode_responses=True)
pool_cache = redis.ConnectionPool(host=redis_info.get('host'), port=redis_info.get('port'),
                                    password=redis_info.get('password'), db=redis_info.get('cache', 1), decode_responses=True)


class RedisOpt:
    broker_db = redis.Redis(connection_pool=pool_broker)
    backend_db = redis.Redis(connection_pool=pool_backend)
    cache_db = redis.Redis(connection_pool=pool_cache)

    @classmethod
    def read_broker(cls, key):
        return cls.broker_db.lrange(key, 0, -1)

    @classmethod
    def read_backend(cls, key):
        return cls.backend_db.get(key)

    @classmethod
    def pop_all_backend(cls, pattern='*', is_delete=False):
        results = []
        keys = cls.backend_db.keys(pattern)
        for key in keys:
            results.append(cls.backend_db.get(key))
            if is_delete:
                cls.backend_db.delete(key)
        return results

    @classmethod
    def delete_backend(cls, pattern='*'):
        keys = cls.backend_db.keys(pattern)
        for key in keys:
            cls.backend_db.delete(key)


    @classmethod
    def push_object(cls, key, value):
        cls.cache_db.rpush(key, value)

    @classmethod
    def pop_object(cls, key):
        return cls.cache_db.lpop(key)

    @classmethod
    def pop_all(cls, key, is_delete=True):
        length = cls.cache_db.llen(key)
        res = cls.cache_db.lrange(key, 0, length)
        if is_delete:
            cls.cache_db.ltrim(key, length, -1)
        return res

    @classmethod
    def write_object(cls, key, value):
        return cls.cache_db.set(key, value)

    @classmethod
    def read_object(cls, key):
        if key in cls.cache_db.keys():
            return cls.cache_db.get(key)
        else:
            return -1

    @classmethod
    def clean_cache_db(cls):
        keys = cls.cache_db.keys()
        for key in keys:
            cls.cache_db.delete(key)

    @classmethod
    def clean_backend_db(cls):
        keys = cls.backend_db.keys()
        if keys:
            return cls.backend_db.delete(*keys)

    @classmethod
    def clean_broker_db(cls):
        keys = cls.broker_db.keys()
        if keys:
            return cls.broker_db.delete(*keys)


if __name__ == '__main__':
    rpt = RedisOpt()
    print(rpt.read_broker('China1'))
    rpt.push_object('jobs', str({'name': 5, 'st': '2015455'}))
    print(rpt.pop_object('jobs'))