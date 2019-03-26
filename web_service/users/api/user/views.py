# -*- coding: utf-8 -*-

from rest_framework import viewsets
from rest_framework.response import Response

from users.models import User
from users.api.user.serializers import UserSerializer

# Created by: guangda.lee
# Created on: 2019/3/25
# Function: 用户目录视图


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    # 移除用户
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            return super(UserViewSet, self).destroy(request, *args, **kwargs)
        finally:
            # 删除 auth_user 中的关联数据
            instance.auth.delete()

