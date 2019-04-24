# -*- coding: utf-8 -*-

from django.views import View
from django.shortcuts import HttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
from utils.request_utils import AdminPermission, search, handle_order
from vps.serializers import AgentSerializer,AreaSerializer,AreaAccountCountSerializer
from vps.models import Agent,Area
import json


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
        print(queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        # if 'all' in request.query_params:
        #     serializer = AgentSerializer(self.get_queryset(), many=True, context={'request': request})
        #     return Response(serializer.data)
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

    def list(self, request, *args, **kwargs):
        if 'all' in request.query_params:
            serializer = AreaSerializer(self.get_queryset(), many=True, context={'request': request})
            return Response(serializer.data)
        return super(AreaViewSet, self).list(request, *args, **kwargs)



class AreaAccountCount(View):

    def get(self, request):
        queryset = Area.objects.all()
        ser = AreaAccountCountSerializer(instance=queryset, many=True)
        # result = list(map(lambda item:{item["name"]:item["count"]},ser.data))
        # result = {item["name"]:item["count"] for item in ser.data}
        ret = json.dumps(ser.data,ensure_ascii=False)
        return HttpResponse(ret)