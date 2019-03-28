# -*- coding: utf-8 -*-

from rest_framework import viewsets

from task.api.category.serializers import CategorySerializer
from task.models import TaskCategory
from utils.request_utils import AuthPermission, AdminPermission, search


# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 任务类型视图


# ViewSets define the view behavior.
class TaskCategoryViewSet(viewsets.ModelViewSet):

    queryset = TaskCategory.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [AuthPermission, ]
        else:
            self.permission_classes = [AdminPermission, ]

        return super(TaskCategoryViewSet, self).get_permissions()

    def get_queryset(self):
        queryset = self.queryset
        from django.db.models import Q
        queryset = search(self.request, queryset,
                          lambda qs, keyword: qs.filter(
                              Q(name__icontains=keyword) | Q(processor=keyword)))
        return queryset


