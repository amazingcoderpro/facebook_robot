#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-16
# Function: 对所有数据库表常用操作进行封装, 降低其他模块与数据操作之间的耦合


import datetime
from config import logger
from db.basic import db_session, db_lock
from sqlalchemy import and_
from db.models import (Scheduler, Account, User, Task, TaskAccountGroup,
                       Job, TaskCategory, UserCategory, AccountCategory, Agent, FingerPrint)


class BaseOpt:
    db_session = None

    def __init__(self, session=None):
        if session:
            BaseOpt.db_session = session
        else:
            BaseOpt.db_session = db_session


class SchedulerOpt(BaseOpt):
    """
    Scheduler表处理类
    """
    @classmethod
    def save_scheduler(cls, mode=0, interval=600, start_date=datetime.datetime.now(), end_date=None):
        sch = Scheduler()
        sch.mode = mode
        sch.interval = interval
        sch.start_date = start_date
        sch.end_date = end_date
        db_session.add(sch)
        db_session.commit()
        return sch

    @classmethod
    def add_scheduler(cls, scheduler):
        if isinstance(scheduler, Scheduler):
            db_session.add(scheduler)
            db_session.commit()
            return True

        return False

    @classmethod
    def get_scheduler(cls, scheduler_id):
        return db_session.query(Scheduler.mode, Scheduler.interval, Scheduler.start_date, Scheduler.end_date).filter(Scheduler.id == scheduler_id).first()


class UserOpt:
    @classmethod
    def save_user(cls, category=0, enable_tasks='', token=''):
        user = User()
        user.category = category
        user.enable_tasks = enable_tasks
        user.token = token
        db_session.add(user)
        db_session.commit()
        return user

    # @classmethod
    # def is_user_exist(cls, account):
    #     user = db_session.query(User).filter(User.account == account).first()
    #     if user:
    #         return True
    #     else:
    #         return False
    #
    # @classmethod
    # def check_user(cls, account, password):
    #     user = db_session.query(User).filter(and_(User.account == account, User.password == password)).first()
    #     if user:
    #         return True
    #     else:
    #         return False


class UserCategoryOpt:
    @classmethod
    def save_user_category(cls, category, name, description):
        uc = UserCategory()
        uc.category = category
        uc.name = name
        uc.description = description
        db_session.add(uc)
        db_session.commit()
        return uc


class AccountCategoryOpt:
    @classmethod
    def save_account_category(cls, category, name=''):
        acg = AccountCategory()
        acg.category = category
        acg.name = name
        db_session.add(acg)
        db_session.commit()
        return acg


class AccountOpt:
    @classmethod
    def save_account(cls, account, password, category, owner, **kwargs):
        acc = Account()
        acc.account = account
        acc.password = password
        acc.category = category
        acc.owner = owner
        for k, v in kwargs.items():
            if hasattr(acc, k):
                setattr(acc, k, v)

        db_session.add(acc)
        db_session.commit()
        return acc

    @classmethod
    def add_account(cls, account):
        if isinstance(account, Account):
            db_session.add(account)
            db_session.commit()
            return True

        return False

    @classmethod
    def get_account(cls, account_id):
        return db_session.query(Account).filter(Account.id == account_id).first()

    @classmethod
    def get_all_accounts(cls):
        return db_session.query(Account).all()

    @classmethod
    def add_account_using_counts(cls, account_id):
        acc = db_session.query(Account).filter(Account.id == account_id).first()
        if acc:
            acc.using += 1


