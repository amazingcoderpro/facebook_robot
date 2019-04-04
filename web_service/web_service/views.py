# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponseRedirect
from web_service.settings import DEBUG

# Created by: guangda.lee
# Created on: 2019/3/19
# Function:


# 页面上下文全局量
GLOBAL_CONTEXT = {
    'static': {
        'main': 79,
        'require': 1,
        'debug': DEBUG
    }
}


# 返回页面
def render_page(request, url=''):
    if url == '':
        url = 'user/login'
    if url == 'favicon.ico':
        return HttpResponseRedirect('/static/img/favicon.ico')
    elif url == 'user/login':
        from django.contrib.auth import logout
        logout(request)
        return render(request, url + '.html', GLOBAL_CONTEXT)
    return render_auth_page(request, url)


# 返回需要登录的页面
def render_auth_page(request, url):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/user/login')
    return render(request, url + '.html', GLOBAL_CONTEXT)
