# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from vps.models import Agent
from vps.api.area.serializers import AreaSerializer


# Created by: guangda.lee
# Created on: 2019/3/27
# Function: Agent 序列化类


class AgentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Agent
        fields = ('url', 'id', 'queue_name', 'status', 'area', 'configure')
        extra_kwargs = {'queue_name': {'allow_blank': True},
                        'configure': {'allow_blank': True}}


