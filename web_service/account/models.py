# -*- coding: utf-8 -*-
# Created by guangda.lee on 19-03-19
# Function:

from datetime import datetime
from django.db import models

from users.models import User


class AccountCategory(models.Model):
    """
    账号类型表
    """
    # 该账号所属类别，1--facebook账号，2--twitter账号， 3--Ins账号
    category = models.AutoField(db_column='category', primary_key=True)
    name = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'account_category'


# 社交账号
class Account(models.Model):
    # 该账号所属类别，该账号所属类别，1--facebook账号，2--twitter账号， 3--Ins账号
    category = models.ForeignKey(AccountCategory, db_column='category', on_delete=models.CASCADE)

    # 每个账号都应该隶属于某个人员，以方便权限管理
    owner = models.ForeignKey(User, db_column='owner', on_delete=models.CASCADE)
    account = models.CharField(max_length=255, default='')
    password = models.CharField(max_length=255, default='')
    # -----------------以上是必填项----------------

    email = models.CharField(max_length=255, default='')
    email_pwd = models.CharField(max_length=255, default='')
    phone_number = models.CharField(max_length=100, default='')

    # 0-女，1-男
    gender = models.IntegerField(default=0)
    # 生日格式"1990-3-21"
    birthday = models.CharField(max_length=100, default='')
    national_id = models.CharField(max_length=100, default='')
    register_time = models.CharField(max_length=100, default='')
    name = models.CharField(max_length=100, default='')
    profile_id = models.CharField(max_length=100, default='')

    # 0-valid, 1-invalid, 2-verify, 3-other
    status = models.CharField(max_length=20, default='valid')

    # 是否正在被某任务使用 0-未使用， 大于1代表正在被使用，数字代表并发使用数
    using = models.IntegerField(default=0)

    # 记录该用户可以创建的[任务类型id]列表(TaskCategory.id)， 以分号分割"1;2;3", 默认为空，代表可以创建所有类型的任务
    enable_tasks = models.CharField(max_length=255, default='')

    # 存放用户profile文件
    profile_path = models.CharField(max_length=255, default='')

    last_login = models.DateTimeField(default=datetime.min)
    last_post = models.DateTimeField(default=datetime.min)
    last_chat = models.DateTimeField(default=datetime.min)
    last_farming = models.DateTimeField(default=datetime.min)
    last_comment = models.DateTimeField(default=datetime.min)
    last_edit = models.DateTimeField(default=datetime.min)

    # active_ip = Column(String(255), default='', server_default='')
    # 活跃地域
    active_area = models.CharField(max_length=255, default='')
    # 常用浏览器指纹
    active_browser = models.CharField(max_length=2048, default='')
    # 账号的其他非常规配置信息
    configure = models.CharField(max_length=2048, default='')

    class Meta:
        db_table = 'account'
        ordering = ('-id',)
