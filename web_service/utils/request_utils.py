# -*- coding: utf-8 -*-

import json
import logging
from collections import OrderedDict
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from web_service.settings import DEBUG

# Created by: guangda.lee
# Created on: 2019/3/20
# Function: 请求预处理的公共方法

logger = logging.getLogger(__name__)


class CustomDjangoJSONEncoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            tt = o.timetuple()
            if tt.tm_year >= '1900':
                return o.strftime('%Y/%m/%d %H:%M:%S')
            return '%04d/%02d/%02d %02d:%02d:%02d' % (tt.tm_year, tt.tm_mon, tt.tm_mday, tt.tm_hour, tt.tm_min, tt.tm_sec)
        if isinstance(o, date):
            tt = o.timetuple()
            if tt.tm_year >= '1900':
                return o.strftime('%Y/%m/%d')
            return '%04d/%02d/%02d' % (tt.tm_year, tt.tm_mon, tt.tm_mday)
        return super(CustomDjangoJSONEncoder, self).default(o)


# 解析 request.body 为字典
def pretreatment(f):

    def parse_payload(request, *params):
        if DEBUG:
            return f(request, json.loads(request.body), *params)
        try:
            return f(request, json.loads(request.body), *params)
        except ValueError:
            pass
        except KeyError:
            pass
        except TypeError:
            pass
        except Exception as err:
            logger.error(err)

        return {'error': u'有错误发生'}, 406

    return parse_payload


# 检查登录状态，返回 JSON
def response_as_json(f):

    @login_required(login_url='/err/auth')
    def as_json(request, *params):
        result, status = f(request, request.user.userinfo, *params)
        return JsonResponse(result, status=status, encoder=CustomDjangoJSONEncoder)

    return as_json


# 返回 JSON
def response_as_json_without_auth(f):

    def as_json(request, *params):
        result, status = f(request, *params)
        return JsonResponse(result, status=status, encoder=CustomDjangoJSONEncoder)

    return as_json


# 根据 datatables.net 要求定义列表 API 参数
class CustomDataSetPagination(LimitOffsetPagination):
    limit_query_param = 'length'
    offset_query_param = 'start'

    default_limit = 10
    max_limit = 100

    def get_paginated_response(self, data):
        draw = -1
        if 'query' in self.request.query_params:
            from json import loads
            draw = loads(self.request.query_params['query'])['draw']
        return Response(OrderedDict([
            ('draw', draw),
            ('count', self.count),
            ('recordsFiltered', self.count),
            ('recordsTotal', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data)
        ]))


# 搜索数据
def search(request, queryset, filter):
    if 'query' in request.query_params:
        keyword = json.loads(request.query_params['query'])['search']['value'].strip()
        if keyword != '':
            return filter(queryset, keyword)
    return queryset




# 是否已经登陆权限
class AuthPermission(permissions.BasePermission):
    """
    Auth permission check for common data.
    """

    def has_permission(self, request, view):
        from users.common import user_by_token
        return user_by_token(request)


# 管理员权限
class AdminPermission(permissions.BasePermission):
    """
    Admin permission check for common data.
    """

    def has_permission(self, request, view):
        from users.common import user_by_token, is_admin
        user = user_by_token(request)
        return user and is_admin(user)

