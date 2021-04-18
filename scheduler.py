#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 08:08:44 2021

@author: n7
"""

from . import task as tk
import bisect as bs
from copy import deepcopy as dc
import numpy as np


class Generic():
    def __init__(self):
        self.tasks = []
        self.crit_tms = [0]
        self.prio_queue = []
        self.end_time = 0

    def register_task(self, task):
        self.tasks.append(task)

    def upd_prio_order(self, current_time):
        self.prio_queue = [task for task in self.tasks]

    def create(self, end_time):
        self.end_time = end_time
        for task in self.tasks:
            task.reset()
        self.crit_tms = [0]
        while True:
            current_time = self.crit_tms[0]
            if (current_time >= self.end_time):
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
            self.prio_queue += srvs
            self.prio_queue += prdc


class Bratley(Generic):
    def get_tree(self, elapsed_time, tasks, pruning=True):
        tree = []
        for i in range(0, len(tasks)):
            task = tasks[i]
            index = task.name.split(" ")[1]
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
            index = task.name.split(" ")[1]
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


    def create(self, pruning=True):
        tree = ["(, )"]
        tree += self.get_tree(0, self.tasks)
        # sl.draw_tree(tree, pruning)
        return tree


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
