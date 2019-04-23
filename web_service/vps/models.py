# -*- coding: utf-8 -*-

from django.db import models


# 区域
class Area(models.Model):
    name = models.CharField(max_length=255, default='')
    running_tasks = models.IntegerField(verbose_name='当前区域正在执行的任务数量')
    description = models.CharField(max_length=2048, default='')

    class Meta:
        db_table = 'area'


#
class Agent(models.Model):

    # 0-idle, 1-normal, 2-busy, 3-disable
    # -1--disable, 大于零代表其忙碌值（即当前待处理的任务量）
    # status = models.IntegerField(default=0, blank=True, null=True)

    # 该agent所属区域
    active_area = models.ForeignKey(Area, db_column='active_area', on_delete=models.DO_NOTHING,blank=True, null=True)

    # 该agent的配置信息
    configure = models.CharField(max_length=2048, default='',  blank=True, null=True)

    class Meta:
        db_table = 'agent'


