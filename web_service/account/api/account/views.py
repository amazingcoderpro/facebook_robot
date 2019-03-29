# -*- coding: utf-8 -*-


from django.http import HttpResponse
from django.views.generic import View
from rest_framework import viewsets

from account.models import Account
from utils.request_utils import AuthPermission, search
from utils.request_utils import response_as_json_without_auth
from .serializers import AccountSerializer, ExportSerializer


# Created by: guangda.lee
# Created on: 2019/3/25
# Function: 社交账户视图


# 处理查询数据集
def get_queryset(request):
    from users.common import user_by_token
    user = user_by_token(request)
    if request.method == 'GET' and 'all' in request.query_params:
        from django.db.models import Q
        queryset = Account.objects.filter(Q(owner_id=user.id) | Q(owner__category__name=u'管理员'))
    else:
        queryset = Account.objects.filter(owner_id=user.id)
    from django.db.models import Q
    queryset = search(request, queryset,
                      lambda qs, keyword: qs.filter(
                          Q(account__icontains=keyword) | Q(email=keyword) | Q(name__icontains=keyword)))
    return queryset


# 社交账户视图
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [AuthPermission]

    def get_queryset(self):
        return get_queryset(self.request)

    # 支持导出
    def list(self, request, *args, **kwargs):
        if 'export' in request.query_params:
            return CSVExportView().get(request, *args, **kwargs)
        return super(AccountViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if 'import' in request.query_params:
            return AccountCSVImportView().post(request, *args, **kwargs)
        return super(AccountViewSet, self).create(request, *args, **kwargs)


# 导出视图类
class CSVExportView(View):
    serializer_class = ExportSerializer

    def get_serializer(self, queryset, many=True):
        return self.serializer_class(
            queryset,
            many=many,
        )

    # 准备序列化实例，重载控制查询数据集
    def prepare_serializer(self, request, *args, **kwargs):
        return self.get_serializer(
            get_queryset(request),
            many=True
        )

    def get(self, request, *args, **kwargs):
        filename = request.query_params['filename'] if 'filename' in request.query_params and len(
            request.query_params['filename']) > 0 else 'account.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        serializer = self.prepare_serializer(request, *args, **kwargs)
        header = ExportSerializer.Meta.fields
        import csv
        writer = csv.DictWriter(response, fieldnames=header)
        writer.writeheader()
        for row in serializer.data:
            writer.writerow(row)
        return response


# 账号导入视图类
class AccountCSVImportView(View):

    def post(self, request, *args, **kwargs):
        from json import dumps
        if 'file' not in request.FILES:
            return HttpResponse(dumps({
                'error': u'no file found'
            }), status=400)
        from io import TextIOWrapper
        import csv
        from django.db import transaction
        f = TextIOWrapper(request.FILES['file'].file, encoding='gb2312')
        data = csv.DictReader(f)
        serializer = AccountSerializer(context={'request': request})
        success = 0
        with transaction.atomic():
            for row in data:
                row = dict(row)
                row['category'] = {
                    'name': row['category']
                }
                if serializer.create(row):
                    success += 1
        return HttpResponse(dumps({
            'success': success
        }), status=201)
