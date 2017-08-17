# -*- coding: utf-8 -*-
u"""
Created on 2015-7-27

@author: cheng.li
"""

import unittest
import copy
import tempfile
import pickle
import os
import math
from collections import deque
import numpy as np
import pandas as pd
from scipy.stats import linregress
from PyFin.Math.Accumulators.IAccumulators import Exp
from PyFin.Math.Accumulators.IAccumulators import Log
from PyFin.Math.Accumulators.IAccumulators import Sqrt
from PyFin.Math.Accumulators.IAccumulators import Sign
from PyFin.Math.Accumulators.IAccumulators import Abs
from PyFin.Math.Accumulators.IAccumulators import Pow
from PyFin.Math.Accumulators.IAccumulators import Acos
from PyFin.Math.Accumulators.IAccumulators import Acosh
from PyFin.Math.Accumulators.IAccumulators import Asin
from PyFin.Math.Accumulators.IAccumulators import Asinh
from PyFin.Math.Accumulators.IAccumulators import TruncatedValueHolder
from PyFin.Math.Accumulators.IAccumulators import IIF
from PyFin.Math.Accumulators.IAccumulators import Latest
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAverage
from PyFin.Math.Accumulators.StatefulAccumulators import MovingVariance
from PyFin.Math.Accumulators.StatefulAccumulators import MovingMax
from PyFin.Math.Accumulators.StatefulAccumulators import MovingCorrelation
from PyFin.Math.Accumulators.StatelessAccumulators import Sum
from PyFin.Math.Accumulators.StatelessAccumulators import Average
from PyFin.Math.Accumulators.StatelessAccumulators import Min
from PyFin.Math.Accumulators.StatelessAccumulators import Max
from PyFin.Math.Accumulators.StatelessAccumulators import Correlation
from PyFin.Math.Accumulators.StatefulAccumulators import MovingAlphaBeta


