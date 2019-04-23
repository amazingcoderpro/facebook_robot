#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-04-13
# Function: 关于浏览器操作的一些通用方法在此封装

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *
import time


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

