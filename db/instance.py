#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 19-3-16
# Function: 


class Task:

    _TASK_DETAILS = ('name', 'category', 'creator', 'account', 'scheduler')

    def __init__(self, name, category, creator, account, scheduler, status='pending'):
        local_values = locals()
        for att in self._TASK_DETAILS:
            setattr(self, att, local_values[att])

    @property
    def status(self):
        return self.status

    @status.setter
    def status(self, value):
        self.status = value





