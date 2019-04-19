import time
from urllib import parse
import requests
from selenium import webdriver

# 2captcha
CAPTCHA_IN_API = "http://2captcha.com/in.php"
CAPTCHA_RES_API = "http://2captcha.com/res.php"
API_KEY = "f4f632da069e2208dd4e5ede45efd683"

# web
CURRENT_URL = "https://www.google.com/recaptcha/api2/demo"
ELEMENT_STR = "data-sitekey"


def get_captcha_str(api_url, captcha_id, key):
    p = {
        "key": key,
        "action": "get",
        "id": captcha_id
    }
    url = api_url + "?" + parse.urlencode(p)
    result = requests.get(url)
    while 'CAPCHA_NOT_READY' in result:
        result = requests.get(url).text
        time.sleep(5)
    return result.text.split('|')[1]


def get_captcha_id(current_url, value, api_key):
    parameter = {
        "key": api_key,
        "googlekey": value,
        "pageurl": current_url,
        "method": "userrecaptcha"
    }
    url = current_url + "?" + parse.urlencode(parameter)
    result = requests.get(url)
    print(result.text)
    return result.text.split('|')[1]


def serach_sitekey(element_str):
    ele = browser.find_element_by_id("recaptcha-demo")
    value = ele.get_attribute(element_str)
    return value


def start_chrome(current_url):
    browser = webdriver.Chrome()
    browser.get(current_url)
    browser.set_window_size(800, 800)
    return browser


if __name__ == '__main__':
    browser = start_chrome(CURRENT_URL)
    time.sleep(3)
    value = serach_sitekey(ELEMENT_STR)
    captcha_id = get_captcha_id(CAPTCHA_IN_API, value, API_KEY)
    time.sleep(90)
    answer = get_captcha_str(CAPTCHA_RES_API, captcha_id, API_KEY)
    browser.execute_script('document.getElementById("g-recaptcha-response").innerHTML="{}"'.format(answer))
    browser.find_element_by_css_selector('input[id="recaptcha-demo-submit"]').click()