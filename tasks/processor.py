#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-20
# Function: 任务的处理器，任务经由各处理器再发往任务队列, 处理器会被定时程序调用


from .workers import app
from db.dao import AgentOpt


# TaskCategoryOpt.save_task_category(category=1, name=u'facebook自动养号', processor='fb_auto_feed')
# TaskCategoryOpt.save_task_category(category=2, name=u'facebook刷好评', processor='fb_click_farming')
# TaskCategoryOpt.save_task_category(category=3, name=u'facebook登录浏览', processor='fb_login')
# TaskCategoryOpt.save_task_category(category=4, name=u'facebook点赞', processor='fb_thumb')
# TaskCategoryOpt.save_task_category(category=5, name=u'facebook发表评论', processor='fb_comment')
# TaskCategoryOpt.save_task_category(category=6, name=u'facebook发表状态', processor='fb_post')
# TaskCategoryOpt.save_task_category(category=7, name=u'facebook聊天', processor='fb_chat')
# TaskCategoryOpt.save_task_category(category=8, name=u'facebook编辑个人信息', processor='fb_edit')

def get_agent_by_account(account):
    agents = list(AgentOpt.get_enable_agents())
    if not agents:
        return None

    if account.active_ip:
        for agent in agents:
            if account.ip == agent.ip:
                return agent
    elif account.active_area:
        for agent in agents:
            if account.active_area == agent.area:
                return agent
    else:
        return agents[0]


def fb_auto_feed(task, account):
    print(1111)
    agent = get_agent_by_account(account)

    if agent:
        queue = agent.queue
        queue_name = queue.split(';')[0]
        routing_key = queue.split(';')[1]

        app.send_task('tasks.tasks.fb_auto_feed',
                      args=(task, account, agent.id),
                      queue=queue_name,
                      routing_key=routing_key)


def fb_click_farming(task, account):
    fb_auto_feed(task, account)
    print('fb_click_farming')


def fb_login(task, account):
    print('fb_login')


def fb_thumb(task, account):
    print('fb_thumb')


def fb_comment(task, account):
    print('fb_comment')
