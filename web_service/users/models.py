# -*- coding: utf-8 -*-
# Created by guangda.lee on 19-03-19
# Function:

from django.db import models
from django.contrib.auth.models import User as AuthUser


# 用户类型
class UserCategory(models.Model):
    category = models.AutoField(db_column='category', primary_key=True)
    name = models.CharField(max_length=255, default='')  # 类别名称，如普通用户，管理员...
    description = models.CharField(max_length=255, default='')

    class Meta:
        db_table = 'user_category'

    def __unicode__(self):
        return self.name


# 用户
class User(models.Model):
    category = models.ForeignKey(UserCategory, db_column='category', on_delete=models.CASCADE)
    auth = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    # 记录该用户可以创建的[任务类型id]列表(TaskCategory.id)， 以分号分割"1;2;3", 默认为空，代表可以创建所有类型的任务
    enable_tasks = models.CharField(max_length=255, default='')
    token = models.CharField(max_length=255, default='')

    class Meta:
        db_table = 'user'
        ordering = ('-id',)

    def __unicode__(self):
        return self.auth.username

