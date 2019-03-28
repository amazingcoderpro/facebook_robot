# -*- coding: utf-8 -*-


# Created by: guangda.lee
# Created on: 2019/3/22
# Function: 字符串公共方法


# 创建随机字符串
def random_string(length=32):
    from string import ascii_letters
    from random import randint
    chars = ascii_letters + '~!@#$^*()'
    result = [chars[randint(0, len(chars) - 1)] for i in range(length)]
    return ''.join(result)


# 生成 token 字符串
def generate_token():
    s = random_string()
    from hashlib import md5
    from datetime import datetime
    m = md5()
    m.update((s + datetime.now().strftime('%Y%m%d%H%M%S%Z')).encode())
    m = m.hexdigest()
    return ''.join([m[i]+s[i] for i in range(0, 32)])


# if __name__ == '__main__':
#     print(random_string(23))
#     print(generate_token())