class TaskOpt:
    @classmethod
    def get_all_tasks(cls):
        return db_session.query(Task).all()

    @classmethod
    def get_all_pending_task(cls):
        return db_session.query(Task).filter(Task.status == 'pending').all()

    @classmethod
    def get_all_running_task(cls):
        return db_session.query(Task).filter(Task.status == 'running').all()

    @classmethod
    def get_all_pausing_task(cls):
        return db_session.query(Task).filter(Task.status == 'pausing').all()

    @classmethod
    def get_all_new_task(cls):
        return db_session.query(Task.id, Task.status).filter(Task.status == 'new').all()

    @classmethod
    def get_all_need_check_task(cls, last_time):
        """
        获取所有需要检查的任务（即状态可能被用户修改的任务）
        :return:
        """
        return db_session.query(Task.id, Task.status, Task.last_update)\
            .filter(and_(Task.status.in_(('pausing', 'running', 'cancelled')), Task.last_update >= last_time)).all()

    @classmethod
    def get_all_need_restart_task(cls):
        """
        主要用于服务器宕机后重新启动时获取所有需要启动的任务,包括pending状态和running状态的
        :return:
        """
        return db_session.query(Task.id, Task.status).filter(Task.status.notin_(('succeed', 'failed', 'cancelled'))).all()

    @classmethod
    def get_all_succeed_task(cls):
        return db_session.query().filter(Task.status == 'succeed').all()

    @classmethod
    def get_all_failed_task(cls):
        return db_session.query().filter(Task.status == 'failed').all()

    @classmethod
    def save_task(cls, name, category_id, creator_id, scheduler_id, account_ids, **kwargs):
        task = Task()
        task.name = name
        task.category = category_id
        task.creator = creator_id
        task.scheduler = scheduler_id
        task.real_accounts_num = task.accounts_num = len(account_ids)
        for k, v in kwargs.items():
            if hasattr(task, k):
                setattr(task, k, v)

        task.last_update = datetime.datetime.now()
        db_session.add(task)
        db_session.commit()

        # task.accounts = account_ids   # account_ids只是id列表,不能赋值
        for acc_id in account_ids:
            tag = TaskAccountGroup()
            tag.task_id = task.id
            tag.account_id = acc_id
            db_session.add(tag)

        db_session.commit()
        return task

    @classmethod
    def add_task(cls, task):
        if isinstance(task, Task):
            task.last_update = datetime.datetime.now()
            db_session.add(task)
            db_session.commit()
            return True

        return False

    @classmethod
    def set_task_status(cls, session, task_id, status, aps_id=''):
        if not session:
            session = db_session
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            if task.status != status:
                # 第一次变成pending, 即已经加入定时处理中, 可设置aps_id
                if status == 'pending':
                    task.aps_id = aps_id
                # 第一次变成running的时间即启动时间
                elif status == 'running':
                    logger.info('task begin running task id={}'.format(task_id))
                    task.start_time = datetime.datetime.now()
                elif status in ['succeed', 'failed']:
                    task.end_time = datetime.datetime.now()
                    # 只有结束是系统自动调度出来的,需要更新last_update字段，其他状态更新不需要,交由webserver
                    task.last_update = datetime.datetime.now()

                task.status = status
                session.commit()
            return True

        return False

    @classmethod
    def set_task_result(cls, task_id, result):
        task = db_session.query(Task).filter(Task.id == task_id).first()
        if task:
            task.result = result
            task.last_update = datetime.datetime.now()
            db_session.commit()
            return True

        return False

    @classmethod
    def get_task_by_task_id(cls, task_id):
        return db_session.query(Task).filter(Task.id == task_id).first()

    @classmethod
    def get_task_status_apsid(cls, task_id):
        return db_session.query(Task.status, Task.aps_id).filter(Task.id == task_id).first()

    @classmethod
    def get_aps_ids_by_task_id(cls, task_id):
        aps_id = db_session.query(Task.aps_id).filter(Task.id == task_id).first()
        if aps_id:
            return aps_id[0]
        return ''


class TaskAccountGroupOpt:
    @classmethod
    def get_account_tasks(cls, account_id):
        """
        查询该账号关联的所有任务
        :param account_id:
        :return: 返回所有关联的task id
        """
        tags = db_session.query(TaskAccountGroup).filter(TaskAccountGroup.account_id == account_id).all()
        task_ids = []
        for t in tags:
            task_ids.append(t.task_id)

        return task_ids

    @classmethod
    def set_aps_status_by_task(cls, task_id, status):
        tags = db_session.query(TaskAccountGroup).filter(TaskAccountGroup.task_id == task_id).all()
        for tag in tags:
            tag.status = status

    @classmethod
    def set_aps_status(cls, aps_id, status):
        tag = db_session.query(TaskAccountGroup).filter(TaskAccountGroup.aps_id == aps_id).first()
        if tag:
            tag.status = status
            db_session.commit()
            return True

        return False


