# -*- coding: utf-8 -*-
u"""
Created on 2015-10-22

@author: cheng.li
"""

import copy
from PyFin.Analysis.SecurityValueHolders import SecurityValueHolder
from PyFin.Math.Accumulators import Latest
from PyFin.Math.Accumulators import XAverage
from PyFin.Math.Accumulators import MACD
from PyFin.Math.Accumulators import Exp
from PyFin.Math.Accumulators import Log
from PyFin.Math.Accumulators import Pow
from PyFin.Math.Accumulators import Sqrt
from PyFin.Math.Accumulators import Abs
from PyFin.Math.Accumulators import Acos
from PyFin.Math.Accumulators import Acosh
from PyFin.Math.Accumulators import Asin
from PyFin.Math.Accumulators import Asinh
from PyFin.Math.Accumulators import Diff
from PyFin.Math.Accumulators import SimpleReturn
from PyFin.Math.Accumulators import LogReturn


class SecurityStatelessSingleValueHolder(SecurityValueHolder):
    def __init__(self, holderType, dependency='x', symbolList=None, **kwargs):
        super(SecurityStatelessSingleValueHolder, self).__init__(dependency, symbolList)

        if isinstance(dependency, SecurityValueHolder):
            self._symbolList = dependency.symbolList
            self._dependency = dependency._dependency
            self._innerHolders = \
                {
                    name: holderType(dependency=copy.deepcopy(dependency.holders[name]), **kwargs) for name in self._symbolList
                    }

        else:
            self._innerHolders = \
                {
                    name: holderType(dependency=self._dependency, **kwargs) for name in self._symbolList
                    }


class SecurityLatestValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityLatestValueHolder, self).__init__(holderType=Latest,
                                                        dependency=dependency,
                                                        symbolList=symbolList)


class SecurityXAverageValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, window, dependency='x', symbolList=None):
        super(SecurityXAverageValueHolder, self).__init__(holderType=XAverage,
                                                          dependency=dependency,
                                                          symbolList=symbolList,
                                                          window=window)


class SecurityMACDValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, short, long, dependency='x', symbolList=None):
        super(SecurityMACDValueHolder, self).__init__(holderType=MACD,
                                                      dependency=dependency,
                                                      symbolList=symbolList,
                                                      short=short,
                                                      long=long)


class SecurityExpValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityExpValueHolder, self).__init__(holderType=Exp,
                                                      dependency=dependency,
                                                      symbolList=symbolList)


class SecurityLogValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityLogValueHolder, self).__init__(holderType=Log,
                                                      dependency=dependency,
                                                      symbolList=symbolList)


class SecurityPowValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityPowValueHolder, self).__init__(holderType=Pow,
                                                      dependency=dependency,
                                                      symbolList=symbolList)


class SecuritySqrtValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecuritySqrtValueHolder, self).__init__(holderType=Sqrt,
                                                      dependency=dependency,
                                                      symbolList=symbolList)


class SecurityAbsValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityAbsValueHolder, self).__init__(holderType=Abs,
                                                      dependency=dependency,
                                                      symbolList=symbolList)


class SecurityAcosValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityAcosValueHolder, self).__init__(holderType=Acos,
                                                      dependency=dependency,
                                                      symbolList=symbolList)


class SecurityAcoshValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityAcoshValueHolder, self).__init__(holderType=Acosh,
                                                      dependency=dependency,
                                                      symbolList=symbolList)


class SecurityAsinValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityAsinValueHolder, self).__init__(holderType=Asin,
                                                      dependency=dependency,
                                                      symbolList=symbolList)


class SecurityAsinhValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityAsinhValueHolder, self).__init__(holderType=Asinh,
                                                      dependency=dependency,
                                                      symbolList=symbolList)


class SecurityDiffValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityDiffValueHolder, self).__init__(holderType=Diff,
                                                      dependency=dependency,
                                                      symbolList=symbolList)


class SecuritySimpleReturnValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecuritySimpleReturnValueHolder, self).__init__(holderType=SimpleReturn,
                                                              dependency=dependency,
                                                              symbolList=symbolList)


class SecurityLogReturnValueHolder(SecurityStatelessSingleValueHolder):
    def __init__(self, dependency='x', symbolList=None):
        super(SecurityLogReturnValueHolder, self).__init__(holderType=LogReturn,
                                                           dependency=dependency,
                                                           symbolList=symbolList)
