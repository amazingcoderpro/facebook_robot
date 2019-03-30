# -*- coding: utf-8 -*-

from rest_framework import viewsets

from task.api.task.serializers import TaskSerializer
from task.models import Task
from utils.request_utils import AuthPermission, search
from rest_framework.generics import GenericAPIView


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
        if 'status' in self.request.query_params:
            queryset = queryset.filter(status=self.request.query_params['status'])
        from django.db.models import Q
        queryset = search(self.request, queryset,
                          lambda qs, keyword: qs.filter(Q(name__icontains=keyword)))
        return queryset


# 任务统计
class TaskSumView(GenericAPIView):

    permission_classes = (AuthPermission,)

    def get(self, request, *args, **kwargs):
        from json import dumps
        from django.http import HttpResponse
        from django.db.models import Count
        rs = TaskViewSet(request=request).get_queryset().values('status').annotate(total=Count('status'))
        result = dict()
        for r in rs:
            if r['status'] in result:
                result[r['status']] += r['total']
            else:
                result[r['status']] = r['total']
        return HttpResponse(dumps({
            'data': list(map(lambda x: {
                'status': x,
                'value': result[x]
            }, result))
        }))




