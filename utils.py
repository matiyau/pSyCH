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
