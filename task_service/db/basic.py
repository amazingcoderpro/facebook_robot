#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-16
# Function: 

import threading
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from config import get_db_args


def get_engine():
    args = get_db_args()
    connect_str = "{}+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(
        args['db_type'], args['user'], args['password'],
        args['host'], args['port'], args['db_name']
    )
    eng = create_engine(connect_str, encoding='utf-8', pool_size=1000, pool_recycle=7200,
                        pool_pre_ping=True, max_overflow=100, pool_timeout=1200, pool_reset_on_return='commit')
    return eng


engine = get_engine()
Base = declarative_base()

Session = sessionmaker(bind=engine)
db_session = Session()

session_factory = sessionmaker(bind=engine)
ScopedSession = scoped_session(session_factory)
db_scoped_session = ScopedSession()


metadata = MetaData(get_engine())
db_lock = threading.RLock()

__all__ = ['engine', 'Base', 'db_session', 'metadata', 'db_lock', 'db_scoped_session', 'ScopedSession']

# ss = ScopedSession()
# ss2 = ScopedSession()
# if ss is ss2:
#     print(1)
# ScopedSession.remove()
#
# if ss is ss2:
#     print(1)
#
# print(ss2.close())
# if ss2:
#     print(3)
#
# ss3 = ScopedSession()
# if ss is ss3:
#     print(2)
#
# ds = db_session
# ds2=db_session
# print(ds)
# ds.close()
# if ds is ds2:
#     print(33)
