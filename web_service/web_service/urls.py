# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from rest_framework import routers

from account.api.account.views import AccountViewSet
from account.api.category.views import AccountCategoryViewSet
from task.api.category.views import TaskCategoryViewSet
from task.api.scheduler.views import SchedulerViewSet
from task.api.task.views import TaskViewSet
from task.api.task.account.views import TaskAccountViewSet
from users.api.category.views import UserCategoryViewSet
from users.api.user.views import UserViewSet
from vps.api.area.views import AreaViewSet
from vps.api.views import AgentViewSet
from web_service.views import render_page

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
# vps
router.register(r'area', AreaViewSet)
router.register(r'agent', AgentViewSet)
# 用户
router.register(r'userCategories', UserCategoryViewSet)
router.register(r'users', UserViewSet)
# 社交账户
router.register(r'accountCategories', AccountCategoryViewSet)
router.register(r'account', AccountViewSet)
# 任务
router.register(r'taskCategories', TaskCategoryViewSet)
router.register(r'taskSchedulers', SchedulerViewSet)
router.register(r'task', TaskViewSet)
router.register(r'task/(\d*?)/account', TaskAccountViewSet)

urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'^api/user/', include('users.api.urls')),
    url(r'^api/', include(router.urls)),
    # path('api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^(.*?)$', render_page),
]
