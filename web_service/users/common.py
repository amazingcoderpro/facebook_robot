# -*- coding: utf-8 -*-

from django.contrib.auth.models import User as AuthUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from users.models import UserCategory, User

# Created by: guangda.lee
# Created on: 2019/3/20
# Function: 用户通用方法单元


# 创建用户类型
def create_category(name, description):
    try:
        return UserCategory.objects.get(name=name)
    except ObjectDoesNotExist:
        r = UserCategory(name=name, description=description)
        r.save()
        return r


# 创建用户
def create_user(category, username, password, fullname, enable_tasks):
    with transaction.atomic():
        try:
            auth_user = AuthUser.objects.get(username=username)
        except ObjectDoesNotExist:
            auth_user = AuthUser(username=username, first_name='', last_name=fullname)
            auth_user.set_password(password)
            auth_user.save()
        try:
            return User.objects.get(auth_id=auth_user.id)
        except ObjectDoesNotExist:
            u = User(category_id=category, auth_id=auth_user.id, enable_tasks=enable_tasks)
            u.save()
            return u