class JobOpt:
    @classmethod
    def save_job(cls, session, task_id, account_id, agent_id, track_id='', status='pending'):
        # status-- -1-pending, 0-failed, 1-succeed, 2-running
        job = Job()
        job.task = task_id
        job.account = account_id
        job.agent = agent_id
        job.status = status
        job.track_id = track_id
        if status == 'running':
            job.start_time = datetime.datetime.now()

        session.add(job)
        session.commit()
        return job

    @classmethod
    def save_jobs(cls, jobs):
        for job in jobs:
            if isinstance(job, dict):
                job = Job().dict2Job(job)

            if job.status == 'running':
                job.start_time = datetime.datetime.now()

            db_session.add(job)

        db_lock.acquire()
        db_session.commit()
        db_lock.release()
        return True

    @classmethod
    def add_job(cls, job):
        if isinstance(job, Job):
            db_session.add(job)
            db_session.commit()
            return True

        return False

    @classmethod
    def get_jobs_by_task_id(cls, task_id):
        return db_session.query(Job.status).filter(Job.task == task_id).all()

    @classmethod
    def count_jobs_by_agent_id(cls, agent_id, status='running'):
        if status:
            return db_session.query(Job).filter(Job.agent == agent_id, Job.status == status).count()
        else:
            return db_session.query(Job).filter(Job.agent == agent_id).count()

    @classmethod
    def count_jobs_by_account_id(cls, account_id, status='running'):
        if status:
            return db_session.query(Job).filter(Job.account == account_id, Job.status == status).count()
        else:
            return db_session.query(Job).filter(Job.account == account_id).count()

    @classmethod
    def set_job_status(cls, job_id, status):
        job = db_session.query(Job).filter(Job.id == job_id).first()
        if job:
            if job.status != status:
                # 第一次变成running的时间即启动时间
                if status == 'running':
                    job.start_time = datetime.datetime.now()
                if status in ['success', 'failure']:
                    job.end_time = datetime.datetime.now()

                job.status = status
                db_session.commit()
            return True

        return False

    @classmethod
    def set_job_by_track_id(cls, track_id, status, result='', traceback=''):
        job = db_session.query(Job).filter(Job.track_id == track_id).first()
        if job:
            if job.status != status:
                # 第一次变成running的时间即启动时间
                if status == 'running':
                    job.start_time = datetime.datetime.now()
                if status in ['succeed', 'failed']:
                    job.end_time = datetime.datetime.now()

            job.result = result
            job.traceback = traceback
            job.status = status
            db_session.commit()
            return True

        return False

    @classmethod
    def set_job_by_track_ids(cls, track_ids, values):
        jobs = db_session.query(Job).filter(Job.track_id.in_(track_ids)).all()
        track_ids_copy = track_ids.copy()
        try:
            for job in jobs:
                track_ids.remove(job.track_id)
                value = values.get(job.track_id, {})
                new_status = value.get('status')
                new_result = value.get('result', '')
                new_traceback = value.get('traceback', '')
                if job.status != new_status:
                    # 第一次变成running的时间即启动时间
                    if new_status == 'running':
                        job.start_time = datetime.datetime.now()
                    if new_status in ['succeed', 'failed']:
                        job.end_time = datetime.datetime.now()

                    job.result = new_result
                    job.traceback = new_traceback
                    job.status = new_status
            db_session.commit()
        except:
            logger.exception('set_job_by_track_ids catch exception.')
            db_session.rollback()
            return track_ids_copy
        return track_ids

    @classmethod
    def set_job_result(cls, job_id, result):
        job = db_session.query(Job).filter(Job.id == job_id).first()
        if job:
            job.result = result
            db_session.commit()
            return True

        return False


# class JobActinsOpt:
#     @classmethod
#     def save_job_actions(cls, job_id, action_id, result=''):
#         jac = JobActions()
#         jac.job_id = job_id
#         jac.action_id = action_id
#         jac.result = result
#
#
# class ActionOpt:
#     @classmethod
#     def save_action(cls, name, depend_on=None):
#         action = Action()
#         action.name = name
#         action.depend_on = depend_on


class TaskCategoryOpt:
    @classmethod
    def save_task_category(cls, category, name, processor, configure='', description=''):
        tag = TaskCategory()
        tag.category = category
        tag.name = name
        tag.processor = processor
        tag.configure = configure
        tag.description = description
        db_session.add(tag)
        db_session.commit()
        return tag

    @classmethod
    def get_all_processor(cls):
        res = db_session.query(TaskCategory.processor).filter().distinct().all()
        return [r[0] for r in res]

    @classmethod
    def get_processor(cls, session, category):
        tcg = session.query(TaskCategory.processor).filter(TaskCategory.category == category).first()
        if tcg:
            return tcg[0]
        else:
            return None


