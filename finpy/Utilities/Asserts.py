# -*- coding: utf-8 -*-
u"""
Created on 2015-8-17

@author: cheng.li
"""


def fpAssert(condition, exception, msg=""):
    if not condition:
        raise exception(msg)