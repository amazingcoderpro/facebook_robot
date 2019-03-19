#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-16
# Function: 


import datetime
from sqlalchemy import or_, and_
from db.basic import db_session
from db.models import Scheduler, Account, User, Task, TaskAccountGroup, Job


class SchedulerOpt:
    @classmethod
    def save_scheduler(cls, category=0, interval=0, date=datetime.datetime.now()):
        sch = Scheduler()
        sch.category = category
        sch.interval = interval
        sch.date = date
        db_session.add(sch)
        db_session.commit()
        return True

    @classmethod
    def add_scheduler(cls, scheduler):
        if isinstance(scheduler, Scheduler):
            db_session.add(scheduler)
            db_session.commit()
            return True

        return False

    @classmethod
    def get_scheduler(cls, id):
        return db_session.query(Scheduler).filter(Scheduler.id == id).first()


class UserOpt:
    @classmethod
    def save_user(cls, account, password, category=0):
        user = User()
        user.account = account
        user.password = password
        user.category = category
        db_session.add(user)
        db_session.commit()

    @classmethod
    def is_user_exist(cls, account):
        user = db_session.query(User).filter(User.account == account).first()
        if user:
            return True
        else:
            return False

    @classmethod
    def check_user(cls, account, password):
        user = db_session.query(User).filter(and_(User.account == account, User.password == password)).first()
        if user:
            return True
        else:
            return False


class AccountOpt:
    @classmethod
    def save_account(cls, account, password, owner, **kwargs):
        acc = Account()
        acc.account = account
        acc.password = password
        acc.owner = owner
        for k, v in kwargs.items():
            if hasattr(acc, k):
                setattr(acc, k, v)

        db_session.add(acc)
        db_session.commit()

    @classmethod
    def add_account(cls, account):
        if isinstance(account, Account):
            db_session.add(account)
            db_session.commit()
            return True

        return False

    @classmethod
    def get_account(cls, id):
        return db_session.query(Account).filter(Account.id == id).first()


class TaskOpt:
    @classmethod
    def get_all_tasks(cls):
        return db_session.query(Task).all()

    @classmethod
    def get_all_pending_task(cls):
        return db_session.query(Task).filter(Task.status == -1).all()

    @classmethod
    def get_all_running_task(cls):
        return db_session.query(Task).filter(Task.status == 2).all()

    @classmethod
    def get_all_need_restart_task(cls):
        return db_session.query(Task).filter(or_(Task.status == -1, Task.status == 2)).all()

    @classmethod
    def get_all_succeed_task(cls):
        return db_session.query(Task.id, Task.name, Task.status, Task.category, Task.creator).filter(
            Task.status == 1).all()

    @classmethod
    def get_all_failed_task(cls):
        return db_session.query(Task.id, Task.name, Task.status, Task.category, Task.creator).filter(
            Task.status == 0).all()

    @classmethod
    def save_task(cls, category, creator_id, scheduler_id, account_ids, **kwargs):
        task = Task()
        task.category = category
        task.creator = creator_id
        task.scheduler = scheduler_id
        for k, v in kwargs.items():
            if hasattr(task, k):
                setattr(task, k, v)

        db_session.add(task)
        db_session.commit()
        for acc_id in account_ids:
            tag = TaskAccountGroup()
            tag.task_id = task.id
            tag.account_id = acc_id
            db_session.add(tag)
        db_session.commit()
        return True

    @classmethod
    def add_task(cls, task):
        if isinstance(task, Task):
            db_session.add(task)
            db_session.commit()
            return True

        return False

    @classmethod
    def set_task_status(cls, id, status):
        task = db_session.query(Task).filter(Task.id == id).first()
        if task:
            task.status = status
            db_session.commit()
            return True

        return False

    @classmethod
    def set_task_result(cls, id, result):
        task = db_session.query(Task).filter(Task.id == id).first()
        if task:
            task.result = result
            db_session.commit()
            return True

        return False

    @classmethod
    def get_task_scheduler(cls, id):
        task = db_session.query(Task.scheduler).filter(Task.id == id).first()
        if task:
            return SchedulerOpt.get_scheduler(task.scheduler)

        return None


class TaskAccountGroupOpt:
    @classmethod
    def get_account_tasks(cls, account_id):
        return db_session.query(TaskAccountGroup).filter(TaskAccountGroup.account_id == account_id).all()

    @classmethod
    def get_aps_ids_by_task(cls, task_id):
        return db_session.query(TaskAccountGroup).filter(TaskAccountGroup.task_id == task_id).all()

    @classmethod
    def get_aps_id(cls, task_id, account_id):
        return db_session.query(TaskAccountGroup).filter(and_(TaskAccountGroup.task_id == task_id,
                                                              TaskAccountGroup.account_id == account_id)).first()

    @classmethod
    def set_aps_id(cls, task_id, account_id, aps_id):
        tag = db_session.query(TaskAccountGroup).filter(and_(TaskAccountGroup.task_id == task_id,
                                                             TaskAccountGroup.account_id == account_id)).first()
        if tag:
            tag.aps_id = aps_id
            db_session.commit()
            return True

        return False


class JobOpt:
    @classmethod
    def save_job(cls, task_id, account, password, status=-1, start_time=datetime.datetime.now()):
        job = Job()
        job.task = task_id
        job.account = account
        job.password = password
        job.status = status
        job.start_time = start_time
        db_session.add(job)
        db_session.commit()
        return job

    @classmethod
    def add_job(cls, job):
        if isinstance(job, Job):
            db_session.add(job)
            db_session.commit()
            return True

        return False

    @classmethod
    def get_job_by_task_id(cls, task_id):
        return db_session.query(Job).filter(Job.task == task_id).all()

    @classmethod
    def set_job_status(cls, id, status):
        job = db_session.query(Job).filter(Job.id == id).first()
        if job:
            job.status = status
            db_session.commit()
            return True

        return False

    @classmethod
    def set_job_result(cls, id, result):
        job = db_session.query(Job).filter(Job.id == id).first()
        if job:
            job.result = result
            db_session.commit()
            return True

        return False


def insert_test_data():
    UserOpt.save_user('test', 'test', 0)
    UserOpt.save_user('admin', 'admin', 1)
    SchedulerOpt.save_scheduler()
    SchedulerOpt.save_scheduler(1, interval=20)
    SchedulerOpt.save_scheduler(2, interval=20)
    AccountOpt.save_account("codynr4nzxh@outlook.com", 'qVhgldHmgp', owner=1)
    AccountOpt.save_account("eddykkqf56@outlook.com", 'nYGcEXNjGY', owner=2)
    AccountOpt.save_account("yakovlev.vinsent@bk.ru", "Ogec1eOAFA", owner=1)
    TaskOpt.save_task(0, 1, 1, [1, 2])


def show_test_data():
    TaskOpt.save_task(0, 2, 2, [1, 2])
    tasks = TaskOpt.get_all_need_restart_task()
    for task in tasks:
        print("tasks = {}".format(task))
        for acc in task.accounts:
            print(acc.account)

    acc = AccountOpt.get_account(id=4)
    print(acc)

    TaskOpt.set_task_status(1, 1)
    res = TaskOpt.get_all_need_restart_task()
    for t in res:
        print(t)

    res = TaskOpt.get_all_running_task()
    for t in res:
        print(t)

    JobOpt.save_job(1, "a", "b")
    jobs = JobOpt.get_job_by_task_id(1)
    for j in jobs:
        print(j)


if __name__ == '__main__':
    insert_test_data()
    show_test_data()