class AgentOpt:
    @classmethod
    def save_agent(cls, area, queue_name='', status=0, config=''):
        agent = Agent()
        agent.status = status
        agent.area = area
        agent.queue_name = queue_name
        agent.config = config
        db_session.add(agent)
        db_session.commit()
        return agent

    @classmethod
    def get_agent_queue(cls, agent_id):
        res = db_session.query(Agent.queue).filter(Agent.id == agent_id).first()
        if res:
            return res[0]
        else:
            return None

    @classmethod
    def get_enable_agents(cls, session, status_order=True):
        if not session:
            session = db_session

        if status_order:
            return session.query(Agent).filter(Agent.status != -1).order_by(Agent.status).all()
        else:
            return session.query(Agent).filter(Agent.status != -1).all()


class FingerPrintOpt:
    @classmethod
    def save_finger_print(cls, name, value):
        fp = FingerPrint()
        fp.name = name
        fp.value = value
        db_session.add(fp)
        db_session.commit()
        return fp

import json

def init_db_data():
    """
    初始化各表基础配置数据,用于环境测试等
    :return:
    """
    # 初始化用户类别表
    # UserCategoryOpt.save_user_category(category=1, name='普通用户', description='可以创建部分或所有类型任务,但无权修改服务器资源')
    # UserCategoryOpt.save_user_category(category=2, name='管理员', description='可创建所有类型任务, 且可以管理服务器资源、修改服务器配置等')

    # 增加测试用户
    # UserOpt.save_user(account='user1', password='user1', category=1, enable_tasks='1;2;3', name='张三')
    # UserOpt.save_user(account='user2', password='user2', category=1, enable_tasks='4;5;6', name='李四')
    # UserOpt.save_user(account='admin', password='admin', category=2, enable_tasks='', name='大哥大')


    # 初始化任务类别表
    # 1--fb自动养账号, 2-fb刷广告好评, 3- fb仅登录浏览, 4- fb点赞, 5- fb发表评论, 6- fb post状态, 7- fb 聊天, 8- fb 编辑个人信息, 未完待续...
    # name: title:type(bool / int / float / str): default[:option1[ | option2[ | optionN]] [\r\n(new
    # line)]
    TaskCategoryOpt.save_task_category(category=1, name=u'facebook自动养号', processor='fb_auto_feed',
                                       configure='is_post:是否发布状态:bool:false\r\nis_add_friend:是否加好友:bool:false\r\npost_content:状态内容:string:good morning everyone!\r\nfriend_key:好友关键字:string:lady gaga')
    TaskCategoryOpt.save_task_category(category=2, name=u'facebook刷好评', processor='fb_click_farming', configure='browser_time:浏览时长:int:600:120|3600\r\nads_code:广告码:string:')
    TaskCategoryOpt.save_task_category(category=3, name=u'facebook登录浏览', processor='fb_login', configure='browser_time:浏览时长:int:600:120|3600')
    TaskCategoryOpt.save_task_category(category=4, name=u'facebook点赞', processor='fb_thumb')
    TaskCategoryOpt.save_task_category(category=5, name=u'facebook发表评论', processor='fb_comment')
    TaskCategoryOpt.save_task_category(category=6, name=u'facebook发表状态', processor='fb_post')
    TaskCategoryOpt.save_task_category(category=7, name=u'facebook聊天', processor='fb_chat')
    TaskCategoryOpt.save_task_category(category=8, name=u'facebook编辑个人信息', processor='fb_edit')

    # 初始化账号类别表
    # 该账号所属类别,1--facebook账号,2--twitter账号, 3--Ins账号
    AccountCategoryOpt.save_account_category(category=1, name=u'Facebook账号')
    AccountCategoryOpt.save_account_category(category=2, name=u'Twitter账号')
    AccountCategoryOpt.save_account_category(category=3, name=u'Instagram账号')


    # 增加任务计划
    # category: 0-立即执行（只执行一次）, 1-间隔执行并不立即开始（间隔一定时间后开始执行,并按设定的间隔周期执行下去） 2-间隔执行,但立即开始, 3-定时执行,指定时间执行
    SchedulerOpt.save_scheduler(mode=0)
    SchedulerOpt.save_scheduler(mode=1, interval=300, start_date=datetime.datetime.now() + datetime.timedelta(minutes=20))
    SchedulerOpt.save_scheduler(mode=1, interval=65,
                                end_date=datetime.datetime.now() + datetime.timedelta(minutes=20))
    SchedulerOpt.save_scheduler(mode=2, interval=60)
    SchedulerOpt.save_scheduler(mode=2, interval=70, end_date=datetime.datetime.now()+datetime.timedelta(hours=1))
    SchedulerOpt.save_scheduler(mode=3, start_date=datetime.datetime.now()+datetime.timedelta(hours=5))
    SchedulerOpt.save_scheduler(mode=2, start_date=datetime.datetime.now() + datetime.timedelta(hours=1),
                                end_date=datetime.datetime.now() + datetime.timedelta(hours=20))


    # FingerPrintOpt.save_finger_print('iPhone 6', value=json.dumps({'device': 'iPhone 6'}))
    FingerPrintOpt.save_finger_print('iPhone 6', value=json.dumps({'device': 'iPhone 6'}))
    FingerPrintOpt.save_finger_print('iPhone 7', value=json.dumps({'device': 'iPhone 7'}))
    FingerPrintOpt.save_finger_print('iPhone 8', value=json.dumps({'device': 'iPhone 8'}))
    FingerPrintOpt.save_finger_print('iPhone X', value=json.dumps({'device': 'iPhone X'}))
    FingerPrintOpt.save_finger_print('Nokia N9', value=json.dumps({'device': 'Nokia N9'}))
    FingerPrintOpt.save_finger_print('iPad Mini', value=json.dumps({'device': 'iPad Mini'}))
    FingerPrintOpt.save_finger_print('Nexus 6', value=json.dumps({'device': 'Nexus 6'}))
    FingerPrintOpt.save_finger_print('Galaxy Note 3', value=json.dumps({'device': 'Galaxy Note 3'}))

    # 添加账号
    produce_account()
    # AccountOpt.save_account(account='codynr4nzxh@outlook.com',
    #                         password='qVhgldHmgp', owner=1, category=1,
    #                         email='codynr4nzxh@outlook.com', email_pwd='UfMSt4aiZ8',
    #                         gender=1, birthday='1986-8-4', profile_id='bank.charles.3', status='verifying')
    # AccountOpt.save_account(account='eddykkqf56@outlook.com',
    #                         password='nYGcEXNjGY', owner=1, category=1,
    #                         email='eddykkqf56@outlook.com', email_pwd='M4c5gs3SEx',
    #                         gender=1, birthday='1974-6-8', profile_id='wheeler.degale.9', status='invalid')
    # AccountOpt.save_account(account='deckor31g90@outlook.com',
    #                         password='mYIiw539Ke', owner=2, category=1,
    #                         email='deckor31g90@outlook.com', email_pwd='GsMNVhEqHu',
    #                         gender=1, birthday='1995-8-6', profile_id='harold.suddaby.1', active_area='North American')
    #
    # AccountOpt.save_account(account='estevanlkz5rw0@outlook.com',
    #                         password='QyjMNAhCGq', owner=2, category=1,
    #                         email='estevanlkz5rw0@outlook.com', email_pwd='dD2EV7ptSk',
    #                         gender=1, birthday='1996-11-27', profile_id='jervis.prockter.7', active_area='Japan')
    #
    # AccountOpt.save_account(account='yorkeru997a@outlook.com',
    #                         password='j9akBXwslF', owner=2, category=1,
    #                         email='yorkeru997a@outlook.com', email_pwd='wSmEHMsg7C',
    #                         gender=1, birthday='1966-6-23', profile_id='franklyn.dyneley.5',
    #                         enable_tasks='1;2;4;6', active_area='China', active_browser=3, configure=json.dumps({'last_login': '2019-2-2 18:36:20', 'last_post': '2018-8-2 18:36:20'}))
    #
    # AccountOpt.save_account(account='yorkeru997a@outlook.com',
    #                         password='Ogec1eOAFA', owner=3, category=1,
    #                         email='yorkeru997a@outlook.com', email_pwd='u3KLKTXye',
    #                         gender=0, birthday='1986-5-21', profile_id='alana.williamson.1401',
    #                         name='Alana Williamson', register_time='2017-9-2', active_area='Spanish',
    #                         active_browser=1, configure=json.dumps({'last_login': '2019-2-2 18:36:20', 'last_post': '2018-8-2 18:36:20'}))

    # 创建任务
    TaskOpt.save_task(category_id=1, creator_id=1, scheduler_id=1, account_ids=[1, 2, 3, 5], name=u'养个号', limit_counts=10)
    TaskOpt.save_task(category_id=2, creator_id=2, scheduler_id=2, account_ids=[3, 4, 6, 2], name=u'刷个好评', configure=json.dumps({'ads_code':'orderplus888'}), limit_counts=20)
    TaskOpt.save_task(category_id=1, creator_id=3, scheduler_id=4, account_ids=[4, 5, 1, 8], name=u'登录浏览就行了', configure=json.dumps({'keep_time': 900}), limit_counts=100)
    TaskOpt.save_task(category_id=1, creator_id=1, scheduler_id=3, account_ids=[1, 2, 4, 7], name=u'养个号11', limit_counts=10)
    TaskOpt.save_task(category_id=2, creator_id=1, scheduler_id=3, account_ids=[6], name=u'thumb', limit_counts=102)

    TaskOpt.save_task(category_id=1, creator_id=1, scheduler_id=5, account_ids=[1, 2, 3], name=u'养个号', limit_counts=100)
    TaskOpt.save_task(category_id=2, creator_id=2, scheduler_id=6, account_ids=[3, 4, 2, 5], name=u'刷个好评', configure=json.dumps({'ads_code':'orderplus888'}), limit_counts=30)
    TaskOpt.save_task(category_id=1, creator_id=3, scheduler_id=7, account_ids=[4, 5, 1, 3], name=u'登录浏览就行了', configure=json.dumps({'keep_time': 900}), limit_counts=10)
    TaskOpt.save_task(category_id=1, creator_id=1, scheduler_id=1, account_ids=[1, 7, 4], name=u'养个号11', limit_counts=40)
    TaskOpt.save_task(category_id=3, creator_id=1, scheduler_id=2, account_ids=[1, 2, 4, 9], name=u'thumb', limit_counts=5)



    AgentOpt.save_agent('Spanish', status=-1)
    AgentOpt.save_agent('China', status=0)
    AgentOpt.save_agent('Japan', status=2)
    AgentOpt.save_agent('North American', status=2)


