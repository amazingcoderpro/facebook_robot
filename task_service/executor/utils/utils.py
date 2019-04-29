#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-04-13
# Function: 关于浏览器操作的一些通用方法在此封装

import os, sys
from config import logger, get_account_args
import random


def download_photo(account, gender):
    logger.info('start download photo from server, account={}, gender={}'.format(account, gender))
    remote_photo_path = get_account_args()['remote_photo_path']
    local_photo_path = os.path.join(os.path.dirname(os.path.dirname(sys.path[0])),
                                    get_account_args()['local_photo_path'])
    save_path = os.path.join(local_photo_path, "{}.jpg".format(account))
    # 下载保存到本地
    # do something

    # 测试阶段直接从本地拿图片, 根据性别请求一张图片
    if gender == 0:
        random_photo_dir = os.path.join(local_photo_path, 'female')
    else:
        random_photo_dir = os.path.join(local_photo_path, 'male')

    photos = os.listdir(random_photo_dir)
    rad_idx = random.randint(1, 10000) % len(photos)
    random_photo_name = os.path.join(random_photo_dir, photos[rad_idx])

    # 把照片从随机池中取到账号池中
    # shutil.move(random_photo_name, save_path)
    save_path = random_photo_name

    logger.info(
        'download photo from server, account={}, gender={}, save_path={}'.format(account, gender, save_path))
    return save_path


def get_photo(account, gender):
    try:
        local_photo_path = os.path.join(os.path.dirname(os.path.dirname(sys.path[0])),
                                        get_account_args()['local_photo_path'])

        # 先在本地找
        local_photo_name = os.path.join(local_photo_path, "{}.jpg".format(account))
        if os.path.exists(local_photo_name):
            logger.info('get photo from local path={}'.format(local_photo_name))
            return local_photo_name
        else:
            # 如果本地没有，则去下载
            return download_photo(account, gender)
    except Exception as e:
        logger.error('get photo failed. account={}, e={}'.format(account, e))
        return ''

# if __name__ == '__main__':
#     super_sendkeys(ele="11", strinfo="ffsafjksa;fjsa;fjsa;fkasfaf")


