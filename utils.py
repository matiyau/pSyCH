#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 19:56:36 2021

@author: n7
"""

from fractions import Fraction
import math
import numpy as np


def flt_gcd(flts):
    max_ds = [10**len(str(float(flt)).split(".")[1]) for flt in flts]
    fracs = [Fraction(flts[i]).limit_denominator(max_ds[i])
             for i in range(0, len(flts))]
    n_gcd = np.gcd.reduce([frac.numerator for frac in fracs])
    d_lcm = np.lcm.reduce([frac.denominator for frac in fracs])
    return n_gcd/d_lcm

def filter_sequence(seq):
    brk_pts = np.where(seq[1][:-1] != seq[1][1:])[0]
    brk_pts = np.unique(np.concatenate([[0], brk_pts, brk_pts+1,
                                        [seq[1].size-1]]))
    return seq[:, brk_pts]


def arrow(ax, x, clr, down=True, major=True):
    styles = ["dotted", "solid"]
    alphas = [0.8, 1]
    mj = int(major)
    dn = int(down)
    y = dn * (1.3 + 0.4*mj)
    dy = -2*(dn-0.5)*(0.9 + 0.4*mj)
    width = 0.08 + 0.04*mj
    ax.arrow(x, y, 0, dy, width=width, head_width=0.45, head_length=0.4,
             color=clr, ls=styles[mj], alpha=alphas[mj])


def get_d_max(tasks):
    return max([task.d for task in tasks])


def get_hyperperiod(tasks):
    return np.lcm.reduce([task.t for task in tasks])

def get_L_star(tasks):
    L = 0
    U = 0
    for task in tasks:
        u = task.c/task.t
        L += (task.t - task.d)*u
        U += u
    L /= (1-U)
    return round(L, 3)


def get_total_u(tasks):
    U = 0
    for task in tasks:
        U += (task.c/task.t)
    return round(U, 3)


def get_ds(tasks, lim):
    ds = []
    for task in tasks:
        ds += list(np.arange(task.d, lim+1, task.t))
    return np.unique(ds)


def get_g_val(tasks, L):
    g_val = 0
    for task in tasks:
        g_val += (math.floor((L + task.t - task.d)/task.t)*task.c)
    return g_val


def get_P(tasks):
    P = 1
    for task in tasks:
        P *= (1 + task.c/task.t)
    return round(P, 3)
