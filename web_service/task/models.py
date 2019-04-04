# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models

from account.models import Account
from users.models import User


# Created by guangda.lee on 19-03-19
# Function:


# 任务调度类型
class Scheduler(models.Model):
    # 执行模式： 0-立即执行（只执行一次）， 1-间隔执行并不立即开始（间隔一定时间后开始执行，并按设定的间隔周期执行下去） 2-间隔执行，但立即开始， 3-定时执行，指定时间执行
    mode = models.IntegerField(default=0)
    interval = models.IntegerField(default=600)       # 间隔时长， 单位秒
    # 作用有二：
    # 1作为定时间任务的执行时间, 仅mode=3时有效
    # 2作为周期任务的首次启动时间, 仅mode=1时有效
    start_date = models.DateTimeField(null=True)  # default=datetime.min)
    # 该任务的终止时间
    end_date = models.DateTimeField(null=True)  # default=datetime.min)       # 定时执行时需要指定，如2019-03-31 13:30:30

    def __unicode__(self):
        return (u'立即执行（只执行一次）',
                u'间隔执行',
                u'间隔执行，立即开始',
                u'定时执行，指定时间执行')[self.mode]

    class Meta:
        db_table = 'scheduler'


class TaskCategory(models.Model):
    """
    任务类型表
    """

    # 1--fb自动养账号， 2-fb刷广告好评， 3- fb仅登录浏览， 4- fb点赞, 5- fb发表评论， 6- fb post状态, 7- fb 聊天， 8- fb 编辑个人信息， 未完待续...
    category = models.AutoField(db_column='category', primary_key=True)
    name = models.CharField(max_length=255, default='')
    processor = models.CharField(max_length=255, default='')  # 任务的处理函数名, 不能为空, 代码逻辑中将依赖这个函数名进行任务分发
    description = models.CharField(max_length=2048, default='')
    # name:title:type(bool/int/float/string):default[:option1[|option2[|optionN]] [\r\n(new line)]
    configure = models.CharField(max_length=2048, default='')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'task_category'


class Task(models.Model):
    """
    任务表， 对用户层承现
    """
    # 任务的创建者
    creator = models.ForeignKey(User, db_column='creator', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default='')
    # 任务类型， 0-养账号，1-刷好评,其他待续
    category = models.ForeignKey(TaskCategory, db_column='category', on_delete=models.CASCADE)
    # 任务状态， -1-pending, 0-failed, 1-succeed, 2-running, 3-pausing, new-新新，还没处理
    # status = Column(Integer, default=-1, server_default='-1')
    # 任务状态改用字符串是为了直观， 避免前后端转换的麻烦
    status = models.CharField(max_length=20, default='new')
    # 任务调度规则
    scheduler = models.ForeignKey(Scheduler, db_column='scheduler', on_delete=models.CASCADE)
    # 调度线程id, 用以暂停、恢复、取消任务
    aps_id = models.CharField(max_length=255, default='')
    # 一个任务同时占用多个账号
    accounts = models.ManyToManyField(Account, through='TaskAccountRelationship')
    # 第一次真正启动的时间
    start_time = models.DateTimeField(null=True)
    # 实际结束时间
    end_time = models.DateTimeField(null=True)
    # 该task成功、失败的次数（针对周期性任务）
    failed_counts = models.IntegerField(default=0)
    succeed_counts = models.IntegerField(default=0)
    # 该任务最大执行次数（即成功的job次数），比如刷分，可以指定最大刷多少次
    limit_counts = models.IntegerField(default=1)
    # 该任务需要的账号数量
    accounts_num = models.IntegerField(default=0)

    # 實際可用的賬號數量（因爲會有賬號狀態不可用）
    real_accounts_num = models.IntegerField(default=0)

    result = models.CharField(max_length=2048, default='')
    # 这里保存任务的额外信息，以json字符形式保存，如post内容， 点赞规则, ads_code, keep time, 目标站点等
    configure = models.CharField(max_length=2048, default='{}')
    # 这个是在APScheduler中调度时的任务id, 用以暂停、重启、终止等 操作,一个任务+一个账号构成一个唯一的task
    # aps_id = models.CharField(max_length=100, default='')

    last_update = models.DateTimeField(auto_now_add=True)

    # def accounts_list(self):
    #     return [acc.account for acc in self.taskaccountrelationship_set.all()]

    class Meta:
        db_table = 'task'
        ordering = ('-id',)


class TaskAccountRelationship(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        db_table = 'task_account_group'



