#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 16:35:08 2021

@author: n7
"""

from . import task as tk
import numpy as np
from . import utils as ut


class PS(tk.Server):
    def update_budget(self, current_time):
        if (current_time % self.t == 0):
            self.log_rem_budget(current_time)
            self.set_rem_budget(current_time, self.q)
        if (len(self.get_pending_jobs(current_time)) == 0):
            if (current_time % self.t == 0):
                self.set_rem_budget(current_time + 0.2, self.q)
                self.set_rem_budget(current_time + 0.2, 0)
            else:
                self.set_rem_budget(current_time, 0)

    def get_self_crit_tm(self, current_time):
        # If budget is non-zero, set critical time to current time so that
        # in next iteration either budget is reduced to zero (no pending tasks)
        # or pengind tasks are executed with the available budget.
        if (self.get_rem_budget() != 0):
            return current_time
        else:
            return (current_time//self.t + 1) * self.t


class DS(tk.Server):
    def update_budget(self, current_time):
        self.log_rem_budget(current_time)
        if (current_time % self.t == 0):
            self.set_rem_budget(current_time, self.q)

    def get_self_crit_tm(self, current_time):
        # If budget is non-zero, and tasks are pending, set critical time to
        # current time so that in next iteration pending tasks are executed
        # with the available budget.
        if (self.get_rem_budget() != 0 and
                len(self.get_pending_jobs(current_time)) != 0):
            return current_time
        else:
            return (current_time//self.t + 1) * self.t


class TBS(tk.Server):
    def __init__(self, q, t, index=None):
        tk.Server.__init__(self, q, t, index)
        self.opt_init = False

    def modify_job(self, current_time, job_index):
        if not self.opt_init:
            job = self.jobs[job_index]
            if (job.a > current_time):
                return

            if (job.get_absolute_deadline(current_time) != -1):
                return

            if job_index == 0:
                prev_d = 0
            else:
                prev_d = self.jobs[job_index -
                                   1].get_absolute_deadline(current_time)

            deadline = max(self.jobs[job_index].a, prev_d) + \
                job.c/self.u
            job.set_absolute_deadline(deadline)
        self.set_rem_budget(current_time,
                            sum([job.c_rem
                                 for job in self.jobs[:job_index+1]]))

    def get_self_crit_tm(self, current_time):
        return -1

    def optimize(self):
        opt_possible = False
        for job in self.jobs:
            f = job.exec_logs[0][np.where(job.exec_logs[1] == 1)[0][-1:]]
            if (f.size != 0):
                f = f[0]
                d = job.get_absolute_deadline(job.a)
                if (f < d):
                    job.set_absolute_deadline(f)
                    opt_possible = True
        self.opt_init = True
        return opt_possible

    def get_subplot_req(self):
        # Only 1 For Jobs. Budget is insignificant
        return (1.5,)

    def subplot(self, axs, end_time=-1):
        clrs = ["#FAC549", "#82B366", "#9673A6"]
        for i in range(0, len(self.jobs)):
            self.jobs[i].plt_template(axs[0], end_time=end_time,
                                      y_label="Server",
                                      color=clrs[i], legend=True)
            clr = "#" + hex(int(clrs[i][1:], 16) - 0x404040).upper()[2:]
            ut.arrow(axs[0], self.jobs[i].a, clr, down=False)
            if (len(self.jobs[i].ds_abs) > 0):
                for d in self.jobs[i].ds_abs[:-1]:
                    ut.arrow(axs[0], d, clr, major=False)
                ut.arrow(axs[0], self.jobs[i].ds_abs[-1], clr)


class CBS(tk.Server):
    def modify_job(self, current_time, job_index):
        job = self.jobs[job_index]
        if (job.a > current_time):
            return

        if (job_index != 0 and self.jobs[job_index-1].c_rem != 0):
            return

        if (job.c_rem == job.c and
                job.get_absolute_deadline(current_time) == -1):
            # Not yet served. Apply admission processing.
            if (job_index == 0):
                dl = 0
            else:
                dl = self.jobs[job_index -
                               1].get_absolute_deadline(current_time)
            if (current_time + self.q_rem/self.u > dl):
                dl = current_time + self.t
                self.set_rem_budget(current_time, self.q_rem)
                self.set_rem_budget(current_time, self.q)
            job.set_absolute_deadline(dl)

        elif (job.c_rem != 0 and self.q_rem == 0):
            # Served midway and budget exhausted.
            self.set_rem_budget(current_time, self.q)
            job.set_absolute_deadline(job.get_absolute_deadline(current_time)
                                      + self.t)
        elif (job_index == len(self.jobs)-1 and job.c_rem == 0):
            # All jobs finished
            self.set_rem_budget(current_time, self.q_rem)

    def get_self_crit_tm(self, current_time):
        done = (np.array([job.c_rem for job in self.jobs
                          if job.a < current_time]) == 0).all()
        if (self.q_rem == 0 and not done):
            return current_time
        else:
            return -1
