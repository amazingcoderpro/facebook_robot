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


class AgentSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source="active_area.name", read_only=True)

    class Meta:
        model = Agent
        fields = ('id', 'status', 'active_area', 'configure', 'area_name')

        write_only_fields = (
            "status",
            "active_area",
            "configure"
        )


# 区域账号数量序列化
class AreaAccountCountSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ('id','name','count',)

    @staticmethod
    def get_count(row):
        return row.Account_Area.all().count()


