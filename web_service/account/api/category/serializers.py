# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from account.models import AccountCategory

# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 社交账户类型序列化类


class CategorySerializer(serializers.HyperlinkedModelSerializer):

    # 检查社交账户类型是否存在，存在则不创建
    def create(self, validated_data):
        try:
            return AccountCategory.objects.get(name=validated_data['name'])
        except ObjectDoesNotExist:
            return super(CategorySerializer, self).create(validated_data)

    class Meta:
        model = AccountCategory
        fields = ('url', 'category', 'name')

