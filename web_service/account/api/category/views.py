# -*- coding: utf-8 -*-

from rest_framework import viewsets

from account.api.category.serializers import CategorySerializer
from account.models import AccountCategory
from utils.request_utils import AuthPermission


# Created by: guangda.lee
# Created on: 2019/3/27
# Function: 社交账户类型视图


# ViewSets define the view behavior.
class AccountCategoryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AccountCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AuthPermission]

