# -*- coding: utf-8 -*-

from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import User as AuthUser
from account.models import AccountCategory, Account
from account.api.category.serializers import CategorySerializer

# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 社交账户序列化类


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    # category = serializers.PrimaryKeyRelatedField(queryset=AccountCategory.objects.all())
    category = CategorySerializer()

    # 创建账户
    def create(self, validated_data):
        with transaction.atomic():
            # 处理目录
            category_data = validated_data.pop('category')
            validated_data['category'] = CategorySerializer().create(category_data)
            from users.common import user_by_token
            validated_data['owner'] = user_by_token(self.context.get("request"))
            return super(AccountSerializer, self).create(validated_data)
    
    # 更新账户
    def update(self, instance, validated_data):
        # 处理目录
        if 'category' in validated_data:
            category_data = validated_data.pop('category')
            validated_data['category'] = CategorySerializer().create(category_data)

        return super(AccountSerializer, self).update(instance, validated_data)

    class Meta:
        model = Account
        fields = ('url', 'id', 'category', 'account', 'password', 'email', 'email_pwd', 'phone_number',
                  'gender', 'birthday', 'national_id', 'register_time', 'name', 'profile_id', 'status',
                  'enable_tasks', 'last_login', 'last_post', 'last_chat', 'last_farming', 'last_comment',
                  'last_edit')
        extra_kwargs = {'phone_number': {'allow_blank': True},
                        'national_id': {'allow_blank': True},
                        'enable_tasks': {'allow_blank': True},
                        'last_login': {'read_only': True},
                        'last_post': {'read_only': True},
                        'last_chat': {'read_only': True},
                        'last_farming': {'read_only': True},
                        'last_comment': {'read_only': True},
                        'last_edit': {'read_only': True}}

