# -*- coding: utf-8 -*-

from rest_framework import viewsets

from account.api.account.views import CSVExportView
from account.models import Account
from task.api.task.account.serializers import TaskAccountSerializer
from task.models import TaskAccountRelationship
from utils.request_utils import AuthPermission


# Created by: guangda.lee
# Created on: 2019/3/29
# Function: 任务关联账号视图


# ViewSets define the view behavior.
class TaskAccountViewSet(viewsets.ModelViewSet):
    queryset = TaskAccountRelationship.objects.all()
    serializer_class = TaskAccountSerializer
    permission_classes = [AuthPermission]

    def get_queryset(self):
        return TaskAccountRelationship.objects.filter(task_id=self.args[0])

    # 支持账号导出
    def list(self, request, *args, **kwargs):
        if 'export' in request.query_params:
            return AccountCSVExportView().get(request, *args, **kwargs)
        return super(TaskAccountViewSet, self).list(request, *args, **kwargs)


# 账号导出视图类
class AccountCSVExportView(CSVExportView):

    def prepare_serializer(self, request, *args, **kwargs):
        return self.get_serializer(
            Account.objects.filter(
                pk__in=TaskAccountRelationship.objects.filter(task_id=args[0]).values_list('account_id', flat=True)),
            many=True
        )


