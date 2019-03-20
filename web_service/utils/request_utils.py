# -*- coding: utf-8 -*-

import json, logging
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie
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
