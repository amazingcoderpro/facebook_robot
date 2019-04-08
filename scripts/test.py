import subprocess
import time
import re


def change_ip_vps():
    try:
        subprocess.call("pppoe-stop", shell=True)
        # subprocess.Popen('pppoe-stop', shell=True, stdout=subprocess.PIPE, encoding='utf8')
        time.sleep(2)
        subprocess.call('pppoe-start', shell=True)
        time.sleep(2)
        pppoe_restart = subprocess.call('pppoe-status', shell=True)
        pppoe_restart.wait()
        pppoe_log = pppoe_restart.communicate()[0]
        adsl_ip = re.findall(r'inet (.+?) peer ', pppoe_log)[0]
        print('[*] New ip address : ' + adsl_ip)
        # return True
        # TaskResult['status'] = 'success'
        # return TaskResult
    except Exception as e:
        print(e)
    #     TaskResult['err_msg'] = str(e)
    #     # change_ip_for_vps()
    # return TaskResult


if __name__ == '__main__':
    count = 1
    while True:
        print('[*] 第%s次拨号' % str(count))
        change_ip_vps()
        count += 1