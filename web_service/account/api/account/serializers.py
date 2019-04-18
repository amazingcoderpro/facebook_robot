# -*- coding: utf-8 -*-

from rest_framework import serializers

from account.api.category.serializers import CategorySerializer
from account.models import Account
from users.api.user.serializers import UserSerializer


# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 社交账户序列化类


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    # category = serializers.PrimaryKeyRelatedField(queryset=AccountCategory.objects.all())
    category = CategorySerializer()
    owner = UserSerializer(read_only=True)
    area_name = serializers.SerializerMethodField(read_only=True)

    # 创建账户
    def create(self, validated_data):
        from django.db import transaction
        from django.core.exceptions import ObjectDoesNotExist
        with transaction.atomic():
            # 处理目录
            category = CategorySerializer().create(validated_data.pop('category'))
            validated_data['category'] = category
            from users.common import user_by_token
            owner = user_by_token(self.context.get("request"))
            validated_data['owner'] = owner
            try:
                return Account.objects.get(category_id=category.category, owner=owner.id,
                                           account=validated_data['account'])
            except ObjectDoesNotExist:
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
        fields = ('url', 'id', 'owner', 'category', 'account', 'password', 'email', 'email_pwd', 'phone_number',
                  'gender', 'birthday', 'national_id', 'register_time', 'name', 'profile_id', 'status',
                  'enable_tasks','area_name',)  # 'last_login', 'last_post', 'last_chat', 'last_farming', 'last_comment', 'last_edit')
        extra_kwargs = {'phone_number': {'allow_blank': True},
                        'national_id': {'allow_blank': True},
                        'enable_tasks': {'allow_blank': True},
                        # 'last_login': {'read_only': True},
                        # 'last_post': {'read_only': True},
                        # 'last_chat': {'read_only': True},
                        # 'last_farming': {'read_only': True},
                        # 'last_comment': {'read_only': True},
                        # 'last_edit': {'read_only': True}
                        }

    def get_area_name(self,row):
        print(row)
        if row.active_area:
            return row.active_area.name



# 导出账号序列化类
class ExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        titles = (u'账号', u'姓名', '邮件地址', u'手机号', 'Profile ID', u'状态',)
        fields = ('account', 'name', 'email', 'phone_number', 'profile_id', 'status',)


