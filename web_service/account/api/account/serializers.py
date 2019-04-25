# -*- coding: utf-8 -*-

from rest_framework import serializers

from account.api.category.serializers import CategorySerializer
from account.models import Account
from users.api.user.serializers import UserSerializer
from vps.serializers import AreaSerializer
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from users.common import user_by_token


# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 社交账户序列化类


class AccountSerializer(serializers.ModelSerializer):

    #创建账户
    def create(self, validated_data):
        # print("#########", validated_data)
        with transaction.atomic():
            owner = user_by_token(self.context.get("request"))
            validated_data['owner'] = owner
            try:
                return Account.objects.get(category_id=validated_data["category"], owner=owner.id,
                                           account=validated_data['account'])
            except ObjectDoesNotExist:
                return super(AccountSerializer, self).create(validated_data)

    # 更新账户
    def update(self, instance, validated_data):
        return super(AccountSerializer, self).update(instance, validated_data)

    class Meta:
        model = Account
        fields = ('url', 'id', 'owner', 'category', 'account', 'password', 'email', 'email_pwd', 'phone_number',
                  'gender', 'birthday', 'national_id', 'register_time', 'name', 'profile_id', 'status',
                  'enable_tasks', 'active_area')
        extra_kwargs = {
                        'email': {'allow_blank': True},
                        'email_pwd': {'allow_blank': True},
                        'birthday': {'allow_blank': True},
                        'register_time': {'allow_blank': True},
                        'name': {'allow_blank': True},
                        'owner':{"write_only": False, "read_only": True},
                        'profile_id': {'allow_blank': True},
                        'phone_number': {'allow_blank': True},
                        'national_id': {'allow_blank': True},
                        'enable_tasks': {'allow_blank': True}
                        }

    def to_representation(self, instance):
        data = super(AccountSerializer, self).to_representation(instance)
        data["owner"] = UserSerializer(instance.owner, context=self.context).data
        data["category"] = CategorySerializer(instance.category, context=self.context).data
        data["active_area"] = AreaSerializer(instance.active_area, context=self.context).data

        return data


# 导出账号序列化类
class ExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        titles = (u'账号', u'姓名', '邮件地址', u'手机号', 'Profile ID', u'状态',)
        fields = ('account', 'name', 'email', 'phone_number', 'profile_id', 'status',)