def show_test_data():
    tasks = TaskOpt.get_all_need_restart_task()
    for id, status in tasks:
        print(id, status)

    acc = AccountOpt.get_account(account_id=0)
    print(acc)


    res = TaskOpt.get_all_running_task()
    for t in res:
        print(t)

    print(TaskCategoryOpt.get_all_processor())
    # JobOpt.save_job(1, "a", "b")
    # jobs = JobOpt.get_job_by_task_id(1)
    # for j in jobs:
    #     print(j)

def opt_db():
    print(datetime.datetime.now())
    jobs = []

    for x in range(3000, 6000):
        job = Job()
        job.task = 2
        job.account = 2
        job.agent = 1
        job.status = 'running_th'
        job.track_id = '{}'.format(x)
        job.start_time = datetime.datetime.now()
        jobs.append(job)


    db_lock.acquire()
    print('thead dbs1={}'.format(db_session))
    db_session.add_all(jobs)
    db_session.commit()
    db_lock.release()

    db_lock.acquire()

    print('thead dbs2={}'.format(db_session))
    db_session.execute(Job.__table__.insert(), [
        {'task': 1, 'account': 3, 'agent': 1, 'status': 'ffff', 'track_id': '{}'.format(x),
         'start_time': datetime.datetime.now()} for x in range(8000, 10000)])
    db_session.commit()
    db_lock.release()


