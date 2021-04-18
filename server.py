#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 16:35:08 2021

@author: n7
"""

from . import task as tk
import numpy as np


class TBS(tk.Server):
    def modify_job(self, current_time, job_index):
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
                self.set_rem_budget(current_time, self.q)
            job.set_absolute_deadline(dl)

        elif (job.c_rem != 0 and self.q_rem == 0):
            # Served midway and budget exhausted.
            self.set_rem_budget(current_time, self.q)
            job.set_absolute_deadline(job.get_absolute_deadline(current_time)
                                      + self.t)

    def get_self_crit_tm(self, current_time):
        done = (np.array([job.c_rem for job in self.jobs
                          if job.a < current_time]) == 0).all()
        if (self.q_rem == 0 and not done):
            return current_time
        else:
            return -1
