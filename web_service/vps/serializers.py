# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from vps.models import Area,Agent


class AreaSerializer(serializers.HyperlinkedModelSerializer):

    # 检查社交账户类型是否存在，存在则不创建
    def create(self, validated_data):
        try:
            return Area.objects.get(name=validated_data['name'])
        except ObjectDoesNotExist:
            return super(AreaSerializer, self).create(validated_data)

    class Meta:
        model = Area
        fields = ('url', 'id', 'name', 'description')
        extra_kwargs = {'description': {'allow_blank': True}}


class AgentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Agent
        fields = ('url', 'id', 'status', 'active_area', 'configure')
        extra_kwargs = {'queue_name': {'allow_blank': True},
                        'configure': {'allow_blank': True}}


