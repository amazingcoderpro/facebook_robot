#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-04-13
# Function: 关于浏览器操作的一些通用方法在此封装

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *
from selenium.webdriver.chrome.webdriver import WebDriver
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
        rantime = random.uniform(0.5, 5.0)
        time.sleep(rantime)
        strinfo = strinfo[n:]

    return True


# if __name__ == '__main__':
#     super_sendkeys(ele="11", strinfo="ffsafjksa;fjsa;fjsa;fkasfaf")