class TestAccumulatorsArithmetic(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.sampleOpen = np.random.randn(10000)
        self.sampleClose = np.random.randn(10000)
        self.sampleRf = np.random.randn(10000)

    def testAddedNanValue(self):
        m = Max(dependency='x')
        m.push({'x': 10.0})
        m.push({'x': np.nan})
        self.assertAlmostEqual(10., m.value)

    def testAccumulatorBasic(self):
        m = Max(dependency='x')
        m.push({'x': 10.0})
        self.assertAlmostEqual(m.result(), m.value)

    def testPlusOperator(self):
        ma5 = MovingAverage(5, 'close')
        ma20 = MovingAverage(20, 'open')
        plusRes = ma5 + ma20

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            ma5.push(data)
            ma20.push(data)
            plusRes.push(data)

            expected = ma5.result() + ma20.result()
            calculated = plusRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testRPlusOperator(self):
        ma5 = MovingAverage(5, 'close')
        ma20 = MovingAverage(20, 'close')
        plusRes = 5.0 + MovingAverage(20, 'close')

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            ma20.push(data)
            plusRes.push(data)
            expected = 5.0 + ma20.result()
            calculated = plusRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testSubOperator(self):
        ma5 = MovingAverage(5, 'close')
        sumTotal = Sum('open')
        subRes = MovingAverage(5, 'close') - Sum('open')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            ma5.push(data)
            sumTotal.push(data)
            subRes.push(data)

            expected = ma5.result() - sumTotal.result()
            calculated = subRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testRSubOperator(self):
        ma20 = MovingAverage(20, 'close')
        sumTotal = Sum('close')
        subRes = 5.0 - MovingAverage(20, 'close')

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma20.push(data)
            sumTotal.push(data)
            subRes.push(data)

            expected = 5.0 - ma20.result()
            calculated = subRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testMultiplyOperator(self):
        mv5 = MovingVariance(5, 'close')
        average = Average('open')
        mulRes = MovingVariance(5, 'close') * Average('open')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            mv5.push(data)
            average.push(data)
            mulRes.push(data)

            if i >= 1:
                expected = mv5.result() * average.result()
                calculated = mulRes.result()
                self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                                 "expected:   {1:f}\n"
                                                                 "calculated: {2:f}".format(i, expected, calculated))

    def testRMultiplyOperator(self):
        ma20 = MovingAverage(20, 'close')
        average = Average('open')
        mulRes = 5.0 * MovingAverage(20, 'close')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            average.push(data)
            ma20.push(data)
            mulRes.push(data)

            expected = 5.0 * ma20.result()
            calculated = mulRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testDivOperator(self):
        mc5 = MovingCorrelation(5, ['open', 'close'])
        minum = Min('open')
        divRes = Min('open') / MovingCorrelation(5, ['open', 'close'])

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            mc5.push(data)
            minum.push(data)
            divRes.push(data)

            if i >= 1:
                expected = minum.result() / mc5.result()
                calculated = divRes.result()
                self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                                 "expected:   {1:f}\n"
                                                                 "calculated: {2:f}".format(i, expected, calculated))

    def testRDivOperator(self):
        ma20 = MovingAverage(20, 'close')
        divRes = 5.0 / MovingAverage(20, 'close')

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma20.push(data)
            divRes.push(data)

            expected = 5.0 / ma20.result()
            calculated = divRes.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testMultipleOperators(self):
        ma20 = MovingAverage(20, 'close')
        ma120 = MovingAverage(120, 'close')
        mmax = MovingMax(50, 'open')
        res = (MovingAverage(20, 'close') - MovingAverage(120, 'close')) / MovingMax(50, 'open')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            ma20.push(data)
            ma120.push(data)
            mmax.push(data)
            res.push(data)

            expected = (ma20.result() - ma120.result()) / mmax.result()
            calculated = res.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testNegativeOperator(self):
        ma20 = MovingAverage(20, 'close')
        negma20 = -ma20
        negma20square = -(ma20 ^ ma20)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma20.push(data)
            negma20.push(data)
            negma20square.push(data)

            expected = -ma20.result()
            calculated = negma20.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            calculated = negma20square.result()
            for cal in calculated:
                self.assertAlmostEqual(cal, expected, 12, "at index {0:d}\n"
                                                          "expected:   {1:f}\n"
                                                          "calculated: {2:f}".format(i, expected, cal))

    def testListedOperator(self):
        ma20 = MovingAverage(20, 'close')
        maxer = Max('open')
        minimumer = Min('close')
        listHolder = MovingAverage(20, 'close') ^ Max('open') ^ Min('close')
        listHolder2 = 2.0 ^ MovingAverage(20, 'close')
        listHolder3 = MovingAverage(20, 'close') ^ 2.0

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            ma20.push(data)
            maxer.push(data)
            minimumer.push(data)
            listHolder.push(data)
            listHolder2.push(data)
            listHolder3.push(data)

            expected = (ma20.result(), maxer.result(), minimumer.result())
            calculated = listHolder.result()
            for ev, cv in zip(expected, calculated):
                self.assertAlmostEqual(ev, cv, 12, "at index {0:d}\n"
                                                   "expected:   {1}\n"
                                                   "calculated: {2}".format(i, expected, calculated))

            expected = (2.0, ma20.result())
            calculated = listHolder2.result()
            for ev, cv in zip(expected, calculated):
                self.assertAlmostEqual(ev, cv, 12, "at index {0:d}\n"
                                                   "expected:   {1}\n"
                                                   "calculated: {2}".format(i, expected, calculated))

            expected = (ma20.result(), 2.0)
            calculated = listHolder3.result()
            for ev, cv in zip(expected, calculated):
                self.assertAlmostEqual(ev, cv, 12, "at index {0:d}\n"
                                                   "expected:   {1}\n"
                                                   "calculated: {2}".format(i, expected, calculated))

    def testCompoundedOperator(self):
        ma5 = MovingAverage(5, 'x')
        maxer = Max('close')
        max5ma = Max('close') >> MovingAverage(5)
        max5ma2 = MovingAverage(5, Max('close'))
        average = Average('close')
        sumM = Sum('close')
        mvTest = Correlation(dependency=('x', 'y'))
        mvCorr = (Average('close') ^ Sum('close')) >> Correlation(dependency=('x', 'y'))

        for i, close in enumerate(self.sampleClose):
            data = {'close': close, 'open': 1.}
            maxer.push(data)
            data2 = {'x': maxer.result()}
            ma5.push(data2)
            max5ma.push(data)
            max5ma2.push(data)
            average.push(data)
            sumM.push(data)
            data3 = {'x': average.result(), 'y': sumM.result()}
            mvTest.push(data3)
            mvCorr.push(data)

            expected = ma5.result()
            calculated = max5ma.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            calculated = max5ma2.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            if i >= 1:
                expected = mvTest.result()
                calculated = mvCorr.result()
                self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                                 "expected:   {1:f}\n"
                                                                 "calculated: {2:f}".format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = Max('close') >> math.sqrt

        with self.assertRaises(ValueError):
            _ = (Max('close') ^ Min('close')) >> MovingCorrelation(20, dependency=('x', 'y', 'z'))

        (Max('close') ^ Min('close')) >> MovingCorrelation(20, dependency=('x', 'y'))

    def testListedAndCompoundedOperator(self):
        maClose = MovingAverage(20, 'close')
        maOpen = MovingAverage(10, 'open')
        maRf = MovingAverage(10, 'rf')
        listHolder = MovingAverage(20, 'close') ^ MovingAverage(10, 'open') ^ MovingAverage(10, 'rf')
        mc = MovingAlphaBeta(20, listHolder)

        maCloseContainer = deque(maxlen=20)
        maOpenContainer = deque(maxlen=20)

        for i, (open, close, rf) in enumerate(zip(self.sampleOpen, self.sampleClose, self.sampleRf)):
            data = {'close': close, 'open': open, 'rf': rf}
            maClose.push(data)
            maOpen.push(data)
            maRf.push(data)
            mc.push(data)
            maCloseContainer.append(maClose.result() - maRf.result())
            maOpenContainer.append(maOpen.result() - maRf.result())

            if i >= 2:
                expected = linregress(maOpenContainer, maCloseContainer)
                calculated = mc.result()

                # check alpha
                self.assertAlmostEqual(expected[1], calculated[0], 10, "at index {0:d}\n"
                                                                       "expected alpha:   {1:f}\n"
                                                                       "calculated alpha: {2:f}".format(i, expected[1],
                                                                                                        calculated[0]))

                # check beta
                self.assertAlmostEqual(expected[0], calculated[1], 10, "at index {0:d}\n"
                                                                       "expected beta:   {1:f}\n"
                                                                       "calculated beta: {2:f}".format(i, expected[0],
                                                                                                       calculated[1]))

    def testTruncatedValueHolder(self):
        ma20 = MovingAverage(20, 'close')
        max5 = MovingMax(5, 'open')

        with self.assertRaises(TypeError):
            _ = TruncatedValueHolder(ma20, 1)

        test = TruncatedValueHolder(ma20 ^ max5, 1)
        test.push(dict(close=10.0, open=5.0))
        test.push(dict(close=10.0, open=20.0))
        self.assertAlmostEqual(test.result(), 20.0, 15)

        test = TruncatedValueHolder(ma20 ^ max5, 0)
        test.push(dict(close=10.0, open=5.0))
        test.push(dict(close=15.0, open=20.0))
        self.assertAlmostEqual(test.result(), 12.50, 15)

        test = TruncatedValueHolder(ma20 ^ max5, slice(1, 2))
        test.push(dict(close=10.0, open=5.0))
        test.push(dict(close=15.0, open=20.0))
        self.assertAlmostEqual(test.result(), [20.0], 15)

        test = TruncatedValueHolder(ma20 ^ max5, slice(0, -1))
        test.push(dict(close=10.0, open=5.0))
        test.push(dict(close=15.0, open=20.0))
        self.assertAlmostEqual(test.result(), [12.5], 15)

        with self.assertRaises(ValueError):
            _ = TruncatedValueHolder(ma20 ^ max5, slice(1, -2))

    def testGetItemOperator(self):
        listHolder = MovingAverage(20, 'close') ^ Max('open') ^ Min('close')
        listHolder1 = listHolder[1]
        listHolder2 = listHolder[1:3]
        maxer = Max('open')

        for i, (open, close) in enumerate(zip(self.sampleOpen, self.sampleClose)):
            data = {'close': close, 'open': open}
            listHolder1.push(data)
            listHolder2.push(data)
            maxer.push(data)

            expected = maxer.result()
            calculated = listHolder1.result()
            self.assertAlmostEqual(expected, calculated, 12, "at index {0:d}\n"
                                                             "expected beta:   {1:f}\n"
                                                             "calculated beta: {2:f}".format(i, expected, calculated))

            calculated = listHolder2.result()[0]
            self.assertAlmostEqual(expected, calculated, 12, "at index {0:d}\n"
                                                             "expected beta:   {1:f}\n"
                                                             "calculated beta: {2:f}".format(i, expected, calculated))

    def testLessOrEqualOperators(self):
        m1 = Max('x')
        m2 = Min('x')
        cmp = m1 <= m2

        cmp.push(dict(x=1.0))
        self.assertEqual(True, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(False, cmp.result())

    def testLessOperator(self):
        m1 = Min('x')
        m2 = Max('x')
        cmp = m1 < m2

        cmp.push(dict(x=1.0))
        self.assertEqual(False, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(True, cmp.result())

    def testGreaterOrEqualOperator(self):
        m1 = Min('x')
        m2 = Max('x')
        cmp = m1 >= m2

        cmp.push(dict(x=1.0))
        self.assertEqual(True, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(False, cmp.result())

    def testGreaterOperator(self):
        m1 = Max('x')
        m2 = Min('x')
        cmp = m1 > m2

        cmp.push(dict(x=1.0))
        self.assertEqual(False, cmp.result())
        cmp.push(dict(x=2.0))
        self.assertEqual(True, cmp.result())

    def testExpFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Exp(MovingAverage(5, 'close'))
        holder2 = MovingAverage(5, 'close') >> Exp

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)
            holder2.push(data)

            expected = math.exp(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

            calculated = holder2.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testLogFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Log(ma5)
        sampleClose = np.exp(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.log(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testSignFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Sign(ma5)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = 1 if ma5.result() >= 0 else -1
            calculated = holder.result()

            self.assertEqual(calculated, expected, "at index {0:d}\n"
                                                   "expected:   {1:f}\n"
                                                   "calculated: {2:f}".format(i, expected, calculated))

    def testSqrtFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Sqrt(ma5)

        sampleClose = np.square(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.sqrt(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testAbsFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Abs(ma5)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = abs(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testPowFunction(self):
        ma5min = MovingAverage(5, 'close') >> Min
        holder = Pow(ma5min, 3)

        for i, close in enumerate(self.sampleClose):
            data = {'close': close}
            ma5min.push(data)
            holder.push(data)

            expected = math.pow(ma5min.result(), 3)
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testAcosFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Acos(ma5)

        sampleClose = np.cos(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.acos(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testAcoshFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Acosh(ma5)

        sampleClose = np.cosh(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.acosh(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testAsinFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Asin(ma5)

        sampleClose = np.sin(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.asin(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testAsinhFunction(self):
        ma5 = MovingAverage(5, 'close')
        holder = Asinh(ma5)

        sampleClose = np.sinh(self.sampleClose)

        for i, close in enumerate(sampleClose):
            data = {'close': close}
            ma5.push(data)
            holder.push(data)

            expected = math.asinh(ma5.result())
            calculated = holder.result()
            self.assertAlmostEqual(calculated, expected, 12, "at index {0:d}\n"
                                                             "expected:   {1:f}\n"
                                                             "calculated: {2:f}".format(i, expected, calculated))

    def testArithmeticFunctionsDeepcopy(self):
        data = {'x': 1}

        test = Exp('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.exp(data['x']), copied.value)

        test = Log('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.log(data['x']), copied.value)

        test = Sqrt('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.sqrt(data['x']), copied.value)

        data['x'] = -1.

        test = Pow('x', 2)
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(data['x'] ** 2, copied.value)

        test = Abs('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(abs(data['x']), copied.value)

        test = Sign('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(-1., copied.value)

        data['x'] = 1.

        test = Acos('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.acos(data['x']), copied.value)

        test = Asin('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.asin(data['x']), copied.value)

        test = Acosh('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.acosh(data['x']), copied.value)

        test = Asinh('x')
        test.push(data)
        copied = copy.deepcopy(test)
        self.assertAlmostEqual(math.asinh(data['x']), copied.value)

    def testArithmeticFunctionsPickle(self):
        data = {'x': 1}

        test = Exp('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Log('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Sqrt('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        data['x'] = -1.

        test = Pow('x', 2)
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Abs('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Sign('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        data['x'] = 1.

        test = Acos('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Asin('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Acosh('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

        test = Asinh('x')
        test.push(data)
        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(test, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            self.assertAlmostEqual(test.value, pickled.value)
        os.unlink(f.name)

    def testAccumulatorTransform(self):
        window = 5
        ma5 = MovingAverage(window, 'close')
        df = pd.DataFrame(self.sampleClose, columns=['close'])
        res = ma5.transform(df, name='my_factor')[window-1:]
        expected = df.rolling(window).mean()[window - 1:]['close']

        self.assertEqual(res.name, 'my_factor')
        np.testing.assert_array_almost_equal(res, expected)

    def testIIFAccumulator(self):
        iif = IIF(Latest('rf') > 0, 'close', 'open')

        for i, close in enumerate(self.sampleClose):
            data = {'close': close,
                    'open': self.sampleOpen[i],
                    'rf': self.sampleRf[i]}

            iif.push(data)

            if data['rf'] > 0:
                self.assertAlmostEqual(iif.result(), data['close'])
            else:
                self.assertAlmostEqual(iif.result(), data['open'])