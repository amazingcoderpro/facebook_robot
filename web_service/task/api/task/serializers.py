# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from task.models import Task

# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 任务序列化类


class TaskSerializer(serializers.HyperlinkedModelSerializer):

    # 检查任务是否存在，存在则不创建
    def create(self, validated_data):
        return super(TaskSerializer, self).create(validated_data)

    class Meta:
        model = Task
        fields = ('url', 'id', 'name')
        # extra_kwargs = {'description': {'allow_blank': True}}