def test_db():
    import threading

    th = threading.Thread(target=opt_db)
    th.start()
    jobs = []
    for x in range(10010, 20000):
        job = Job()
        job.task = 2
        job.account = 2
        job.agent = 1
        job.status = 'running11'
        job.track_id = '{}'.format(x)
        job.start_time = datetime.datetime.now()
        jobs.append(job)

    db_lock.acquire()
    print(datetime.datetime.now())
    db_session.add_all(jobs)
    # db_session.commit()
    db_session.execute(Job.__table__.insert(), [{'task':1, 'account':3, 'agent':1, 'status':'ffff', 'track_id': '{}'.format(x), 'start_time': datetime.datetime.now()} for x in range(1000)])
    db_session.commit()
    print(db_session)
    db_session.close()
    db_lock.release()
    print(datetime.datetime.now())


def produce_account():
    # 添加账号
    filename = 'E:/accont_info.txt'
    with open(filename, 'r') as line:
        all_readline = line.readlines()
        import random
        t = random.randint(1, 100)
        for i in all_readline:
            str_info = i.split("/")
            print(str_info)
            user_account = str(str_info[0])
            user_password = str(str_info[1])
            email_password = str(str_info[2])
            gender = int(str_info[3])
            AccountOpt.save_account(account=user_account,
                            password=user_password, owner=3, category=1,
                            email='', email_pwd=email_password,
                            gender=gender, birthday='1986-8-4', profile_id='', status='valid', active_browser=(t%6+1), configure=json.dumps({'last_login': '2019-4-2 18:36:20', 'last_post': '2018-8-2 18:36:20'}))


