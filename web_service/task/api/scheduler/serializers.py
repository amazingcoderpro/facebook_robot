# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from task.models import Scheduler

# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 任务调度类型序列化类


class SchedulerSerializer(serializers.HyperlinkedModelSerializer):

    # # 检查任务调度类型是否存在，存在则不创建
    # def create(self, validated_data):
    #     return super(SchedulerSerializer, self).create(validated_data)

    class Meta:
        model = Scheduler
        fields = ('url', 'id', 'mode', 'interval', 'start_date', 'end_date')
        extra_kwargs = {'start_date': {'allow_null': True},
                        'end_date': {'allow_null': True}}

