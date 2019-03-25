# -*- coding: utf-8 -*-

from django.urls import path
from django.conf.urls import url, include

from rest_framework import routers

from users.api.category.views import UserCategoryViewSet
from users.api.user.views import UserViewSet


from web_service.views import render_page


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'userCategories', UserCategoryViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'^api/user/', include('users.api.urls')),
    url(r'^api/', include(router.urls)),
    # path('api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^(.*?)$', render_page),
]
