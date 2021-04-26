#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 08:08:44 2021

@author: n7
"""

from . import task as tk
from . import utils as ut
import bisect as bs
from copy import deepcopy as dc
import math
from matplotlib import pyplot as plt
import numpy as np
import svgling as sl


class Generic():
    def __init__(self):
        self.tasks = []
        self.crit_tms = [0]
        self.prio_queue = []
        self.end_time = 0
        self.unit = 1

    def register_task(self, task):
        if (task.name is None):
            if isinstance(task, tk.Server):
                family = [tsk for tsk in self.tasks
                          if isinstance(tsk, tk.Server)]
                fam_name = "Server"
            if (isinstance(task, tk.Periodic) or
                    isinstance(task, tk.Aperiodic)):
                family = [tsk for tsk in self.tasks
                          if (isinstance(task, tk.Periodic) or
                              isinstance(task, tk.Aperiodic))]
                fam_name = "Task"
            if (len(family) == 0):
                task.name = fam_name
            else:
                if (len(family) == 1):
                    family[0].name = fam_name + " 1"
                task.name = fam_name + " " + str(len(family) + 1)
        self.tasks.append(task)

    def register_tasks(self, tasks):
        for task in tasks:
            self.register_task(task)

    def upd_prio_order(self, current_time):
        self.prio_queue = [task for task in self.tasks]

    def create(self, end_time):
        self.end_time = end_time
        for task in self.tasks:
            task.reset()
        self.unit = ut.flt_gcd([task.unit for task in self.tasks])
        self.crit_tms = [0]
        end_time_auto = 0
        done = False
        while True:
            tmp = dc(self.crit_tms)
            current_time = self.crit_tms[0]
            prev_time = current_time
            self.crit_tms = self.crit_tms[1:]
            if (len(self.crit_tms) == 0):
                self.crit_tms = [current_time]
            self.upd_prio_order(current_time)
            for task in self.prio_queue:
                used_time, crit_tm = task.sanction(current_time,
                                                   self.crit_tms[0] -
                                                   current_time)
                if (crit_tm >= 0) and (crit_tm not in self.crit_tms):
                    bs.insort(self.crit_tms, crit_tm)
                current_time += used_time
                if (current_time >= self.end_time):
                    done = True
                    break
            if (tmp == self.crit_tms):
                bs.insort(self.crit_tms, self.crit_tms[0] + self.unit)
            if (prev_time != current_time):
                end_time_auto = current_time
            if done:
                self.upd_prio_order(current_time)
                for task in self.tasks:
                    if (isinstance(task, tk.Aperiodic)):
                        end_time_auto = max(end_time_auto,
                                            task.get_absolute_deadline(
                                                current_time))
                break
        self.end_time = end_time_auto

    def plot(self, op_path=None):
        plt_reqs = [task.get_subplot_req() for task in self.tasks]

        plt_counts = [len(i) for i in plt_reqs]
        plt_ratios = []
        for plt_req in plt_reqs:
            for ratio in plt_req:
                plt_ratios.append(ratio)
        fig, ax = plt.subplots(sum(plt_counts), 1, sharex=True,
                               gridspec_kw={'height_ratios': plt_ratios})
        if (sum(plt_counts) == 1):
            ax = [ax]
        j = 0
        for i in range(0, len(self.tasks)):
            self.tasks[i].subplot([ax[k] for k in range(j, j+plt_counts[i])],
                                  end_time=self.end_time)
            j += plt_counts[i]

        fig.set_size_inches(ax[0].get_xlim()[1]/4, sum(plt_counts))
        fig.tight_layout()
        if (op_path is not None):
            fig.savefig(op_path)
        return fig

    def full(self, tasks, time, op_path=None):
        self.register_tasks(tasks)
        self.create(time)
        fig = self.plot(op_path)
        return fig


class FCFS(Generic):
    def upd_prio_order(self, current_time):
        if (len(self.prio_queue) == 0):
            srt = [i for _, i in
                   sorted(zip([task.a for task in self.tasks],
                              [j for j in range(len(self.tasks))]))]
            self.prio_queue = [self.tasks[i] for i in srt]
            total_time = 0
            for task in self.tasks:
                total_time = max(total_time, task.a) + task.c
            bs.insort(self.crit_tms, total_time)
            self.end_time = total_time


class EDD(Generic):
    def upd_prio_order(self, current_time):
        if (len(self.prio_queue) == 0):
            srt = [i for _, i in
                   sorted(zip([task.d for task in self.tasks],
                              [j for j in range(len(self.tasks))]))]
            self.prio_queue = [self.tasks[i] for i in srt]
            total_c = sum([task.c for task in self.tasks])
            bs.insort(self.crit_tms, total_c)
            self.end_time = total_c


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
            aprd = [task for task in self.tasks if
                    ((task.get_absolute_deadline(current_time) == d) and
                     isinstance(task, tk.Aperiodic))]
            self.prio_queue += srvs
            self.prio_queue += prdc
            self.prio_queue += aprd


class Bratley(Generic):
    def get_tree(self, elapsed_time, tasks, pruning=True):
        tree = []
        for i in range(0, len(tasks)):
            task = tasks[i]
            index = task.get_id(str)
            elp_time_new = max(elapsed_time, task.a) + task.c
            if (pruning is True and
                    (elp_time_new > task.get_absolute_deadline(elp_time_new))):
                return ["X {" + index + "}"]

            subtree = ["(" + index + ", " + str(elp_time_new) + ")"]
            pending = tasks[:i] + tasks[i:]
            pending.remove(task)
            subsubtree = self.get_tree(elp_time_new, pending)
            if (len(subsubtree) == 0):
                subtree[0] += " [Done]"
            else:
                subtree += subsubtree
            tree.append(subtree)

        return tree

    def create(self, pruning=True):
        tree = ["(0, )"]
        tree += self.get_tree(0, self.tasks, pruning)
        self.tree = tree
        return tree

    def plot(self):
        sl.draw_tree(self.tree)


class Spring(Generic):
    def __init__(self, h_exp):
        Generic.__init__(self)
        self.H_coeffs = {"a": 0, "C": 0, "d": 0, "D": 0, "L": 0}
        terms = [term.strip() for term in h_exp.split("+")]
        for term in terms:
            if (len(term) == 1):
                term = "1" + term
            self.H_coeffs[term[-1]] = int(term[:-1])

    def H(self, elapsed_time, task):
        vals = {"a": task.a, "C": task.c, "D": task.d,
                "d": task.get_absolute_deadline(elapsed_time),
                "L": elapsed_time-task.get_absolute_deadline(elapsed_time)}
        H_val = 0
        for param in self.H_coeffs:
            H_val += (self.H_coeffs[param] * vals[param])

        return H_val

    def get_tree(self, elapsed_time, tasks):
        tree = []
        H_vals = []
        elp_times_new = []
        for task in tasks:
            index = task.get_id(str)
            elp_time_new = max(elapsed_time, task.a) + task.c
            H_val = self.H(elp_time_new, task)
            H_vals.append(H_val)
            elp_times_new.append(elp_time_new)
            tree.append(["(" + index + ", " + str(H_val) + ")"])
        if (len(tasks) == 1):
            return tree
        i = np.argmin(H_vals)
        task = tasks[i]
        elp_time_new = elp_times_new[i]
        pending = tasks[:i] + tasks[i:]
        pending.remove(task)
        tree[i][0] += " min"
        subsubtree = self.get_tree(elp_time_new, pending)
        tree[i] += subsubtree
        return tree

    def create(self):
        tree = ["(, )"]
        tree += self.get_tree(0, self.tasks)
        self.tree = tree
        return tree

    def plot(self):
        sl.draw_tree(self.tree)


class LDF(Generic):
    def set_constraints(self, edges):
        self.edges = edges

    def upd_prio_order(self, current_time):
        if (len(self.prio_queue) == 0):
            tasks = {task.get_id(): task for task in self.tasks}
            task_ids = [i for i in tasks]
            task_succ = {}
            for task_id in task_ids:
                task_succ[task_id] = [j for i, j in self.edges if i == task_id]
            while (len(task_ids) != 0):
                ready = []
                for task_id in task_ids:
                    pending = [i for i in task_succ[task_id] if i in task_ids]
                    if (len(pending) == 0):
                        ready.append(task_id)
                j = ready[np.argmax([tasks[i].get_absolute_deadline(tasks[i].a)
                                     for i in ready])]
                self.prio_queue = [tasks[j]] + self.prio_queue
                task_ids.remove(j)

    def full(self, tasks, time, edges, op_path=None):
        self.register_tasks(tasks)
        self.set_constraints(edges)
        self.create(time)
        fig = self.plot(op_path)
        return fig


class EDFStar(Generic):
    def set_constraints(self, edges):
        self.edges = edges

    def modify_releases(self, rel_simplification=False):
        k = int(not rel_simplification)
        tasks = {task.get_id(): task for task in self.tasks}
        task_ids = [i for i in tasks]
        task_pred = {}
        for task_id in task_ids:
            task_pred[task_id] = [i for i, j in self.edges if j == task_id]
        while (len(task_ids) != 0):
            for task_id in task_ids:
                task = tasks[task_id]
                pending = [i for i in task_pred[task_id] if i in task_ids]
                if (len(pending) == 0):
                    task.a = max([task.a] + [(tasks[i].a + k*tasks[i].c)
                                             for i in task_pred[task_id]])
                    task_ids.remove(task_id)
                    break

    def modify_deadlines(self):
        tasks = {task.get_id(): task for task in self.tasks}
        task_ids = [i for i in tasks]
        task_succ = {}
        for task_id in task_ids:
            task_succ[task_id] = [j for i, j in self.edges if i == task_id]
        while (len(task_ids) != 0):
            for task_id in task_ids:
                task = tasks[task_id]
                pending = [i for i in task_succ[task_id] if i in task_ids]
                if (len(pending) == 0):
                    D = min([task.get_absolute_deadline(task.a)] +
                            [(tasks[i].get_absolute_deadline(tasks[i].a) -
                              tasks[i].c) for i in task_succ[task_id]])
                    task.set_absolute_deadline(D)
                    task_ids.remove(task_id)
                    break

    def modify_tasks(self, rel_simplification=False):
        self.modify_releases(rel_simplification)
        self.modify_deadlines()

    def create(self, end_time, rel_simplification=False):
        self.modify_tasks(rel_simplification)
        Generic.create(self, end_time)

    def full(self, tasks, time, edges, rel_simplification=False, op_path=None):
        self.register_tasks(tasks)
        self.set_constraints(edges)
        self.create(time, rel_simplification)
        fig = self.plot(op_path)
        return fig


class Monotonic(Generic):
    def __init__(self, mntc_param):
        Generic.__init__(self)
        self.mntc_param = mntc_param

    def upd_prio_order(self, current_time):
        param = self.mntc_param
        if (len(self.prio_queue) == 0):
            unq = np.unique([getattr(task, param) for task in self.tasks])
            for x in unq:
                srvs = [task for task in self.tasks if
                        ((getattr(task, param) == x) and
                         isinstance(task, tk.Server))]
                prdc = [task for task in self.tasks if
                        ((getattr(task, param) == x) and
                         isinstance(task, tk.Periodic))]
                self.prio_queue += srvs
                self.prio_queue += prdc

    def get_wcrts(self):
        self.upd_prio_order(-1)
        wcrts = {task.get_id(): [task.c] for task in self.prio_queue}
        for i in range(0, len(self.prio_queue)):
            task = self.prio_queue[i]
            Rs = wcrts[task.get_id()]
            while True:
                R = task.c + sum([math.ceil((Rs[-1] + tsk.aj)/tsk.t)*tsk.c
                                  for tsk in self.prio_queue[:i]])
                Rs.append(R)
                if (Rs[-1] == Rs[-2]):
                    break
        return wcrts

    def get_bcrts(self, ret_wcrt=False):
        wcrts = self.get_wcrts()
        bcrts = {i: [wcrts[i][-1]] for i in wcrts}
        for i in range(0, len(self.prio_queue)):
            task = self.prio_queue[i]
            Rs = bcrts[task.get_id()]
            while True:
                R = task.c + sum([(math.ceil((Rs[-1]-tsk.aj)/tsk.t) - 1)*tsk.c
                                  for tsk in self.prio_queue[:i]])
                Rs.append(R)
                if (Rs[-1] == Rs[-2]):
                    break
        if ret_wcrt:
            return {"bc": bcrts, "wc": wcrts}
        else:
            return bcrts

    def get_jitter(self):
        rt = self.get_bcrts(True)
        jit = {"FJ": {}, "RJ": {}}
        for task in self.tasks:
            i = task.get_id()
            jit["RJ"][i] = rt["wc"][i][-1] - rt["bc"][i][-1]
            jit["FJ"][i] = jit["RJ"][i] + task.aj
        return {"jit": jit, "rt": rt}


class RM(Monotonic):
    def __init__(self):
        Monotonic.__init__(self, "t")

    def upd_prio_order(self, current_time):
        Monotonic.upd_prio_order(self, current_time)

        for task in self.tasks:
            if (isinstance(task, tk.Server)):
                task.update_budget(current_time)


class DM(Generic):
    def __init__(self):
        Monotonic.__init__(self, "d")
