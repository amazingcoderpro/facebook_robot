# -*- coding: utf-8 -*-


# Created by: guangda.lee
# Created on: 2019/4/4
# Function: 任务助手


# 处理任务配置
def parse_config(cfg):
    if len(cfg) == 0:
        return dict()
    kv_str = filter(lambda x: len(x) != 0, map(lambda x: x.strip(), cfg.split('\n')))



