# -*- coding: utf-8 -*-


from rest_framework import viewsets

from account.api.account.serializers import AccountSerializer
from account.models import Account
from utils.request_utils import AuthPermission, search


# Created by: guangda.lee
# Created on: 2019/3/25
# Function: 社交账户视图


class AccountViewSet(viewsets.ModelViewSet):

    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [AuthPermission]

    def get_queryset(self):
        from users.common import user_by_token
        user = user_by_token(self.request)
        if self.request.method == 'GET' and 'all' in self.request.query_params:
            from django.db.models import Q
            queryset = Account.objects.filter(Q(owner_id=user.id) | Q(owner__category__name=u'管理员'))
        else:
            queryset = Account.objects.filter(owner_id=user.id)
        from django.db.models import Q
        queryset = search(self.request, queryset,
                          lambda qs, keyword: qs.filter(Q(account__icontains=keyword) | Q(email=keyword) | Q(name__icontains=keyword)))
        return queryset

