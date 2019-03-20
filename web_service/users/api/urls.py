# -*- coding: utf-8 -*-
from django.conf.urls import url
from users.api import auth_views

# Created by: guangda.lee
# Created on: 2019/3/20
# Function:

urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'^auth$', auth_views.auth),
]
