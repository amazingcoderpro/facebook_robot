#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-04-10
# Function:

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from pyvirtualdisplay import Display
# display = Display(visible=0, size=(900, 800))
# display.start()
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com/")
time.sleep(2)
driver.find_element_by_xpath("./*//input[@name='q']").send_keys("orderplus")
driver.find_element_by_xpath("./*//input[@name='q']").send_keys(Keys.ENTER)
time.sleep(4)
print(driver.current_url)
print(driver.page_source)
driver.quit()
