# -*- coding: utf-8 -*-

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from task.models import Task, Scheduler
from users.api.user.serializers import UserSerializer
from task.api.category.serializers import CategorySerializer
from task.api.scheduler.serializers import SchedulerSerializer
from account.models import Account
from account.api.account.serializers import AccountSerializer


# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 任务序列化类


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    category = CategorySerializer()
    creator = UserSerializer(read_only=True)
    scheduler = SchedulerSerializer()
    # accounts = AccountSerializer(many=True)

    def create(self, validated_data):
        validated_data['category'] = CategorySerializer().create(validated_data.pop('category'))
        has_accounts = 'accounts' in validated_data
        if has_accounts:
            accounts_data = validated_data.pop('accounts')
        from users.common import user_by_token
        validated_data['creator'] = user_by_token(self.context.get("request"))
        with transaction.atomic():
            scheduler_data = validated_data.pop('scheduler')
            print(scheduler_data)
            validated_data['scheduler'] = Scheduler.objects.create(**scheduler_data)  # SchedulerSerializer().create(scheduler_data)  # (validated_data.pop('scheduler'))
            instance = super(TaskSerializer, self).create(validated_data)
            # if has_accounts and accounts_data:
            #     for account_data in accounts_data:
            #         try:
            #             account = Account.objects.get(pk=account_data['id'])
            #             instance.accounts.add(account)
            #         except ObjectDoesNotExist:
            #             pass
            #     instance.save()
            return instance

    def update(self, instance, validated_data):
        # if 'accounts' in validated_data:
        #     accounts_data = validated_data.pop('accounts')
        #     if accounts_data:
        #         for account_data in accounts_data:
        #             try:
        #                 account = Account.objects.get(pk=account_data['id'])
        #                 instance.accounts.add(account)
        #             except ObjectDoesNotExist:
        #                 pass
        return super(TaskSerializer, self).update(instance, validated_data)

    class Meta:
        model = Task
        fields = ('url', 'id', 'creator', 'category', 'scheduler', 'name', 'status', 'accounts', 'start_time',
                  'end_time', 'failed_counts', 'succeed_counts', 'limit_counts', 'accounts_num', 'result',
                  'configure')
        extra_kwargs = {
            'start_time': {'read_only': True},
            'end_time': {'read_only': True},
            'failed_counts': {'read_only': True},
            'succeed_counts': {'read_only': True},
            # 'limit_counts': {'allow_blank': True},
            'accounts_num': {'read_only': True},
            'result': {'read_only': True},
            'configure': {'read_only': True}
        }
