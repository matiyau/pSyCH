#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 19:56:36 2021

@author: n7
"""

import numpy as np


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
