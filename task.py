#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 23:02:01 2021

@author: n7
"""

import numpy as np
from matplotlib.ticker import MaxNLocator
from . import utils as ut


class Generic():
    def __init__(self, name, tm_params):
        self.name = name
        self.unit = np.gcd.reduce([pair[1] for pair in tm_params.items()])
        for key in tm_params:
            setattr(self, key, tm_params[key])
        self.exec_logs = np.array([[], []])

    def reset(self):
        self.exec_logs = np.array([[], []])

    def query(self, current_time):
        return current_time + self.unit

    def get_absolute_deadline(self, current_time):
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
                                                  [0, 1, 1, 0]]], axis=1)
        return used_time, self.query(current_time+used_time)

    def get_subplot_req(self):
        # Single element corresponds to one subplot.
        # The value corresponds to the y-proportion
        return (1,)

    def plt_template(self, ax, cust_quant=None, end_time=-1, y_label=None,
                     hide_yticks=True, color="#B3B3B3", legend=False):
        if (cust_quant is None):
            self.exec_logs = ut.filter_sequence(self.exec_logs)
            quant = self.exec_logs
            quant_annots = True
        else:
            quant = cust_quant
            quant_annots = False

        if (end_time == -1):
            end_time = quant[0].max()

        if (y_label is None):
            y_label = self.name

        ax.margins(x=0, y=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_ylabel(y_label, fontsize=14)
        if (hide_yticks):
            ax.get_yaxis().set_ticks([])
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlim(0, end_time)
        ax.set_xticks(np.arange(0, end_time, 1), minor=True)
        ax.set_xticks(np.arange(0, end_time, 2))
        ax.grid(True, which="both")

        if (quant.size == 0):
            return
        ax.set_ylim(0, 2*quant[1].max())
        ax.fill_between(quant[0], quant[1], 0, color=color, label=self.name)
        if (quant_annots):
            brk_pts = quant[0][:-1][quant[1][:-1] !=
                                    quant[1][1:]].reshape(-1, 2)
            for pts in brk_pts:
                if (pts.mean() < end_time):
                    ax.text(pts.mean(), 0.5, str(int(pts[1] - pts[0])),
                            ha="center", va="center", size=14, weight="bold")
        if (legend):
            ax.set_ylim(0, 3*quant[1].max())
            ax.legend(ncol=5)


class Periodic(Generic):
    def __init__(self, index, c, t, d=None):
        Generic.__init__(self, "Task " + str(index),
                         {"c": c, "t": t, "d": t if d is None else d})
        self.prev_run_time = -1
        self.pending_time = 0

    def reset(self):
        Generic.reset(self)
        self.prev_run_time = -1
        self.pending_time = 0

    def query(self, current_time):
        return (current_time//self.t + 1) * self.t

    def get_absolute_deadline(self, current_time):
        return (current_time//self.t)*self.t + self.d

    def run(self, current_time, available_time):
        self.pending_time += (current_time//self.t -
                              self.prev_run_time//self.t) * self.c
        self.prev_run_time = current_time
        used_time = min(self.pending_time, available_time)
        self.pending_time -= used_time
        return used_time

    def subplot(self, axs, end_time=-1):
        self.plt_template(axs[0], end_time=end_time)
        if (end_time==-1):
            end_time = self.exec_logs[0].max()
        if (self.d == self.t):
            for i in range(0, end_time+1, self.t):
                axs[0].plot([i, i], [0, 1], color="#000000")
        else:
            for i in range(0, end_time+1, self.t):
                axs[0].arrow(i, 0, 0, 1.2, width=0.04, head_width=0.3,
                             head_length=0.5, color="#0000ff")
            for i in range(self.d, end_time+1, self.t):
                axs[0].arrow(i, 1.7, 0, -1.2, width=0.04, head_width=0.3,
                             head_length=0.5, color="#ff0000")


class Aperiodic(Generic):
    def __init__(self, index, c, a=0, d=-1):
        Generic.__init__(self, "Task " + str(index), {"a": a, "c": c, "d": d,
                                                      "c_rem": c})
        self.ds_abs = []
        if (d > 0):
            self.set_absolute_deadline(self.a + self.d)

    def reset(self):
        Generic.reset(self)
        self.c_rem = self.c

    def query(self, current_time):
        if (current_time < self.a):
            return self.a
        else:
            return -1

    def set_absolute_deadline(self, deadline):
        i = 0
        while (i < len(self.ds_abs)):
            if (self.ds_abs[i] > deadline):
                break
            i += 1
        self.ds_abs.insert(i, deadline)
        self.ds_abs = self.ds_abs[:i+1]

    def get_absolute_deadline(self, current_time):
        if (current_time >= self.a and len(self.ds_abs) > 0):
            return self.ds_abs[-1]
        else:
            return -1

    def run(self, current_time, available_time):
        if (current_time >= self.a):
            used_time = min(self.c_rem, available_time)
            self.c_rem -= used_time
            return used_time
        else:
            return 0

    def subplot(self, axs, end_time=-1):
        self.plt_template(axs[0], end_time=end_time)
        axs[0].arrow(self.a, 0, 0, 1.2, width=0.04, head_width=0.3,
                     head_length=0.5, color="#0000ff")
        if (self.d > 0):
            axs[0].arrow(self.get_absolute_deadline(self.a), 1.7, 0, -1.2,
                         width=0.04, head_width=0.3, head_length=0.5,
                         color="#ff0000")


class Server(Generic):
    def __init__(self, q, t, index=None):
        Generic.__init__(self, "Task " + str(index),
                         {"q": q, "q_rem": 0, "t": t})
        self.u = q/t
        self.q_rem = 0
        self.q_logs = np.array([[], []])
        self.jobs = []

    def reset(self):
        Generic.reset(self)
        self.q_rem = 0
        self.q_logs = np.array([[], []])
        for job in self.jobs:
            job.reset()

    def query(self, current_time):
        crit_tm_self = [self.get_self_crit_tm(current_time)]
        crit_tms_jobs = np.array([job.query(current_time)
                                  for job in self.jobs])
        crit_tms = np.concatenate([crit_tm_self, crit_tms_jobs])
        crit_tms = crit_tms[crit_tms >= 0]
        return crit_tms.min() if crit_tms.size > 0 else -1

    def get_absolute_deadline(self, current_time):
        self.modify_all_jobs(current_time)
        ds = np.array([job.get_absolute_deadline(current_time)
                       for job in self.jobs if job.c_rem > 0])
        ds = ds[ds > current_time]
        return ds.min() if ds.size != 0 else -1

    def run(self, current_time, available_time):
        self.log_rem_budget(current_time)
        available_time = min(available_time, self.q_rem)
        for job in self.jobs:
            used_time, _ = job.sanction(current_time, available_time)
            if (used_time != 0):
                break
        self.set_rem_budget(current_time + used_time,
                            self.get_rem_budget() - used_time)
        return used_time

    def attach_job(self, job):
        i = 0
        while (i < len(self.jobs)):
            if (self.jobs[i].a > job.a):
                break
            i += 1
        job.name = job.name.replace("Task", "Job")
        self.jobs.insert(i, job)

    def modify_job(self, current_time, job_index):
        return

    def modify_all_jobs(self, current_time):
        for i in range(0, len(self.jobs)):
            self.modify_job(current_time, i)

    def get_pending_jobs(self, current_time):
        return [job for job in self.jobs if (job.a <= current_time and
                                             job.c_rem != 0)]

    def get_self_crit_tm(self, current_time):
        return current_time + self.unit

    def get_rem_budget(self):
        return self.q_rem

    def set_rem_budget(self, current_time, q_rem):
        self.q_rem = q_rem
        self.log_rem_budget(current_time)

    def log_rem_budget(self, current_time):
        self.q_logs = np.concatenate([self.q_logs,
                                      [[current_time], [self.q_rem]]], axis=1)

    def get_subplot_req(self):
        # 1 For Budget and 1 For Jobs
        return (1.5, self.q)

    def subplot(self, axs, end_time=-1):
        clrs = ["#FAC549", "#82B366", "#9673A6"]
        for i in range(0, len(self.jobs)):
            job = self.jobs[i]
            job.plt_template(axs[0], end_time=end_time, y_label="Server",
                             color=clrs[i], legend=True)
            clr = "#" + hex(int(clrs[i][1:], 16) - 0x404040).upper()[2:]
            axs[0].arrow(job.a, 0, 0, 1.2, width=0.04, head_width=0.3,
                         head_length=0.5, color=clr)
            if (len(job.ds_abs) > 0):
                for d in job.ds_abs[:-1]:
                    axs[0].arrow(d, 1.7, 0, -1.2, width=0.04, head_width=0.3,
                                 head_length=0.5, color=clr, ls="dashed")
                axs[0].arrow(job.ds_abs[-1], 1.7, 0, -1.2,
                             width=0.04, head_width=0.3, head_length=0.5,
                             color=clr)

        self.q_logs = ut.filter_sequence(self.q_logs)
        self.plt_template(axs[1], cust_quant=self.q_logs, end_time=end_time,
                          y_label="Budget", hide_yticks=False, color="#FF8000")
