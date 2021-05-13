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
        """
        Initialise a generic task object.

        Parameters
        ----------
        name : str
            Label which can be used to identify the task.
        tm_params : dict
            Timing parameters for the task (E.g., arrival time, period,
            relative deadline, completion time, phase, etc). This base class
            does not utilise these parameters. Thus, in general, any
            key-value pair, which is required by the derived implementation
            can be passed.

        Returns
        -------
        None.

        """
        self.name = name
        self.unit = ut.flt_gcd([pair[1] for pair in tm_params.items()])
        for key in tm_params:
            setattr(self, key, tm_params[key])
        self.exec_logs = np.array([[], []])

    def get_id(self, typ=int):
        """
        Retrieve the task ID from the task name. The task name is assumed to be
        in the format "xxxx<space><id>". The returned ID will be of the
        specified type.

        Parameters
        ----------
        typ : type, optional
            Tyoe of the returned ID (str or int). The default is int.

        Returns
        -------
        str or int
            Task ID, in the specified data type.

        """
        return typ(self.name.split(" ")[1])

    def reset(self):
        """
        Reset the task objects.

        Caution
        -------
        This is only a basic implementation for resetting the tasks.
        The derived class may require additional actions to be performed.

        Returns
        -------
        None.

        """
        self.exec_logs = np.array([[], []])

    def query(self, current_time):
        """
        Get the next instant (wrt the current time), at which a change in the
        task parameters is executed (E.g., completion, new arrival,
        budget exhaustion, budget replinishment, etc.).

        Caution
        -------
        This is only a basic implementation of the query. The derived class
        may require an elaborate implementation to suit its needs.

        Parameters
        ----------
        current_time : float
            Time after which the next crucial instant needs to be computed.

        Returns
        -------
        float
            Next crucial instant in the task execution timeline.

        """
        return current_time + self.unit

    def get_absolute_deadline(self, current_time):
        """
        Return the next absolute deadline wrt the specified current time.

        Caution
        -------
        This is only a syntactic template for returning the absolute deadline.
        The derived class should include an elaborate implementation to suit
        its needs.

        Parameters
        ----------
        current_time : float
            Time instant at at which the oncoming absolute deadline needs
            to be computed.

        Returns
        -------
        float
            Oncoming absolute deadline.

        """
        return current_time + self.unit

    def run(self, current_time, exec_time):
        """
        Run the task from the specified current time instant for a
        (max) duration specified by the execution time.

        Note
        ----
        The execution time is only used in mathematical computation. The
        task is not actually "executed". In other words, the function will
        NOT really require the specified time to execute.

        Caution
        -------
        This is only a syntactic template for executing the task.
        The derived class should include an elaborate implementation to suit
        its needs.

        Parameters
        ----------
        current_time : float
            Time instant from which the task is to be executed.
        exec_time : float
            Execution time sanctioned to the task.

        Returns
        -------
        float
            Execution time actually utilised by the task.

        """
        return exec_time

    def sanction(self, current_time, available_time):
        """
        Sanction a time duration, starting from the specified current time,
        for executing the task. This function first executes the "run"
        function, then updates the execution logs according to the utilised
        time, and finally returns the utilised time along with the next
        crucial time (wrt the end of the utilised time).

        Parameters
        ----------
        current_time : float
            Time from which execution should begin.
        available_time : float
            Available time for the execution.

        Returns
        -------
        float
            Time utilised by the execution. This value is less than or equal
            to the available time.
        float
            Next crucial time, obtained from "query" at the end of execution.

        """
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
        """
        Returns the height proportions of subplots required by the task object
        in the figure. The number of elements in the requrned tuple corresponds
        to the number of subplots required.

        Returns
        -------
        tuple
            Proportions of height for the subplots required by the task object.

        """
        # Single element corresponds to one subplot.
        # The value corresponds to the y-proportion
        return (1,)

    def plt_template(self, ax, cust_quant=None, end_time=-1, y_label=None,
                     hide_yticks=True, color="#B3B3B3", legend=False):
        """
        Template for plotting task timelines on the given axes object.

        Parameters
        ----------
        ax : matplotlib.axes._subplots.AxesSubplot
            Axes object for plotting the timeline.
        cust_quant : numpy.ndarray, or None optional
            Array containing x and y coordinates for creating the timeline.
            If None, the excution logs are selected. The default is None.
        end_time : float, optional
            Maximum time value for the x-axis. If -1, this limit will be
            automatically selected. The default is -1.
        y_label : str or None, optional
            Label for the y-axis. If None, the task name is selected.
            The default is None.
        hide_yticks : bool, optional
            Specified whether the y-axis ticks should be hidden or not.
            The default is True.
        color : (Color format supported by matplotlib), optional
            Color for filling the plot. The default is "#B3B3B3".
        legend : bool, optional
            Specified whether the legend should be displayed or not.
            The default is False.

        Returns
        -------
        None.

        """

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
    def __init__(self, c, t, d=None, phase=0, aj=0, i=None):
        """
        Initialize a periodic task object.

        Parameters
        ----------
        c : float
            Completion time.
        t : float
            Period.
        d : float or None, optional
            Relative deadline. If None, it is assumed to be equal to the task
            period. The default is None.
        phase : float, optional
            Offset for the arrival times of the task. The default is 0.
        aj : float, optional
            Activation jitter. The default is 0.
        i : int or str or None, optional
            ID for setting the task name. If None, no task name is registered.
            The default is None.

        Returns
        -------
        None.

        """
        Generic.__init__(self,
                         ("Task " + str(i)) if i is not None else None,
                         {"c": c, "t": t, "d": t if d is None else d,
                          "p": phase})
        self.aj = aj
        self.prev_run_time = self.p - 1
        self.pending_time = 0

    def reset(self):
        """
        Reset the execution logs, pending time and starting time of the
        previous run.

        Returns
        -------
        None.

        """
        Generic.reset(self)
        self.prev_run_time = self.p - 1
        self.pending_time = 0

    def query(self, current_time):
        """
        Get the next instant (wrt the current time), at which a new instance
        of the task would be released.

        Parameters
        ----------
        current_time : float
            Time at which the next crucial instant needs to be computed.

        Returns
        -------
        float
            Next release time in the execution timeline.

        """
        return ((current_time - self.p)//self.t + 1) * self.t + self.p

    def get_absolute_deadline(self, current_time):
        """
        Get the oncoming absolute deadline (wrt the current time).

        Parameters
        ----------
        current_time : float
            Time at which the oncoming absolute deadline needs to be computed.

        Returns
        -------
        float
            Next absolute deadline in the execution timeline.

        """
        return ((current_time - self.p)//self.t)*self.t + self.d + self.p

    def run(self, current_time, available_time):
        """
        Run the task from the specified current time instant for a
        (max) duration specified by the available time.

        Note
        ----
        The execution time is only used in mathematical computation. The
        task is not actually "executed". In other words, the function will
        NOT really require the specified time to execute.

        Parameters
        ----------
        current_time : float
            Time instant from which the task is to be executed.
        available_time : float
            Execution time sanctioned to the task.

        Returns
        -------
        float
            Execution time actually utilised by the task.

        """
        self.pending_time += ((current_time - self.p)//self.t -
                              (self.prev_run_time - self.p)//self.t) * self.c
        self.prev_run_time = current_time
        used_time = min(self.pending_time, available_time)
        self.pending_time -= used_time
        return used_time

    def subplot(self, axs, end_time=-1):
        """
        Plot the execution logs on the given Axes object, and draw bars or
        arrows for the periods, arrival times and deadlines.

        Parameters
        ----------
        axs : numpy.ndarray of matplotlib.axes._subplots.AxesSubplot
            Array of axes objects. The 0th element will be used for plotting.
        end_time : float, optional
            Maximum time value for the x-axis. If -1, this limit will be
            automatically selected. The default is -1.

        Returns
        -------
        None.

        """
        self.plt_template(axs[0], end_time=end_time)
        if (end_time == -1):
            end_time = int(self.exec_logs[0].max())
        if (self.d == self.t):
            for i in np.arange(self.p, end_time+1, self.t):
                axs[0].plot([i, i], [0, 1.5], color="#000000")
        else:
            for i in np.arange(self.p, end_time+1, self.t):
                ut.arrow(axs[0], i, "#0000ff", down=False)
            for i in np.arange(self.p + self.d, end_time+1, self.t):
                ut.arrow(axs[0], i, "#ff0000")


class Aperiodic(Generic):
    def __init__(self, c, a=0, d=-1, i=None):
        """
        Initialize an aperiodic task object.

        Parameters
        ----------
        c : float
            Relative completion time.
        a : float, optional
            Absolute arrival time. The default is 0.
        d : float, optional
            Relative deadline. The default is -1.
        i : int or str or None, optional
            ID for setting the task name. If None, no task name is registered.
            The default is None.

        Returns
        -------
        None.

        """
        Generic.__init__(self, ("Task " + str(i)) if i is not None else None,
                         {"a": a, "c": c, "d": d, "c_rem": c})
        self.ds_abs = []
        if (d > 0):
            self.set_absolute_deadline(self.a + self.d)

    def reset(self):
        """
        Reset the execution logs and remaining completion time.

        Returns
        -------
        None.

        """
        Generic.reset(self)
        self.c_rem = self.c

    def query(self, current_time):
        """
        Return the arrival time if the current time is less than the
        arrival time. Otherwise -1 os returned.

        Parameters
        ----------
        current_time : float
            Time at which the next crucial instant needs to be returned.

        Returns
        -------
        float
            Next crucial instant (if any) for the task.

        """
        if (current_time < self.a):
            return self.a
        else:
            return -1

    def set_absolute_deadline(self, deadline):
        """
        Set the absolute deadline of the task to a new value

        Parameters
        ----------
        deadline : float
            New absolute deadline for the task.

        Returns
        -------
        None.

        """

        # i = 0
        # while (i < len(self.ds_abs)):
        #     if (self.ds_abs[i] > deadline):
        #         break
        #     i += 1
        # self.ds_abs.insert(i, deadline)
        # self.ds_abs = self.ds_abs[:i+1]
        self.ds_abs.append(deadline)

    def get_absolute_deadline(self, current_time):
        """
        Get the most recently updated absolute deadline if the task has been
        released (current time >= arrival time). Otherwise -1 is returned.

        Parameters
        ----------
        current_time : float
            Time at which the oncoming absolute deadline is to be returned.

        Returns
        -------
        float
            Most recently updated absolute deadline if the task has been
            released (current time >= arrival time), -1 otherwise.

        """
        if (current_time >= self.a and len(self.ds_abs) > 0):
            return self.ds_abs[-1]
        else:
            return -1

    def run(self, current_time, available_time):
        """
        Run the task from the specified current time instant for a
        (max) duration specified by the available time.

        Note
        ----
        The execution time is only used in mathematical computation. The
        task is not aactually "executed". In other words, the function will
        NOT really require the specified time to execute.

        Parameters
        ----------
        current_time : float
            Time instant from which the task is to be executed.
        available_time : float
            Execution time sanctioned to the task.

        Returns
        -------
        float
            Execution time actually utilised by the task.

        """
        if (current_time >= self.a):
            used_time = min(self.c_rem, available_time)
            self.c_rem -= used_time
            return used_time
        else:
            return 0

    def subplot(self, axs, end_time=-1):
        """
        Plot the execution logs on the given Axes object, and arrows for the
        arrival times and deadlines.

        Parameters
        ----------
        axs : numpy.ndarray of matplotlib.axes._subplots.AxesSubplot
            Array of axes objects. The 0th element will be used for plotting.
        end_time : float, optional
            Maximum time value for the x-axis. If -1, this limit will be
            automatically selected. The default is -1.

        Returns
        -------
        None.

        """
        self.plt_template(axs[0], end_time=end_time)
        ut.arrow(axs[0], self.a, "#0000ff", down=False)
        if (self.d > 0):
            ut.arrow(axs[0], self.get_absolute_deadline(self.a), "#ff0000")


class Server(Generic):
    def __init__(self, q, t, i=None):
        """
        Initializes a Server object

        Parameters
        ----------
        q : float
            Max Budget.
        t : float
            Replinishment Period.
        i : int or str or None, optional
            ID for setting the task name. If None, no task name is registered.
            The default is None.

        Returns
        -------
        None.

        """
        # "d" is assigned only as a dummy (for compatibility with prdc tasks)
        Generic.__init__(self, ("Server " + str(i))
                         if i is not None else None,
                         {"q": q, "q_rem": 0, "c": q, "t": t, "d": t})
        self.u = q/t
        self.q_rem = 0
        self.q_logs = np.array([[], []])
        self.jobs = []

    def reset(self):
        """
        Reset the execution logs, budget logs, remaining budget and reset all
        attached jobs.

        Returns
        -------
        None.

        """
        Generic.reset(self)
        self.q_rem = 0
        self.q_logs = np.array([[], []])
        for job in self.jobs:
            job.reset()

    def query(self, current_time):
        """
        Return the next crucial time by quering all attached jobs and
        considering budget replinishment times.

        Parameters
        ----------
        current_time : float
            Time at which the next crucial instant needs to be returned.

        Returns
        -------
        float
            Next crucial instant for the server.

        """
        crit_tm_self = [self.get_self_crit_tm(current_time)]
        crit_tms_jobs = np.array([job.query(current_time)
                                  for job in self.jobs])
        crit_tms = np.concatenate([crit_tm_self, crit_tms_jobs])
        crit_tms = crit_tms[crit_tms >= 0]
        return crit_tms.min() if crit_tms.size > 0 else -1

    def get_absolute_deadline(self, current_time):
        """
        Get the next absolute deadline (wrt the current time) by checking all
        attached jobs.

        Parameters
        ----------
        current_time : float
            Time at which the next absolute deadline needs to be computed.

        Returns
        -------
        float
            Oncoming absolute deadline.

        """
        self.modify_all_jobs(current_time)
        ds = np.array([job.get_absolute_deadline(current_time)
                       for job in self.jobs if job.c_rem > 0])
        ds = ds[ds > current_time]
        return ds.min() if ds.size != 0 else -1

    def run(self, current_time, available_time):
        """
        Run the server from the specified current time instant for a
        (max) duration specified by the available time. The server will allow
        the attached jobs to collectively run for a maximum duration specified
        by the available time.

        Note
        ----
        The execution time is only used in mathematical computation. The
        server is not actually "executed". In other words, the function will
        NOT really require the specified time to execute.

        Parameters
        ----------
        current_time : float
            Time instant from which the server is to be activated.
        available_time : float
            Execution time sanctioned to the server.

        Returns
        -------
        float
            Execution time actually utilised by the server.

        """
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
        """
        Attach an aperiodic job to the server.

        Parameters
        ----------
        job : pSyCH.task.Aperiodic
            Aperioidc job to be attached to the server.

        Returns
        -------
        None.

        """
        i = 0
        while (i < len(self.jobs)):
            if (self.jobs[i].a > job.a):
                break
            i += 1
        if (job.name is None):
            job.name = "Job " + str(len(self.jobs) + 1)
        elif ("Task" in job.name):
            job.name = job.name.replace("Task", "Job")
        self.jobs.insert(i, job)

    def attach_jobs(self, jobs):
        """
        Attach multiple aperiodic jobs to the server.

        Parameters
        ----------
        jobs : list of pSyCH.task.Aperiodic
            List of perioidc jobs to be attached to the server.

        Returns
        -------
        None.

        """
        for job in jobs:
            self.attach_job(job)

    def modify_job(self, current_time, job_index):
        """
        Modify the parameters of the given job at the specified time.

        Caution
        -------
        This is only a syntactic template for modifying the tasks. The derived
        class (for a specific type of Server) may require an elaborate
        implementation.

        Parameters
        ----------
        current_time : float
            Time instant at which the job parameters should be modified.
        job_index : int
            ID of the job which is to be modified.

        Returns
        -------
        None.

        """
        return

    def modify_all_jobs(self, current_time):
        """
        Modify the parameters of all attached job at the specified time.

        Parameters
        ----------
        current_time : float
            Time instant at which the job parameters should be modified.

        Returns
        -------
        None.

        """
        for i in range(0, len(self.jobs)):
            self.modify_job(current_time, i)

    def get_pending_jobs(self, current_time):
        """
        Get a list of jobs which have been released but not yet completed at
        the given time

        Parameters
        ----------
        current_time : float
            Time at which pending jobs need to be returned.

        Returns
        -------
        list of pSyCH.task.Aperiodic
            List of pending jobs.

        """
        return [job for job in self.jobs if (job.a <= current_time and
                                             job.c_rem != 0)]

    def get_self_crit_tm(self, current_time):
        """
        Return the next crucial time for the server.

        Caution
        -------
        This is only a syntactic template for modifying the tasks. The derived
        class (for a specific type of Server) may require an elaborate
        implementation.

        Parameters
        ----------
        current_time : float
            Time instant at which the next crucial time is to be computed.

        Returns
        -------
        float
            Next crucial time instant (wrt the specified current time).

        """
        return -1

    def get_rem_budget(self):
        """
        Return the remaining budget of the server.

        Returns
        -------
        float
            Budget remaining with the server.

        """
        return self.q_rem

    def set_rem_budget(self, current_time, q_rem):
        """
        Set and log the remaining budget at the specified time to the
        specified value.

        Parameters
        ----------
        current_time : float
            Time coordinate for logging the updated budget.
        q_rem : float
            New value for the remaining budget.

        Returns
        -------
        None.

        """
        self.q_rem = q_rem
        self.log_rem_budget(current_time)

    def log_rem_budget(self, current_time):
        """
        Add the remaining budget at the current time to the budget logs.

        Parameters
        ----------
        current_time : float
            Time coordinate for logging the current remaining budget.

        Returns
        -------
        None.

        """
        self.q_logs = np.concatenate([self.q_logs,
                                      [[current_time], [self.q_rem]]], axis=1)

    def get_subplot_req(self):
        """
        Returns the height proportions of subplots required by the server
        object in the figure. (1.5 for execution logs and max budget for
        budget logs).

        Returns
        -------
        tuple
            Proportions of height for the budget and execution subplots.

        """
        return (1.5, self.q)

    def subplot(self, axs, end_time=-1):
        """
        Plot the execution and budget logs on the given Axes objects.

        Parameters
        ----------
        axs : numpy.ndarray of matplotlib.axes._subplots.AxesSubplot
            Array of axes objects. The 0th element will be used for plotting
            the execution and the 1st for plotting budget.
        end_time : float, optional
            Maximum time value for the x-axis. If -1, this limit will be
            automatically selected. The default is -1.

        Returns
        -------
        None.

        """
        clrs = ["#FAC549", "#82B366", "#9673A6"]
        for i in range(0, len(self.jobs)):
            job = self.jobs[i]
            job.plt_template(axs[0], end_time=end_time, y_label=self.name,
                             color=clrs[i], legend=True)
            clr = "#" + hex(int(clrs[i][1:], 16) - 0x404040).upper()[2:]
            ut.arrow(axs[0], job.a, clr, down=False)
            if (len(job.ds_abs) > 0):
                for d in job.ds_abs[:-1]:
                    ut.arrow(axs[0], d, clr, major=False)
                ut.arrow(axs[0], job.ds_abs[-1], clr)

        self.q_logs = ut.filter_sequence(self.q_logs)
        self.plt_template(axs[1], cust_quant=self.q_logs, end_time=end_time,
                          y_label="Budget", hide_yticks=False, color="#FF8000")
