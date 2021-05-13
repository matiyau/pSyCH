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
    """
    Compute the GCD for a list of float values.

    Parameters
    ----------
    flts : list of float
        Floats whose GCD is to be computed.

    Returns
    -------
    float
        GCD of the given floats.

    """
    max_ds = [10**len(str(float(flt)).split(".")[1]) for flt in flts]
    fracs = [Fraction(flts[i]).limit_denominator(max_ds[i])
             for i in range(0, len(flts))]
    n_gcd = np.gcd.reduce([frac.numerator for frac in fracs])
    d_lcm = np.lcm.reduce([frac.denominator for frac in fracs])
    return n_gcd/d_lcm


def filter_sequence(seq):
    """
    Filter a sequence of timeline coordinates and their corresponding y-values
    byt removing redundant coordinates and retaining only critical points
    (points where the slope changes).

    Parameters
    ----------
    seq : numpy.ndarray
        2D array containing timeline coordinates and their corresponding
        y-values.

    Returns
    -------
    numpy.ndarray
        Filtered sequence of coordinates.

    """
    brk_pts = np.where(seq[1][:-1] != seq[1][1:])[0]
    if (brk_pts.size == 0):
        return seq
    brk_pts = np.unique(np.concatenate([[0], brk_pts, brk_pts+1,
                                        [seq[1].size-1]]))
    return seq[:, brk_pts]


def arrow(ax, x, clr, down=True, major=True):
    """
    Plot an arrow on the given Axes object

    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        Axes object on which the arrow needs to be plotted.
    x : float
        X-coordinate for the arrow.
    clr : color format supported by matplotlib
        Color for the arrow.
    down : bool, optional
        If True, arrow head is downwards. Otherwise, arrow points upwards.
        The default is True.
    major : bool, optional
        If True, a major arrow (solid stroke, greater alpha, greater height)
        is drawn. Otherwise, a minor arrow (dotted stroke, smaller alpha,
        smaller height) is drawn. The default is True.

    Returns
    -------
    None.

    """
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
    """
    Get the maximum relative deadline among the given periodic tasks.

    Parameters
    ----------
    tasks : list of pSyCH.task.Periodic
        Periodic tasks among which the maximum relative deadline needs to be
        computed.

    Returns
    -------
    float
        Maximum relative deadline among for the give tasks.

    """
    return max([task.d for task in tasks])


def get_hyperperiod(tasks):
    """
    Get the hyperperiodic for the given periodic task set.

    Parameters
    ----------
    tasks : list of pSyCH.task.Periodic
        Set of periodic tasks, for which the HB product needs to be computed.

    Returns
    -------
    float
        HB product for the task set.

    """
    return np.lcm.reduce([task.t for task in tasks])


def get_L_star(tasks):
    """
    Get the L* value for the given periodic task set.

    Parameters
    ----------
    tasks : list of pSyCH.task.Periodic
        Set of periodic tasks, for which the L* value needs to be computed.

    Returns
    -------
    float
        L* value for the task set.

    """
    L = 0
    U = 0
    for task in tasks:
        u = task.c/task.t
        L += (task.t - task.d)*u
        U += u
    L /= (1-U)
    return round(L, 3)


def get_total_u(tasks):
    """
    Get the total utilization for the given periodic task set.

    Parameters
    ----------
    tasks : list of pSyCH.task.Periodic
        Set of periodic tasks, for which the utilization needs to be computed.

    Returns
    -------
    float
        Total utilization of the task set.

    """
    U = 0
    for task in tasks:
        U += (task.c/task.t)
    return round(U, 3)


def get_ds(tasks, lim):
    """
    Get all absolute deadlines for the given periodic task set, upto the
    specified time limit. Deadlines for every instance of each periodic task
    will be considered.

    Parameters
    ----------
    tasks : list of pSyCH.task.Periodic
        Set of periodic tasks, for which the absolute deadlines need to be
        extracted.
    lim : float
        Time limit until which the deadlines need to be extracted.

    Returns
    -------
    float
        All absolute deadlines till the specified time limit.

    """
    ds = []
    for task in tasks:
        ds += list(np.arange(task.d + task.p, lim+1, task.t))
    return np.unique(ds)


def get_g_val(tasks, L):
    """
    Get the g-value product for the given periodic task set.

    Parameters
    ----------
    tasks : list of pSyCH.task.Periodic
        Set of periodic tasks, for which the g-value needs to be computed.
    L : float
        End time limit for computing the g-value

    Returns
    -------
    float
        g-value for the task set.

    """
    g_val = 0
    for task in tasks:
        g_val += (math.floor((L + task.t - task.d)/task.t)*task.c)
    return g_val


def get_P(tasks):
    """
    Get the HB product for the given periodic task set.

    Parameters
    ----------
    tasks : list of pSyCH.task.Periodic
        Set of periodic tasks, for which the HB product needs to be computed.

    Returns
    -------
    float
        HB product for the task set.

    """
    P = 1
    for task in tasks:
        P *= (1 + task.c/task.t)
    return round(P, 3)
