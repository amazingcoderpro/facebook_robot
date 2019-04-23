# -*- coding: utf-8 -*-

from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import User as AuthUser
from users.models import User, UserCategory
from users.api.category.serializers import CategorySerializer

# Created by: guangda.lee
# Created on: 2019/3/25
# Function: 用户序列化类


# Auth User 序列化类
class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ('username', 'last_name', 'email')


class UserSerializer(serializers.ModelSerializer):
    # category = serializers.PrimaryKeyRelatedField(queryset=UserCategory.objects.all())
    category = CategorySerializer()

    auth = AuthUserSerializer(read_only=True)

    email = serializers.EmailField(source='auth.email', allow_blank=True)
    username = serializers.CharField(source='auth.username')
    fullname = serializers.CharField(source='auth.last_name')
    password = serializers.CharField(source='auth.password', write_only=True, allow_null=True, allow_blank=True)
    enable_tasks = serializers.CharField(allow_blank=True)

    # 重置用户密码
    @staticmethod
    def reset_password(instance, password):
        if isinstance(instance, AuthUser) and password and password != '':
            instance.set_password(password)

    # 创建用户
    def create(self, validated_data):
        with transaction.atomic():
            # 处理目录
            category_data = validated_data.pop('category')
            validated_data['category'] = CategorySerializer().create(category_data)
            # 处理 auth
            for related_obj_name in self.Meta.related_fields:
                data = validated_data.pop(related_obj_name)
                if related_obj_name == 'auth':
                    related_instance = AuthUser()
                else:
                    continue
                if 'password' in data:
                    self.reset_password(related_instance, data.pop('password'))
                # Same as default update implementation
                for attr_name, value in data.items():
                    setattr(related_instance, attr_name, value)
                related_instance.save()
                validated_data['auth'] = related_instance
            return super(UserSerializer, self).create(validated_data)
    
    # 更新用户
    def update(self, instance, validated_data):
        # 处理目录
        if 'category' in validated_data:
            category_data = validated_data.pop('category')
            validated_data['category'] = CategorySerializer().create(category_data)
        # auth
        for related_obj_name in self.Meta.related_fields:
            data = validated_data.pop(related_obj_name)
            related_instance = getattr(instance, related_obj_name)
            if 'password' in data:
                self.reset_password(related_instance, data.pop('password'))
            # Same as default update implementation
            for attr_name, value in data.items():
                setattr(related_instance, attr_name, value)
            related_instance.save()
        return super(UserSerializer, self).update(instance, validated_data)

    class Meta:
        model = User
        fields = ('url', 'id', 'auth', 'category', 'username', 'fullname', 'email', 'enable_tasks', 'password')
        related_fields = ['auth']
        extra_kwargs = {'password': {'write_only': True}}
        # depth = 2



