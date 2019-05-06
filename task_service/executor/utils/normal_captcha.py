from config import logger, get_support_args
import time
from urllib import parse
import requests

captcha_arg = get_support_args()


class NormalVerify:
    key_str = "data-sitekey"
    element_class = "div[class='g-recaptcha']"
    captcha_in_api = None
    captcha_res_api = None
    captcha_api_key = None

    def __init__(self, driver):
        NormalVerify.set_captcha_arg()
        self.driver = driver

    @classmethod
    def set_captcha_arg(cls):
        cls.captcha_in_api = captcha_arg.get("captcha_in_api")
        cls.captcha_res_api = captcha_arg.get("captcha_res_api")
        cls.captcha_api_key = captcha_arg.get("captcha_api_key")

    @classmethod
    def get_captcha_id(cls, base64_data):
        """
        获取2capcha第一次请求的结果
        :param base64_data: 页面data-sitekey的值
        :return: captcha_id
        """

        parameter = {
            "key": cls.captcha_api_key,
            "regsense": 0,
            "numeric": 4,
            "method": "base64"
        }
        url = cls.captcha_in_api +"?" + parse.urlencode(parameter)
        logger.info(u"文字验证码验证: 第一次请求url-->{},参数-->{}".format(url, parameter))
        result = requests.post(url, data={"body": base64_data})
        logger.info(u"文字验证码验证: 第一次请求结果-->{}".format(result.text))
        # return
        captcha_id = result.text.split('|')[1]
        captcha_str = NormalVerify.get_captcha_str(captcha_id)
        print(captcha_str)
        return captcha_str

    @classmethod
    def get_captcha_str(cls, captcha_id):
        """
        获取2capcha第二次请求的结果

        :param captcha_id: 2captcha第一次返回的captcha_id
        :return: 返回 2captcha字符串
        """
        parameter = {
            "key": cls.captcha_api_key,
            "action": "get",
            "id": captcha_id
        }
        url = cls.captcha_res_api + "?" + parse.urlencode(parameter)
        logger.info(u"文字验证码验证: 第二次请求url-->{},参数-->{}".format(url,parameter))
        time.sleep(6)
        result = requests.get(url)
        count = 0
        while "CAPCHA_NOT_READY" in result.text and count < 20:
            logger.info(u"文字验证码验证: 第二次请求结果-->{}<--重试{}次".format(result.text,count))
            result = requests.get(url)
            time.sleep(5)
            count += 1
        if "ERROR_CAPTCHA_UNSOLVABLE" in result.text:
            logger.info(u"文字验证码验证: 第二次请求------未解决----{}".format(result.text))
            return False
        return result.text.split('|')[1]
