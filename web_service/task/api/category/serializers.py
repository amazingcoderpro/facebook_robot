# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from task.models import TaskCategory

# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 任务类型序列化类


class CategorySerializer(serializers.HyperlinkedModelSerializer):

    id = serializers.IntegerField(source='category', read_only=True)

    # 检查任务类型是否存在，存在则不创建
    def create(self, validated_data):
        try:
            return TaskCategory.objects.get(name=validated_data['name'])
        except ObjectDoesNotExist:
            return super(CategorySerializer, self).create(validated_data)

    class Meta:
        model = TaskCategory
        fields = ('url', 'category', 'id', 'name', 'processor', 'description')
        extra_kwargs = {'description': {'allow_blank': True}}