def produce_tasks():
    # 创建任务
    for i in range(3):
        TaskOpt.save_task(category_id=1, creator_id=1, scheduler_id=1, account_ids=[x for x in range(10100, 10369)], name=u'养个号'.format(i), limit_counts=10)
        TaskOpt.save_task(category_id=2, creator_id=2, scheduler_id=2, account_ids=[x for x in range(10021, 10100)], name=u'刷个好评'.format(i), configure=json.dumps({'ads_code':'orderplus888'}), limit_counts=20)
        TaskOpt.save_task(category_id=1, creator_id=3, scheduler_id=4, account_ids=[x for x in range(11500, 12000)], name=u'登录浏览就行了'.format(i), configure=json.dumps({'keep_time': 900}), limit_counts=100)
        TaskOpt.save_task(category_id=1, creator_id=1, scheduler_id=3, account_ids=[x for x in range(16000, 16800)], name=u'养号'.format(i), limit_counts=30, configure=json.dumps({'ads_code':'2112121'}))
        TaskOpt.save_task(category_id=2, creator_id=1, scheduler_id=3, account_ids=[x for x in range(10756, 11200)], name=u'好评'.format(i), limit_counts=102)

        TaskOpt.save_task(category_id=1, creator_id=1, scheduler_id=5, account_ids=[x for x in range(18900, 19630)], name=u'来养号'.format(i), limit_counts=100, last_edit=datetime.datetime.now())
        TaskOpt.save_task(category_id=2, creator_id=2, scheduler_id=6, account_ids=[x for x in range(16900, 17400)], name=u'刷评'.format(i), configure=json.dumps({'ads_code':'orderplus888'}), limit_counts=30)
        TaskOpt.save_task(category_id=1, creator_id=3, scheduler_id=7, account_ids=[x for x in range(15000, 15025)], name=u'登录就行了'.format(i), configure=json.dumps({'keep_time': 900}), limit_counts=10)
        TaskOpt.save_task(category_id=1, creator_id=1, scheduler_id=1, account_ids=[x for x in range(15900, 16026)], name=u'yang'.format(i), limit_counts=400)
        TaskOpt.save_task(category_id=2, creator_id=1, scheduler_id=2, account_ids=[x for x in range(12856, 13059)], name=u'shua'.format(i), limit_counts=5)


def test11(*names):
    print(names)
    test12(*names)


def test12(*names):
    print(names)


def generate_fb_json():
    with open('name.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        names = []
        limit = 0
        for line in lines:
            if limit >=1000:
                break
            name = line.strip()
            names.append(name)
            limit+=1
    dict_cfg = {"friend_search_keys": names,
                "chat_msgs": [],
                "posts": []
                }

    import json
    str_cfg = json.dumps(dict_cfg)
    with open('facebook.json', 'w', encoding='utf-8') as f:
        f.write(str_cfg)




if __name__ == '__main__':
    # init_db_data()
    # show_test_data()
    # test_db()
    produce_account()
    # print(11)
    # produce_tasks()
    generate_fb_json()
    # TaskOpt.save_task(category_id=1, creator_id=1, scheduler_id=3, account_ids=[i for i in range(1,10000)], name=u'太多的账号', limit_counts=10, limit_end_time=datetime.datetime.now()+datetime.timedelta(days=3))

    ALTER_SQL = '''
    ALTER TABLE `user` ADD COLUMN `auth_id` INT NOT NULL;
    ALTER TABLE `user` ADD UNIQUE KEY `auth_id` (`auth_id`);
    ALTER TABLE `user` ADD CONSTRAINT `user_auth_id_3666ad92_fk_auth_user_id` FOREIGN KEY (`auth_id`) REFERENCES `auth_user` (`id`);
    '''

 # pipenv run python web_service/initialization/users/new_user.py





