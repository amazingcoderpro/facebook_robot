import re
import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

global PhotoNum
PhotoNum = 587
PWD = "E:/download_image/girl_image/"

url = "https://image.baidu.com/search/index?tn=baiduimage&ct=201326592&lm=-1&cl=2&ie=gb18030&word=%C4%D0%C9%FA%BB%EE%D5%D5%CD%BC%C6%AC&fr=ala&ala=1&alatpl=adress&pos=0&hs=2&xthttps=111111"
url_google = "https://www.google.com/search?biw=1920&bih=938&tbm=isch&sa=1&ei=MkWwXJf5A4fZ-Qa52biQDg&q=%E7%B4%A0%E9%A2%9C%E5%A5%B3%E7%94%9F%E7%94%9F%E6%B4%BB%E7%85%A7%E7%89%87&oq=%E7%B4%A0%E9%A2%9C%E5%A5%B3%E7%94%9F%E7%94%9F%E6%B4%BB%E7%85%A7%E7%89%87&gs_l=img.3...11349.12838..13166...0.0..0.171.1140.0j7......0....1..gws-wiz-img.fhdQ1QffcJY"


def downfile(file, url):
    print("开始下载：", file, url)
    try:
        r = requests.get(url, stream=True)
        with open(file, 'wb') as fd:
            for chunk in r.iter_content():
                fd.write(chunk)
    except Exception as e:
        print("下载失败了", e)


def requestpageText(url):
    try:
        Page = requests.session().get(url)
        Page.encoding = "utf-8"
        return Page.text
    except Exception as e:
        print("联网失败了...重试中", e)
        time.sleep(5)
        print("暂停结束")
        requestpageText(url)


def requestUrl(url):
    global PhotoNum
    print("*******************************************************************")
    print("请求网址：", url)
    chrome_options = Options()
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.maximize_window()
    driver.get(url)
    time.sleep(40)
    # for i in range(1000):
    #     if i % 50 == 0:
    #         time.sleep(2)
    #     driver.execute_script("window.scrollTo(0,{})".format(i*6))

    # items =driver.find_elements(By.XPATH, '//*[@id="imgid"]//div//ul//li//div//a//img//@src')
    items = driver.find_elements_by_css_selector("img.rg_ic.rg_i")
    print(len(items))
    # print(total_image_url)
    for item in items:
        src_link = item.get_attribute('src')
        print("开始下载第{0}张图片".format(PhotoNum))
        filename = PWD + str(PhotoNum) + ".jpg"
        if os.path.isfile(filename):
            print("文件存在：", filename)
            continue
        downfile(filename, src_link)
        PhotoNum += 1
    # requestUrl(urlNext + max_pin_id)


if not os.path.exists(PWD):
    os.makedirs(PWD)

requestUrl(url_google)