# -*- coding: utf-8 -*-

from rest_framework import viewsets
from utils.request_utils import AdminPermission, search, handle_order
from vps.serializers import AgentSerializer,AreaSerializer
from vps.models import Agent,Area


# ViewSets define the view behavior.
class AgentViewSet(viewsets.ModelViewSet):

    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [AdminPermission]

    @handle_order
    def get_queryset(self):
        queryset = Agent.objects.all()
        from django.db.models import Q
        queryset = search(self.request, queryset,
                          lambda qs, keyword: qs.filter(Q(queue_name__icontains=keyword) | Q(area__icontains=keyword)))
        return queryset

    def list(self, request, *args, **kwargs):
        if 'all' in request.query_params:
            from rest_framework.response import Response
            serializer = AgentSerializer(self.get_queryset(), many=True, context={'request': request})
            return Response(serializer.data)
        return super(AgentViewSet, self).list(request, *args, **kwargs)


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