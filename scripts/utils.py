#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-04-13
# Function: 关于浏览器操作的一些通用方法在此封装

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *


def super_click(ele, driver, x_off=1, y_off=1):
    """
    封装的复合点击函数
    :param ele:需要点击的元素
    :param driver: 浏览器驱动
    :param x_off: x轴偏移
    :param y_off: y轴偏移
    :return: 成功返回True, 失败返回false
    """
    if not ele:
        return False

    try:
        ele.click()
    except (WebDriverException, ElementNotVisibleException, ElementNotSelectableException,
            ElementClickInterceptedException, ElementNotInteractableException) as e:
        action = ActionChains(driver)
        action.move_to_element_with_offset(ele, x_off, y_off)
        action.click()
        action.perform()

    return True

