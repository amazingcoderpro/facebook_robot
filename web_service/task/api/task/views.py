# -*- coding: utf-8 -*-

from rest_framework import viewsets

from task.api.task.serializers import TaskSerializer
from task.models import Task
from utils.request_utils import AuthPermission, AdminPermission, search


# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 任务视图


# ViewSets define the view behavior.
class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AuthPermission, ]

    def get_queryset(self):
        from users.common import user_by_token, is_admin
        user = user_by_token(self.request)
        queryset = Task.objects.all() if is_admin(user) else Task.objects.filter(creator_id=user.id)
        from django.db.models import Q
        queryset = search(self.request, queryset,
                          lambda qs, keyword: qs.filter(Q(name__icontains=keyword)))
        return queryset


