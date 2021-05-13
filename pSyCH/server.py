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
        """
        Update the budget at the given time by analysing the attached jobs
        and the current time instant itself.

        Parameters
        ----------
        current_time : float
            Time at which budget needs to be updated.

        Returns
        -------
        None.

        """
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
        """
        Return the next time instant at which the server can begin executing
        jobs. This is equal to the next replinishment time if budget is
        exhausted, or current time if budget is avaialble.

        Parameters
        ----------
        current_time : float
            Time at which the start time of the next execution is to be
            computed.

        Returns
        -------
        float
            Oncoming time instant at which the server can start executing
            tasks.

        """
        # If budget is non-zero, set critical time to current time so that
        # in next iteration either budget is reduced to zero (no pending tasks)
        # or pengind tasks are executed with the available budget.
        if (self.get_rem_budget() != 0):
            return current_time
        else:
            return (current_time//self.t + 1) * self.t


class DS(tk.Server):
    def update_budget(self, current_time):
        """
        Update the budget at the given time by analysing the attached jobs
        and the current time instant itself.

        Parameters
        ----------
        current_time : float
            Time at which budget needs to be updated.

        Returns
        -------
        None.

        """
        self.log_rem_budget(current_time)
        if (current_time % self.t == 0):
            self.set_rem_budget(current_time, self.q)

    def get_self_crit_tm(self, current_time):
        """
        Return the next time instant at which the server can begin executing
        jobs.

        Parameters
        ----------
        current_time : float
            Time at which the start time of the next execution is to be
            computed.

        Returns
        -------
        float
            Oncoming time instant at which the server can start executing
            tasks.

        """
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
        """
        Initialize a Total Bandwidth Server.

        Note
        ----
        "q" and "t" are not individually important for a Total Bandwidth
        Server. Only the utilization, which is equal to the ratio "q/t" is
        important.


        Parameters
        ----------
        q : float
            Max budget.
        t : float
            Replinishment period.
        i : int or str or None, optional
            ID for setting the task name. If None, no task name is registered.
            The default is None.

        Returns
        -------
        None.

        """
        tk.Server.__init__(self, q, t, index)
        self.opt_init = False

    def modify_job(self, current_time, job_index):
        """
        Modify job deadline according to its execution status at the given
        current time.

        Parameters
        ----------
        current_time : float
            Time at which the deadline of the specified job needs to be
            modified.
        job_index : int
            Index of the job whose deadline needs to be modified.

        Returns
        -------
        None.

        """
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

    def optimize(self):
        """
        Optimize the deadlines of the attached jobs in the existing schedule.

        Returns
        -------
        float
            True if further optimization is possible.

        """
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
        """
        Returns the height proportions of subplots required by the server
        object in the figure. Only execution logs are required for TBS.
        Budget logs are not required.

        Returns
        -------
        tuple
            Proportion of height of TBS execution subplot in the figure.

        """
        # Only 1 For Jobs. Budget is insignificant
        return (1.5,)

    def subplot(self, axs, end_time=-1):
        """
        Plot the execution logs on the given Axes objects.

        Parameters
        ----------
        axs : numpy.ndarray of matplotlib.axes._subplots.AxesSubplot
            Array of axes objects. The 0th element will be used for plotting
            the execution logs.
        end_time : float, optional
            Maximum time value for the x-axis. If -1, this limit will be
            automatically selected. The default is -1.

        Returns
        -------
        None.

        """
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
        """
        Modify job deadline according to its execution status at the given
        current time.

        Parameters
        ----------
        current_time : float
            Time at which the deadline of the specified job needs to be
            modified.
        job_index : int
            Index of the job whose deadline needs to be modified.

        Returns
        -------
        None.

        """
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
        """
        Return the current time if budget has been exhausted and jobs are
        pending. Otherwise, -1 is returned.

        Parameters
        ----------
        current_time : float
            Time at which remaining budget and pending jobs should be checked.

        Returns
        -------
        float
            Next crucial time instant, if any. -1 otherwise.

        """
        done = (np.array([job.c_rem for job in self.jobs
                          if job.a < current_time]) == 0).all()
        if (self.q_rem == 0 and not done):
            return current_time
        else:
            return -1
