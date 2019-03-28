# -*- coding: utf-8 -*-

from django.db import models


# 区域
class Area(models.Model):
    name = models.CharField(max_length=255, default='')
    description = models.CharField(max_length=2048, default='')

    class Meta:
        db_table = 'area'


#
class Agent(models.Model):
    # 该agent绑定的任务队列， job将根据与其最亲近的agent的queue名来被分发, 通常队列名与area相同
    queue_name = models.CharField(max_length=255, default='')

    # 0-idle, 1-normal, 2-busy, 3-disable
    # -1--disable, 大于零代表其忙碌值（即当前待处理的任务量）
    status = models.CharField(max_length=20, default='0')

    # 该agent所属区域
    area = models.CharField(max_length=255, default='')

    # 该agent的配置信息
    configure = models.CharField(max_length=2048, default='')

    class Meta:
        db_table = 'agent'


