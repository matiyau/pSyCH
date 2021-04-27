#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 13:01:25 2021

@author: n7
"""

import math
from . import utils as ut

def rm_prdc_sched(tasks):
    params = {}
    U = ut.get_total_u(tasks)
    params["U"] = U
    if (U > 1):
        sched = -1 # Definitely not schedulable
    else:
        HB = ut.get_P(tasks)
        params["HB"] = HB
        params["LL"] = U
        if (HB <= 2):
            sched = 1 # Definitely schedulable
        else:
            sched = 0 # Might be schedulable
    return sched, params


def dm_prdc_sched(tasks):
    sched = True
    params = {}
    params["R"] = {}
    for task in tasks:
        index = task.get_id()
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
