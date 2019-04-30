# coding=utf-8

import requests
from bs4 import BeautifulSoup
user_agent = open("xiaoning.text", 'w')
for i in range(1, 10):
    url = "https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/{}".format(i)
    page = requests.get(url)   # 打开网址
    bs0bj = BeautifulSoup(page.text)
    namelist = bs0bj.findAll("a")
    for name in namelist:
        if "Mozilla" in name.text:
            print(name.text)
            user_agent.write(name.text+"\n")

user_agent.close()
