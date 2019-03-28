# -*- coding: utf-8 -*-

from rest_framework import viewsets
from rest_framework.response import Response

from users.models import UserCategory
from users.api.category.serializers import CategorySerializer
from utils.request_utils import AdminPermission

# Created by: guangda.lee
# Created on: 2019/3/25
# Function: 用户类型视图


# ViewSets define the view behavior.
class UserCategoryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = UserCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminPermission]
