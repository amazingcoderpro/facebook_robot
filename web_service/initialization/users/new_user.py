# -*- coding: utf-8 -*-

import os
import sys

import django

import codecs
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from web_service.settings import *
from django.conf import settings
try:
    settings.configure(INSTALLED_APPS=INSTALLED_APPS, DATABASES=DATABASES)
    django.setup()
except RuntimeError:
    pass

from users.common import create_category, create_user


# Created by: guangda.lee
# Created on: 2019/3/20
# Function: 初始化一个管理员


ALTER_SQL = '''
ALTER TABLE `user` ADD COLUMN `auth_id` INT NOT NULL;
ALTER TABLE `user` ADD UNIQUE KEY `auth_id` (`auth_id`);
ALTER TABLE `user` ADD CONSTRAINT `user_auth_id_3666ad92_fk_auth_user_id` FOREIGN KEY (`auth_id`) REFERENCES `auth_user` (`id`);
'''


def execute():
    # 初始化用户类别表
    user_category = create_category(u'普通用户', u'可以创建部分或所有类型任务，但无权修改服务器资源')
    manager_category = create_category(u'管理员', u'可创建所有类型任务， 且可以管理服务器资源、修改服务器配置等')
    # 增加测试用户
    create_user(user_category.category, 'user1', 'user1', u'张三', '1;2;3')
    create_user(user_category.category, 'user2', 'user2', u'李四', '4;5;6')
    create_user(manager_category.category, 'admin', 'admin', u'大哥大', '')


if __name__ == "__main__":
    execute()
