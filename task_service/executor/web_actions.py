import time
import random
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *
from config import logger


class WebActions:
    def __init__(self, finger_print={}, headless=False):
        """
        初始化
        :param finger_print: 指定浏览器指纹，包括devices/user-agent
        :param headless: 是否指定浏览为无头浏览器, 默认为False
        """
        self.device = finger_print.get("device", "")
        self.user_agent = finger_print.get("user_agent", "")
        self.headless = headless
        self.driver = None
        self.options = None

    def start_chrome(self, force_display=False, force_client=""):
        """
        配置并启动浏览器
        :param force_display: 强制显示chrome界面
        :param force_client: 强制指定启动chrome的环境， 可选输入项为"pc"或“mobile"
        :return: True/False
        """
        try:
            # 定制浏览器启动项
            chrome_options = webdriver.ChromeOptions()
            if self.headless and not force_display:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-gpu')

            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-popup-blocking')  # 禁止弹出拦截
            chrome_options.add_argument("--ignore-certificate-errors")  # 忽略 Chrome 浏览器证书错误报警提示
            chrome_options.add_argument('lang=en_US')

            prefs = {'profile.default_content_setting_values':{'notifications': 2}}
            chrome_options.add_experimental_option('prefs', prefs)

            if self.user_agent and force_client != "mobile":
                chrome_options.add_argument('--user-agent={}'.format(self.user_agent))

            if self.device and force_client != "pc":
                # 移动设备仿真
                mobile_emulation = {
                    'deviceName': self.device
                    # "deviceMetrics": {"width": 600, "height":800, "pixelRatio": 4.0},
                    # "userAgent": "Mozilla/5.0 (Linux; Android 8.0.0; XT1635-02 Build/OPNS27.76-12-22-9)"
                }
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

            chrome_driver = webdriver.Chrome(chrome_options=chrome_options)
            time.sleep(1)

            logger.info("start_chrome device={}, user-agent={}, headless={}, options={}".format(self.device, self.user_agent,
                                                                                    self.headless, chrome_options.arguments))

            self.driver = chrome_driver
            self.options = chrome_options
            return True
        except Exception as e:
            logger.error("The browser did not start successfully, exception: {}".format(str(e)))
            return False

    def quit(self):
        if self.driver:
            self.driver.quit()

    def get_cookies(self):
        if self.driver:
            return self.driver.get_cookies()
        else:
            return None

    def browse_page(self, browse_times=0, distance=0, interval=0, back_top=True):
        """
        浏览页面
        :param browse_times: 浏览次数
        :param distance: 每次间隔距离，默认为零，代表使用随机距离
        :param interval: 间隔时间， 单位秒, 默认为零，代表使用随机停顿时间
        :param back_top: 是否回到顶点
        :return:
        """
        # 浏览页面js
        try:
            logger.info('browse_page start.')
            y_dis = 0
            if browse_times <= 0:
                browse_times = random.randint(3, 15)

            for i in range(browse_times):
                if interval <= 0:
                    self.sleep(1, 10)
                else:
                    time.sleep(interval)

                if distance > 0:
                    y_dis += distance
                else:
                    y_dis += random.randint(20, 200)

                self.driver.execute_script("window.scrollTo(0,{})".format(y_dis))

            if back_top:
                self.driver.execute_script("window.scrollTo(0,0)")

            logger.info('browse_page end.')
            return True
        except Exception as e:
            logger.exception('browse_page exception. e={}'.format(e))
            return False

    def click(self, ele, double=False):
        """
        封装的复合点击函数
        :param ele:需要点击的元素
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
            action = ActionChains(self.driver)
            if double:
                action.move_to_element(ele).double_click(ele)
            else:
                action.move_to_element(ele).click(ele)
            action.perform()
        return True

    def send_keys(self, ele, inputs, smart=True):
        """
        封装输入的函数
        :param ele: 需要输入的元素
        :param inputs: 传入的输入内容
        :param smart: 是否智能输入
        :return:
        """
        if not all([ele, inputs]):
            return False

        try:
            if smart:
                while inputs:
                    n = random.randint(2, 8)
                    if n > len(inputs):
                        n = len(inputs)
                    split_inputs = inputs[:n]
                    ele.send_keys(split_inputs)
                    self.sleep(0.2, 1.5)
                    inputs = inputs[n:]
            else:
                ele.send_keys(inputs)
        except Exception as e:
            logger.info("send_keys catch exception, e={}".format(e))
            return False

        return True

    def sleep(self, lower=2, upper=5):
        """
        随机休眠
        :param lower: 最短休眠时间
        :param upper: 最长休眠时间
        :return:
        """
        if lower > upper:
            tmp = lower
            lower = upper
            upper = tmp

        sleep_time = random.uniform(lower, upper)
        sleep_time = 1 if sleep_time <= 0 else sleep_time
        time.sleep(sleep_time)
        return True
