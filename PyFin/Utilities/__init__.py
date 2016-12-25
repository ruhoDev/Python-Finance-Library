# -*- coding: utf-8 -*-
u"""
Created on 2015-8-17

@author: cheng.li
"""

import time
from PyFin.Utilities.Asserts import pyFinAssert
from PyFin.Utilities.Asserts import isClose

__all__ = ['pyFinAssert',
           'isClose']


def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        return t2 - t1, res
    return wrapper


def check_date(date):
    from PyFin.DateUtilities import Date
    if isinstance(date, str):
        return Date.strptime(date, dateFormat='%Y-%m-%d')
    else:
        return Date.fromDateTime(date)


def to_dict(raw_data):
    category = raw_data.index
    values = raw_data.values
    columns = raw_data.columns

    inner_values = [dict(zip(columns, values[i])) for i in range(len(values))]
    dict_values = dict(zip(category, inner_values))
    return dict_values, category