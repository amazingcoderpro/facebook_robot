# -*- coding: utf-8 -*-

from django.shortcuts import render

# Created by: guangda.lee
# Created on: 2019/3/19
# Function:


GLOBAL_CONTEXT = {
    'static': {
        'main': 7,
        'require': 1
    }
}


# 返回页面
def render_page(request, url=''):
    if url == '':
        url = 'user/login'
    return render(request, url + '.html', GLOBAL_CONTEXT) if url == 'user/login' else render_auth_page(request, url)


# 返回需要登录的页面
def render_auth_page(request, url):
    return render(request, 'url' + '.html', GLOBAL_CONTEXT)
