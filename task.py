#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 23:02:01 2021

@author: n7
"""

import numpy as np


class Generic():
    def __init__(self, name, tm_params):
        self.unit = np.gcd.reduce([pair[1] for pair in tm_params.items])
        for key in tm_params:
            setattr(self, key, tm_params[key])
        self.exec_logs = np.array([[], []])

    def query(self, current_time):
        return current_time + self.unit

    def run(self, current_time, exec_time):
        return exec_time

    def sanction(self, current_time, available_time):
        used_time = self.run(current_time, available_time)
        if (used_time > 0):
            if (self.exec_logs.size != 0 and
                    self.exec_logs[0, -1] == current_time):
                self.exec_logs[0, -2:] = [current_time + used_time,
                                          current_time + used_time]
            else:
                self.exec_logs = np.concatenate([self.exec_logs,
                                                 [[current_time, current_time,
                                                   current_time + used_time,
                                                   current_time + used_time],
                                                  [1, 0, 0, 1]]], axis=1)
        return used_time, self.query(current_time+used_time)

    def get_absolute_deadline(self, current_time):
        return current_time + self.unit


class Periodic(Generic):
    def __init__(self, index, c, t, d=None):
        Generic.__init__(self, "Task " + str(index),
                         {"c": c, "t": t, "d": t if d is None else d})
        self.prev_run_rime = -1
        self.pending_time = 0

    def query(self, current_time):
        return (current_time//self.t + 1) * self.t

    def run(self, current_time, available_time):
        self.pending_time += (current_time//self.t -
                              self.prev_run_time//self.t) * self.t
        self.prev_run_time = current_time
        used_time = min(self.pending_time, available_time)
        self.pending_time -= used_time
        return used_time

    def get_absolute_deadline(self, current_time):
        return current_time//self.t + self.d


class Aperiodic(Generic):
    def __init__(self, index, c, a=0, d=0):
        Generic.__init__(self, "Task " + str(index), {"a": a, "c": c, "d": d})

    def query(self, current_time):
        if (current_time < self.a):
            return self.a
        else:
            return -1

    def run(self, current_time, available_time):
        if (current_time >= self.a):
            used_time = min(self.c, available_time)
            self.c -= used_time
            return used_time
        else:
            return 0

    def get_absolute_deadline(self, current_time):
        if (current_time >= self.a):
            return self.a + self.d
        else:
            return -1


class Server(Generic):
    def __init__(self, q, t, index=None):
        Generic.__init__(self, "Task " + str(index),
                         {"q": q, "q_rem": 0, "t": t})
        self.u = q/t
        self.q_rem = 0
        self.q_logs = np.array([[], []])
        self.jobs = []

    def modify_job(self):
        return

    def attach_job(self, job):
        self.modify(job)
        self.jobs.append(job)

    def query(self, current_time):
        # TODO: Change might be reqd
        crit_tm_self = self.get_self_crit_tm(current_time)
        crit_tms_jobs = np.array([job.query(current_time)
                                  for job in self.jobs])
        return min(crit_tm_self, crit_tms_jobs[crit_tms_jobs >= 0].min())

    def run(self, current_time, available_time):
        self.q_logs = np.concatenate([self.q_logs,
                                      [[current_time], [self.q_rem]]], axis=1)
        # TODO: Write Function and Add additional parameters for updating
        # budget
        self.update_budget(current_time)
        self.q_logs = np.concatenate([self.q_logs,
                                      [[current_time], [self.q_rem]]], axis=1)
        available_time = min(available_time, self.q_rem)
        for job in self.jobs:
            used_time, _ = job.sanction(current_time)
            if (used_time != 0):
                break
        self.q_rem -= used_time
        self.q_logs = np.concatenate([self.q_logs, [[current_time + used_time],
                                                    [self.q_rem]]], axis=1)
        return used_time
