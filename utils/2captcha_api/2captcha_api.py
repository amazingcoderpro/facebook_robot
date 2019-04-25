import time
from urllib import parse
import requests
from selenium import webdriver

# 2captcha
CAPTCHA_IN_API = "http://2captcha.com/in.php"
CAPTCHA_RES_API = "http://2captcha.com/res.php"
API_KEY = "f4f632da069e2208dd4e5ede45efd683"

# web
# CURRENT_URL = "https://www.google.com/recaptcha/api2/demo"
CURRENT_URL = 'https://www.facebook.com/checkpoint/block/'
ELEMENT_STR = "data-sitekey"


def get_captcha_str(api_url, captcha_id, key):
    p = {
        "key": key,
        "action": "get",
        "id": captcha_id
    }
    url = api_url + "?" + parse.urlencode(p)
    result = requests.get(url)
    print(result.text, 1)
    count = 0
    while 'CAPCHA_NOT_READY' in result.text and count<20:
        result = requests.get(url)
        print(result.text, 2)
        time.sleep(5)
        count += 1
    print(result.text, 3)
    if "ERROR_CAPTCHA_UNSOLVABLE" in result.text:
        return None

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
    # ele = browser.find_element_by_id("recaptcha-demo")# div[calss='g-recaptcha'] / div['data-sit']
    # browser.switch_to_frame()
    browser.switch_to.frame(browser.find_element_by_id("captcha-recaptcha"))
    ele = browser.find_element_by_css_selector("div[class='g-recaptcha']")
    value = ele.get_attribute(element_str)
    print(value)
    return value


def start_chrome(current_url):
    browser = webdriver.Chrome()
    browser.get(current_url)
    browser.set_window_size(800, 800)
    return browser


if __name__ == '__main__':
    browser = start_chrome(CURRENT_URL)
    time.sleep(60)
    print(browser.current_url)

    value = serach_sitekey(ELEMENT_STR)

    # value = "6Lc9qjcUAAAAADTnJq5kJMjN9aD1lxpRLMnCS2TR"
    captcha_id = get_captcha_id(CAPTCHA_IN_API, value, API_KEY)
    time.sleep(30)
    answer = get_captcha_str(CAPTCHA_RES_API, captcha_id, API_KEY)
    print(answer)

    # if answer:
        browser.execute_script('document.getElementById("g-recaptcha-response").innerHTML="{}"'.format(answer))
    #     # browser.find_element_by_css_selector('input[id="recaptcha-demo-submit"]').click()
    #     browser.find_element_by_css_selector("button[id='checkpointSubmitButton']").click()