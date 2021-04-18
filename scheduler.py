#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 08:08:44 2021

@author: n7
"""

from . import task as tk
import bisect as bs
import numpy as np


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


class EDF(Generic):
    def upd_prio_order(self, current_time):
        unq = np.unique([task.get_absolute_deadline(current_time)
                         for task in self.tasks])

        # Push negative deadlines to the end
        unq = np.concatenate([unq[unq >= 0], unq[unq < 0]])
        self.prio_queue = []
        for d in unq:
            srvs = [task for task in self.tasks if
                    ((task.get_absolute_deadline(current_time) == d) and
                     isinstance(task, tk.Server))]
            prdc = [task for task in self.tasks if
                    ((task.get_absolute_deadline(current_time) == d) and
                     isinstance(task, tk.Periodic))]
            self.prio_queue += srvs
            self.prio_queue += prdc


class RM(Generic):
    def upd_prio_order(self, current_time):
        if (len(self.prio_queue) == 0):
            unq = np.unique([task.t for task in self.tasks])
            for t in unq:
                srvs = [task for task in self.tasks if
                        ((task.t == t) and isinstance(task, tk.Server))]
                prdc = [task for task in self.tasks if
                        ((task.t == t) and isinstance(task, tk.Periodic))]
                self.prio_queue += srvs
                self.prio_queue += prdc

        for task in self.tasks:
            if (isinstance(task, tk.Server)):
                task.update_budget(current_time)


class DM(Generic):
    def upd_prio_order(self, current_time):
        if (len(self.prio_queue) == 0):
            unq = np.unique([task.t for task in self.tasks])
            for t in unq:
                srvs = [task for task in self.tasks if
                        ((task.t == t) and isinstance(task, tk.Server))]
                prdc = [task for task in self.tasks if
                        ((task.t == t) and isinstance(task, tk.Periodic))]
                self.prio_queue += srvs
                self.prio_queue += prdc
