# -*- coding: utf-8 -*-

from django.db import transaction
from rest_framework import serializers

from account.models import Account
from task.api.category.serializers import CategorySerializer
from task.api.scheduler.serializers import SchedulerSerializer
from task.models import Task, Scheduler, TaskAccountRelationship
from users.api.user.serializers import UserSerializer


# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 任务序列化类


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    category = CategorySerializer()
    creator = UserSerializer(read_only=True)
    scheduler = SchedulerSerializer()
    # accounts = AccountSerializer(many=True)

    @staticmethod
    def update_timestamp(instance):
        from datetime import datetime
        instance.last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        instance.save()

    def create(self, validated_data):
        validated_data['category'] = CategorySerializer().create(validated_data.pop('category'))
        has_accounts = 'accounts' in validated_data
        if has_accounts:
            accounts_data = validated_data.pop('accounts')
        from users.common import user_by_token
        user = user_by_token(self.context.get("request"))
        validated_data['creator'] = user
        with transaction.atomic():
            scheduler_data = validated_data.pop('scheduler')
            validated_data['scheduler'] = Scheduler.objects.create(**scheduler_data)  # SchedulerSerializer().create(scheduler_data)  # (validated_data.pop('scheduler'))
            account_count = int(validated_data['accounts_num'])
            instance = super(TaskSerializer, self).create(validated_data)
            # if has_accounts and accounts_data:
            #     for account_data in accounts_data:
            #         try:
            #             account = Account.objects.get(pk=account_data['id'])
            #             instance.accounts.add(account)
            #         except ObjectDoesNotExist:
            #             pass
            #     instance.save()
            # 分配账号
            from django.db.models import Q
            accounts = Account.objects.filter(Q(owner_id=user.id) | Q(owner__category__name=u'管理员'),
                                              Q(status='valid')).order_by('using')[:account_count]
            for account in accounts:
                TaskAccountRelationship.objects.create(account_id=account.id, task_id=instance.id)
            self.update_timestamp(instance)
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
        if 'scheduler' in validated_data and instance.status in ('new', 'pending', 'pausing', 'running') and instance.scheduler.mode in (1, 2):
            instance.scheduler.end_date = validated_data.pop('scheduler')['end_date']
            instance.scheduler.save()
        self.update_timestamp(instance)
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
            # 'accounts_num': {'read_only': True},
            'result': {'read_only': True},
            'configure': {'allow_blank': True}
        }
