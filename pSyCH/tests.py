#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 13:01:25 2021

@author: n7
"""

import math
from . import utils as ut


def rm_prdc_sched(tasks):
    """
    Check schedulability of the given periodic tasks under RM scheduling.

    Parameters
    ----------
    tasks : list of pSyCH.tasks.Periodic
        Task set whose schedulability is to be checked.

    Returns
    -------
    sched : int
        |br|
        If -1, the task set is definitely not schedulable (U > 1).
        |br|
        If 0, the task set might be schedulable (U <= 1 and HB > 2).
        |br|
        If 1, the task set is definitely schedulable (HB <= 2).
    params : dict
        The dictionary includes the following key-value pairs:
        |br|
        "U" - Total utilization of all tasks.
        |br|
        "HB" - HB product value.
        |br|
        "LL" - LL sum value.

    """
    params = {}
    U = ut.get_total_u(tasks)
    params["U"] = U
    if (U > 1):
        sched = -1  # Definitely not schedulable
    else:
        HB = ut.get_P(tasks)
        params["HB"] = HB
        params["LL"] = U
        if (HB <= 2):
            sched = 1  # Definitely schedulable
        else:
            sched = 0  # Might be schedulable
    return sched, params


def dm_prdc_sched(tasks):
    """
    Check schedulability of the given periodic tasks under DM scheduling.

    Parameters
    ----------
    tasks : list of pSyCH.tasks.Periodic
        Task set whose schedulability is to be checked.

    Returns
    -------
    sched : bool
        True if the task set is schedulable, False otherwise.
    params : dict
        The dictionary includes the following key-value pairs:
        |br|
        "U" - Total utilization of all tasks.
        |br|
        "R" - Dictionary containing the task IDs as the keys and the list of
        outputs of each step from the fixed-point iteration, as the values.

    """
    sched = True
    params = {}
    params["R"] = {}
    U = ut.get_total_u(tasks)
    params["U"] = U
    for index in range(1, len(tasks)+1):
        task = tasks[index-1]
        Rs = [task.c]
        while True:
            i = 0
            for tsk in tasks:
                if (tsk.d < task.d):
                    i += (math.ceil(Rs[-1]/tsk.t) * tsk.c)
            R = task.c + i
            Rs.append(R)
            if (R == Rs[-2]):
                break
        params["R"][index] = Rs
        if (Rs[-1] > task.d):
            sched = False
            break
    return sched, params


def edf_prdc_sched(tasks):
    """
    Check schedulability of the given periodic tasks under EDF scheduling.

    Parameters
    ----------
    tasks : list of pSyCH.tasks.Periodic
        Task set whose schedulability is to be checked.

    Returns
    -------
    sched : bool
        True if the task set is schedulable, False otherwise.
    params : dict
        The dictionary includes the following key-value pairs:
        |br|
        "U" - Total utilization of all tasks.
        |br|
        "L*" - L* value for the task set.
        |br|
        "H" - Hyperperiod of the task set.
        |br|
        "D_max" - Maximum relative deadline among the tasks.
        |br|
        "L" - L value computed from "H", "D_max" and "L*"
        |br|
        "g" - Dictionary with the time coordinate, t, as the key and the
        g-value, g(0, t) as the value.

    """
    eq = True  # D=T condition
    sched = False
    params = {}
    for task in tasks:
        if (task.d != task.t):
            eq = False
            break
    U = ut.get_total_u(tasks)
    params["U"] = U
    L_star = ut.get_L_star(tasks)
    H = ut.get_hyperperiod(tasks)
    D_max = ut.get_d_max(tasks)
    L = min(H, max(D_max, L_star))
    ds = ut.get_ds(tasks, L)
    params["L*"] = L_star
    params["H"] = H
    params["D_max"] = D_max
    params["L"] = L
    if (U > 1):
        sched = False
    elif eq:
        sched = True
    else:
        sched = True
        g_vals = {}
        for d in ds:
            g = ut.get_g_val(tasks, d)
            g_vals[d] = g
            if (g > d):
                sched = False
                break
        params["g"] = g_vals
    return eq, sched, params


def ps_dim(tasks):
    """
    Dimension a Polling Server such that it fits into the provided task set.

    Parameters
    ----------
    tasks : list of pSyCH.tasks.Periodic
        Task set whose schedulability is to be checked.

    Returns
    -------
    sched : bool
        True if the task set is schedulable, False otherwise.
    params : dict
        The dictionary includes the following key-value pairs:
        |br|
        "P" - HB product.
        |br|
        "T" - Suggested budget replenishment period for the server.
        |br|
        "C" - Suggested max budget for the server.

    """
    params = {}
    P = ut.get_P(tasks)
    params["P"] = P
    U_max = round((2 - P)/P, 3)
    if (U_max < 0):
        return False, params
    T = min([task.t for task in tasks])
    C = round(U_max * T, 3)
    params["T"] = T
    params["C"] = C
    return True, params


def ds_dim(tasks):
    """
    Dimension a Deferable Server such that it fits into the provided task set.

    Parameters
    ----------
    tasks : list of pSyCH.tasks.Periodic
        Task set whose schedulability is to be checked.

    Returns
    -------
    sched : bool
        True if the task set is schedulable, False otherwise.
    params : dict
        The dictionary includes the following key-value pairs:
        |br|
        "P" - HB product.
        |br|
        "T" - Suggested budget replenishment period for the server.
        |br|
        "C" - Suggested max budget for the server.

    """
    params = {}
    P = ut.get_P(tasks)
    params["P"] = P
    U_max = round((2 - P)/(2*P - 1), 3)
    if (U_max < 0):
        return False, params
    T = min([task.t for task in tasks])
    C = U_max * T
    params["T"] = T
    params["C"] = C
    return True, params
