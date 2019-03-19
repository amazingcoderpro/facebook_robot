#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-16
# Function:


from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Table, ForeignKey)
from sqlalchemy.orm import relationship
from db.basic import Base, metadata, engine


TASK_STATUS = {-1: "pending", 0: "failed", 1: "succeed", 2: "running", 3: "pausing"}
TASK_CATEGORY = {0: "feed account", 1: "click farming"}


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(255), unique=True)
    password = Column(String(255))
    # 用户身份，0-普通用户，1-管理员
    category = Column(Integer, default=0, server_default='0')


class Scheduler(Base):
    __tablename__ = 'scheduler'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 0-立即执行（只执行一次）， 1-间隔执行并不立即开始（间隔一定时间后开始执行，并按设定的间隔周期执行下去） 2-间隔执行，但立即开始， 3-定时执行，指定时间执行
    category = Column(Integer, default=0, server_default='0')
    interval = Column(Integer, default=0, server_default='0')       # 间隔时长， 单位秒
    date = Column(DateTime(3))       # 定时执行时需要指定，如2019-03-31 13:30:30

    def __repr__(self):
        return "id:{}, category:{}, interval:{}, date:{}. ".format(
            self.id, self.category, self.interval, self.date)


task_account_group_table = Table(
    'task_account_group', Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('task_id', Integer, ForeignKey("task.id")),
    Column('account_id', Integer, ForeignKey("account.id")),
    Column('aps_id', String(100))   ## 这个是在APScheduler中调度时的任务id, 用以暂停、重启、终止等 操作,一个任务+一个账号构成一个唯一的task
)


class TaskAccountGroup(Base):
    # __tablename__ = 'task_account_group'
    # task_id = Column(Integer, ForeignKey("task.id"))
    # account_id = Column(Integer, ForeignKey("account.id"))
    __table__ = task_account_group_table


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), default='', server_default='')

    # 任务类型， 0-养账号，1-刷好评
    category = Column(Integer, default=0, server_default='0')

    # 任务状态， -1-pending, 0-failed, 1-succeed, 2-running, 3-pausing
    status = Column(Integer, default=-1, server_default='-1')

    # 任务的创建者
    creator = Column(Integer, ForeignKey('user.id'))

    # 任务调度规则
    scheduler = Column(Integer, ForeignKey('scheduler.id'))

    # 一个任务同时占用多个账号
    accounts = relationship('Account',
                            secondary=task_account_group_table)#,
                            # back_populates='parents')

    description = Column(String(2048), default='', server_default='')
    result = Column(String(2048), default='', server_default='')

    def category_str(self):
        return TASK_CATEGORY.get(self.category, "unknown")

    def status_str(self):
        return TASK_STATUS.get(self.status, "unknown")

    def accounts_list(self):
        return [acc.account for acc in self.accounts]

    def __repr__(self):
        return "id:{}, name:{}, category:{}, status:{}, creator:{}, scheduler:{}, accounts:{}, description:{}, " \
               "errors:{}. ".format(self.id, self.name, "{}-{}".format(self.category, self.category_str()),
                                    "{}-{}".format(self.status, self.status_str()), self.creator, self.scheduler,
                                    self.accounts_list(), self.description, self.result)


class Job(Base):
    __tablename__ = 'job'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(255))
    password = Column(String(255))
    task = Column(Integer, ForeignKey('task.id'))
    # -1-pending, 0-failed, 1-succeed, 2-running
    status = Column(Integer, default=-1, server_default='-1')
    start_time = Column(DateTime(3))
    result = Column(String(2048), default='', server_default='')

    def __repr__(self):
        return "id:{}, task_id:{}, account:{}, password:{}, start_time:{}, status:{}, result:{}. ".format(
            self.id, self.task, self.account, self.password, self.start_time, self.status, self.result)


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 该账号所属类别，0--facebook账号，1--twitter账号， 2--Ins账号
    category = Column(Integer, default=0, server_default='0')
    account = Column(String(255))
    password = Column(String(255))
    email = Column(String(255), default='', server_default='')
    email_pwd = Column(String(255))
    gender = Column(Integer, default=0, server_default='0')
    birthday = Column(String(100), default='', server_default='')
    national_id = Column(String(100), default='', server_default='')
    register_time = Column(String(100), default='', server_default='')
    name = Column(String(100), default='', server_default='')
    profile_id = Column(String(100), default='', server_default='')
    # 0-可用，1-被封,2-需要验证，3-其他问题
    status = Column(Integer, default=0, server_default='0')
    # 每个账号都应该隶属于某个人员，以方便权限管理
    owner = Column(Integer, ForeignKey('user.id'))
    usage = Column(Integer, default=0, server_default='0')   # 0-通用， 1-仅养号，2-仅刷单
    profile_path = Column(String(255), default='', server_default='')
    last_login = Column(DateTime(3))
    last_post = Column(DateTime(3))
    last_chat = Column(DateTime(3))
    last_farming = Column(DateTime(3))
    last_comment = Column(DateTime(3))
    last_edit = Column(DateTime(3))
    # 一个账号有可能同是被多个任务占用，逻辑上是可以的， 但实际操作上应该尽量避免此种情况，以规避多IP同时登录带来的封号风险
    tasks = relationship("Task",
                         secondary=task_account_group_table)#,
                         # back_populates='children')

    def __repr__(self):
        return "id:{}, account:{}, password:{}, email={}, email_pwd:{}, gender:{}, birthday:{}, national_id:{}, " \
               "register_time:{}, name:{}, profile_id:{}, status:{}, owner:{}, usage:{}, last_login:{}, last_post:{}, " \
               "las_chat:{}, last_comment:{}, last_farming:{}, last_edit:{}, tasks:{}, profile_path:{}. ".format(
                self.id, self.account,self.password, self.email, self.email_pwd, self.gender, self.birthday,
                self.national_id, self.register_time, self.name, self.profile_id, self.status, self.owner,
                self.usage, self.last_login, self.last_post, self.last_chat, self.last_comment, self.last_farming,
                self.last_edit, self.tasks, self.profile_path)


if __name__ == '__main__':
    while 1:
        res = input("What do you want to do, create or drop? \n")
        if res == 'drop':
            res = input("Are you sure? \n")
            if res.lower().startswith('y'):
                Base.metadata.drop_all(engine)
            break
        elif res == 'create':
            Base.metadata.create_all(engine)
            break
        elif res == 'exit':
            break
        else:
            pass

    print("finished.")
