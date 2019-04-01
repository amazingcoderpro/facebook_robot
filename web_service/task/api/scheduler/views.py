# -*- coding: utf-8 -*-

from rest_framework import viewsets

from task.api.scheduler.serializers import SchedulerSerializer
from task.models import Scheduler
from utils.request_utils import AuthPermission, handle_order


# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 任务调度类型视图


# ViewSets define the view behavior.
class SchedulerViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Scheduler.objects.all()
    serializer_class = SchedulerSerializer
    permission_classes = [AuthPermission]

    @handle_order
    def get_queryset(self):
        return super(SchedulerViewSet, self).get_queryset()

