# -*- coding: utf-8 -*-

from rest_framework import viewsets

from utils.request_utils import search, handle_order
from vps.api.area.serializers import AreaSerializer
from vps.models import Area


# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 区域视图


# ViewSets define the view behavior.
class AreaViewSet(viewsets.ModelViewSet):

    queryset = Area.objects.all()
    serializer_class = AreaSerializer

    @handle_order
    def get_queryset(self):
        queryset = Area.objects.all()
        queryset = search(self.request, queryset,
                          lambda qs, keyword: qs.filter(name__icontains=keyword))
        return queryset
