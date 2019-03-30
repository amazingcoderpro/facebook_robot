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
    eng = create_engine(connect_str, encoding='utf-8', pool_size=100, pool_recycle=60,
                        pool_pre_ping=True, max_overflow=10, pool_timeout=120, pool_reset_on_return='commit')
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
