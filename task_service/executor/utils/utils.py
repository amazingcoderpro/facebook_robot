#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-04-13
# Function: 关于浏览器操作的一些通用方法在此封装

import os, sys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *
from config import logger, get_account_args
import time
import random


def super_click(ele, driver, double=False):
    """
    封装的复合点击函数
    :param ele:需要点击的元素
    :param driver: 浏览器驱动
    :param double: 是否双击
    :return: 成功返回True, 失败返回false
    """
    if not ele:
        return False

    try:
        time.sleep(1)
        ele.click()
    except (WebDriverException, ElementNotVisibleException, ElementNotSelectableException,
            ElementClickInterceptedException, ElementNotInteractableException) as e:
        time.sleep(1)
        action = ActionChains(driver)
        if double:
            action.move_to_element(ele).double_click(ele)
        else:
            action.move_to_element(ele).click(ele)
        action.perform()
    return True


def super_sendkeys(ele, strinfo):
    """
    封装输入的函数
    :param ele: 需要输入的元素
    :param strinfo: 传入的输入内容
    :return:
    """

    if not all([ele, strinfo]):
        return False

    while strinfo:
        n = random.randint(2, 8)
        if n > len(strinfo):
            n = len(strinfo)
        input = strinfo[:n]
        ele.send_keys(input)
        rantime = random.uniform(0.2, 1.5)
        time.sleep(rantime)
        strinfo = strinfo[n:]

    return True


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


