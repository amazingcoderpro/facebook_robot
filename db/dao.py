#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-16
# Function: 对所有数据库表常用操作进行封装， 降低其他模块与数据操作之间的耦合


import datetime
from sqlalchemy import or_, and_
from db.basic import db_session
from db.models import (Scheduler, Account, User, Task, TaskAccountGroup,
                       Job, TaskCategory, UserCategory, AccountCategory, Agent)


class SchedulerOpt:
    """
    Scheduler表处理类
    """
    @classmethod
    def save_scheduler(cls, mode=0, interval=0, date=datetime.datetime.now()):
        sch = Scheduler()
        sch.mode = mode
        sch.interval = interval
        sch.date = date
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
        return db_session.query(Scheduler).filter(Scheduler.id == scheduler_id).first()


class UserOpt:
    @classmethod
    def save_user(cls, auth_id, category=0, enable_tasks=''):
        user = User()
        user.auth_id = auth_id
        user.category = category
        user.enable_tasks = enable_tasks
        db_session.add(user)
        db_session.commit()
        return user

    @classmethod
    def get_user_enable_tasks(cls, user_id):
        res = db_session.query(User.enable_tasks).filter(User.id == user_id).first()
        if res:
            return res[0].split(';')
        else:
            return None


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
    def get_all_need_restart_task(cls):
        """
        主要用于服务器宕机后重新启动时获取所有需要启动的任务，包括pending状态和running状态的
        :return:
        """
        return db_session.query(Task).filter(or_(Task.status == 'pending', Task.status == 'running')).all()

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

        for k, v in kwargs.items():
            if hasattr(task, k):
                setattr(task, k, v)

        db_session.add(task)
        db_session.commit()

        # task.accounts = account_ids   # account_ids只是id列表，不能赋值
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
            db_session.add(task)
            db_session.commit()
            return True

        return False

    @classmethod
    def set_task_status(cls, task_id, status):
        task = db_session.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = status
            db_session.commit()
            return True

        return False

    @classmethod
    def set_task_result(cls, task_id, result):
        task = db_session.query(Task).filter(Task.id == task_id).first()
        if task:
            task.result = result
            db_session.commit()
            return True

        return False

    @classmethod
    def get_task(cls, task_id):
        return db_session.query(Task.scheduler).filter(Task.id == task_id).first()


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
    def get_aps_ids_by_task(cls, task_id):
        tags = db_session.query(TaskAccountGroup).filter(TaskAccountGroup.task_id == task_id).all()
        ids = []
        for t in tags:
            ids.append(t.aps_id)

        return ids

    @classmethod
    def get_aps_id(cls, task_id, account_id):
        tag = db_session.query(TaskAccountGroup).filter(and_(TaskAccountGroup.task_id == task_id,
                                                             TaskAccountGroup.account_id == account_id)).first()
        if tag:
            return tag.aps_id
        else:
            return None

    @classmethod
    def set_aps_id(cls, task_id, account_id, aps_id):
        # 更新apscheduler任务调度产生的id,用以暂停、重启一个子任务
        tag = db_session.query(TaskAccountGroup).filter(and_(TaskAccountGroup.task_id == task_id,
                                                             TaskAccountGroup.account_id == account_id)).first()
        if tag:
            tag.aps_id = aps_id
            db_session.commit()
            return True

        return False


class JobOpt:
    @classmethod
    def save_job(cls, task_id, account_id, execute_id='', status=-1, start_time=datetime.datetime.now()):
        # status-- -1-pending, 0-failed, 1-succeed, 2-running
        job = Job()
        job.task = task_id
        job.account = account_id
        job.status = status
        job.execute_id = execute_id
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
    def get_jobs_by_task_id(cls, task_id):
        return db_session.query(Job).filter(Job.task == task_id).all()

    @classmethod
    def set_job_status(cls, job_id, status):
        job = db_session.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            db_session.commit()
            return True

        return False

    @classmethod
    def set_job_result(cls, job_id, result):
        job = db_session.query(Job).filter(Job.id == job_id).first()
        if job:
            job.result = result
            db_session.commit()
            return True

        return False


