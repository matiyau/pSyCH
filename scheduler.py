#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 08:08:44 2021

@author: n7
"""

import bisect as bs


class Generic():
    def __init__(self):
        self.tasks = []
        self.crit_tms = [0]
        self.prio_queue = []

    def register_task(self, task):
        self.tasks.append(task)

    def upd_prio_order(self, current_time):
        self.prio_queue = [task for task in self.tasks]

    def create(self, end_time):
        for task in self.tasks:
            task.reset()
        self.crit_tms = [0]
        while True:
            current_time = self.crit_tms[0]
            if (current_time >= end_time):
                break
            self.crit_tms = self.crit_tms[1:]
            if (len(self.crit_tms) == 0):
                self.crit_tms = [current_time]
            self.upd_prio_order(current_time)
            qu = self.prio_queue
            for task in self.prio_queue:
                used_time, crit_tm = task.sanction(current_time,
                                                   self.crit_tms[0] -
                                                   current_time)
                if (crit_tm >= 0) and (crit_tm not in self.crit_tms):
                    bs.insort(self.crit_tms, crit_tm)
                current_time += used_time
