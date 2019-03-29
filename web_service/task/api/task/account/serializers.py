# -*- coding: utf-8 -*-

from rest_framework import serializers

from account.api.account.serializers import AccountSerializer
from task.models import TaskAccountRelationship


# Created by: guangda.lee
# Created on: 2019/3/29
# Function: 任务关联账号序列化类


class TaskAccountSerializer(serializers.ModelSerializer):

    account = AccountSerializer()

    class Meta:
        model = TaskAccountRelationship
        fields = ('id', 'account')