class TaskCategoryOpt:
    @classmethod
    def save_task_category(cls, category, name, processor, description=''):
        tag = TaskCategory()
        tag.category = category
        tag.name = name
        tag.processor = processor
        tag.description = description
        db_session.add(tag)
        db_session.commit()
        return tag

    @classmethod
    def get_all_processor(cls):
        res = db_session.query(TaskCategory.processor).filter().distinct().all()
        return [r[0] for r in res]

    @classmethod
    def get_processor(cls, category):
        tcg = db_session.query(TaskCategory.processor).filter(TaskCategory.category == category).first()
        if tcg:
            return tcg[0]
        else:
            return None


class AgentOpt:
    @classmethod
    def save_agent(cls, queue, ip, status=1, area='', config=''):
        agent = Agent()
        agent.queue = queue
        agent.status = status
        agent.ip = ip
        agent.area = area
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
    def get_agents(cls, status=-1):
        if status >= 0:
            return db_session.query(Agent).filter().all(Agent.status == status)
        else:
            return db_session.query(Agent).filter().all()

    @classmethod
    def get_enable_agents(cls):
        return db_session.query(Agent).filter(Agent.status != 3).order_by(Agent.status)


def init_db_data():
    """
    初始化各表基础配置数据，用于环境测试等
    :return:
    """
    # 初始化用户类别表
    # UserCategoryOpt.save_user_category(category=1, name='普通用户', description='可以创建部分或所有类型任务，但无权修改服务器资源')
    # UserCategoryOpt.save_user_category(category=2, name='管理员', description='可创建所有类型任务， 且可以管理服务器资源、修改服务器配置等')
    #
    # # 增加测试用户
    # UserOpt.save_user(account='user1', password='user1', category=1, enable_tasks='1;2;3', name='张三')
    # UserOpt.save_user(account='user2', password='user2', category=1, enable_tasks='4;5;6', name='李四')
    # UserOpt.save_user(account='admin', password='admin', category=2, enable_tasks='', name='大哥大')

    # return
    # 初始化任务类别表
    # 1--fb自动养账号， 2-fb刷广告好评， 3- fb仅登录浏览， 4- fb点赞, 5- fb发表评论， 6- fb post状态, 7- fb 聊天， 8- fb 编辑个人信息， 未完待续...
    TaskCategoryOpt.save_task_category(category=1, name=u'facebook自动养号', processor='fb_auto_feed')
    TaskCategoryOpt.save_task_category(category=2, name=u'facebook刷好评', processor='fb_click_farming')
    TaskCategoryOpt.save_task_category(category=3, name=u'facebook登录浏览', processor='fb_login')
    TaskCategoryOpt.save_task_category(category=4, name=u'facebook点赞', processor='fb_thumb')
    TaskCategoryOpt.save_task_category(category=5, name=u'facebook发表评论', processor='fb_comment')
    TaskCategoryOpt.save_task_category(category=6, name=u'facebook发表状态', processor='fb_post')
    TaskCategoryOpt.save_task_category(category=7, name=u'facebook聊天', processor='fb_chat')
    TaskCategoryOpt.save_task_category(category=8, name=u'facebook编辑个人信息', processor='fb_edit')

    # 初始化账号类别表
    # 该账号所属类别，1--facebook账号，2--twitter账号， 3--Ins账号
    AccountCategoryOpt.save_account_category(category=1, name=u'Facebook账号')
    AccountCategoryOpt.save_account_category(category=2, name=u'Twitter账号')
    AccountCategoryOpt.save_account_category(category=3, name=u'Instagram账号')


    # 增加任务计划
    # category: 0-立即执行（只执行一次）， 1-间隔执行并不立即开始（间隔一定时间后开始执行，并按设定的间隔周期执行下去） 2-间隔执行，但立即开始， 3-定时执行，指定时间执行
    SchedulerOpt.save_scheduler(mode=0)
    SchedulerOpt.save_scheduler(mode=1, interval=600)
    SchedulerOpt.save_scheduler(mode=2, interval=900)
    SchedulerOpt.save_scheduler(mode=3, date=datetime.datetime.now()+datetime.timedelta(hours=5))

    # 添加账号
    AccountOpt.save_account(account='codynr4nzxh@outlook.com',
                            password='qVhgldHmgp', owner=1, category=1,
                            email='codynr4nzxh@outlook.com', email_pwd='UfMSt4aiZ8',
                            gender=1, birthday='1986-8-4', profile_id='bank.charles.3', status='verify')
    AccountOpt.save_account(account='eddykkqf56@outlook.com',
                            password='nYGcEXNjGY', owner=1, category=1,
                            email='eddykkqf56@outlook.com', email_pwd='M4c5gs3SEx',
                            gender=1, birthday='1974-6-8', profile_id='wheeler.degale.9')
    AccountOpt.save_account(account='deckor31g90@outlook.com',
                            password='mYIiw539Ke', owner=2, category=1,
                            email='deckor31g90@outlook.com', email_pwd='GsMNVhEqHu',
                            gender=1, birthday='1995-8-6', profile_id='harold.suddaby.1')

    AccountOpt.save_account(account='estevanlkz5rw0@outlook.com',
                            password='QyjMNAhCGq', owner=2, category=1,
                            email='estevanlkz5rw0@outlook.com', email_pwd='dD2EV7ptSk',
                            gender=1, birthday='1996-11-27', profile_id='jervis.prockter.7')

    AccountOpt.save_account(account='yorkeru997a@outlook.com',
                            password='j9akBXwslF', owner=2, category=1,
                            email='yorkeru997a@outlook.com', email_pwd='wSmEHMsg7C',
                            gender=1, birthday='1966-6-23', profile_id='franklyn.dyneley.5',
                            enable_tasks='1;2;4;6')

    AccountOpt.save_account(account='yorkeru997a@outlook.com',
                            password='Ogec1eOAFA', owner=3, category=1,
                            email='yorkeru997a@outlook.com', email_pwd='u3KLKTXye',
                            gender=0, birthday='1986-5-21', profile_id='alana.williamson.1401',
                            name='Alana Williamson', register_time='2017-9-2')

    # 创建任务
    TaskOpt.save_task(category_id=1, creator_id=1, scheduler_id=1, account_ids=[1, 2], name=u'养个号')
    TaskOpt.save_task(category_id=2, creator_id=2, scheduler_id=2, account_ids=[3, 4], name=u'刷个好评', ads_code='orderplus888')
    TaskOpt.save_task(category_id=3, creator_id=3, scheduler_id=4, account_ids=[4, 5], keep_time=900, name=u'登录浏览就行了')

    AgentOpt.save_agent('agent1;for_agent1', '1.1.1.1', status=1)
    AgentOpt.save_agent('agent2;for_agent2', '2.2.2.2', status=0)
    AgentOpt.save_agent('agent3;for_agent3', '3.3.3.3', status=2)


def show_test_data():
    tasks = TaskOpt.get_all_need_restart_task()
    for task in tasks:
        print("tasks = {}".format(task))
        for acc in task.accounts:
            print(acc.account)

    acc = AccountOpt.get_account(account_id=0)
    print(acc)

    TaskOpt.set_task_status(1, 1)
    res = TaskOpt.get_all_need_restart_task()
    for t in res:
        print(t)

    res = TaskOpt.get_all_running_task()
    for t in res:
        print(t)

    print(TaskCategoryOpt.get_all_processor())
    # JobOpt.save_job(1, "a", "b")
    # jobs = JobOpt.get_job_by_task_id(1)
    # for j in jobs:
    #     print(j)
    print(UserOpt.get_user_enable_tasks(1))
    print(UserOpt.get_user_enable_tasks(2))
    print(UserOpt.get_user_enable_tasks(3))


if __name__ == '__main__':
    init_db_data()
    show_test_data()






