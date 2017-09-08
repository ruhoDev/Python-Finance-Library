# -*- coding: utf-8 -*-
u"""
Created on 2015-8-11

@author: cheng.li
"""

import unittest
import math
import numpy as np
import copy
import pickle
import tempfile
import os
from collections import deque
from PyFin.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingVariance
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingStandardDeviation
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMax
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingMin
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingQuantile
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAllTrue
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingAnyTrue
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingSum
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingCountedPositive
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingPositiveAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingPositiveDifferenceAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingNegativeDifferenceAverage
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingRSI
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingLogReturn
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingResidue
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingRank
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingCorrelation
from PyFin.Analysis.TechnicalAnalysis import SecurityMovingHistoricalWindow


class TestStatefulTechnicalAnalysis(unittest.TestCase):
    def setUp(self):
        # preparing market data
        np.random.seed(0)
        aaplClose = np.random.randn(1000)
        aaplOpen = np.random.randn(1000)
        self.aapl = {'close': aaplClose, 'open': aaplOpen}

        ibmClose = np.random.randn(1000)
        ibmOpen = np.random.randn(1000)
        self.ibm = {'close': ibmClose, 'open': ibmOpen}
        self.dataSet = {'aapl': self.aapl, 'ibm': self.ibm}

    def template_test_deepcopy(self, class_type, **kwargs):
        ma = class_type(**kwargs)

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        copied = copy.deepcopy(ma)

        for name in ma.value.index():
            self.assertAlmostEqual(ma.value[name], copied.value[name])

        for v in np.random.rand(20):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)
            copied.push(data)

            for name in ma.value.index():
                self.assertAlmostEqual(ma.value[name], copied.value[name])

    def template_test_pickle(self, class_type, **kwargs):
        ma = class_type(**kwargs)

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(ma, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            for name in ma.value.index():
                self.assertAlmostEqual(ma.value[name], pickled.value[name])
        os.unlink(f.name)

        for v in np.random.rand(20):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)
            pickled.push(data)

            for name in ma.value.index():
                self.assertAlmostEqual(ma.value[name], pickled.value[name])

    def testSecurityMovingAverage(self):
        window = 10
        ma1 = SecurityMovingAverage(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = np.mean(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingAverage(window, ['close', 'open'])

    def testSecurityMovingAverageWithErrorValues(self):
        window = 5
        to_average = SecurityLatestValueHolder('open') / SecurityLatestValueHolder('close')
        ma = SecurityMovingAverage(window, to_average)

        container = {'aapl': deque(maxlen=window), 'ibm': deque(maxlen=window)}

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=1.0 if self.aapl['close'][i] >= 1.0 else 0.,
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))

            ma.push(data)

            for name in data:
                res = data[name]['open'] / data[name]['close']
                if res != np.inf and res != -np.inf and not math.isnan(res):
                    container[name].append(res)

            value = ma.value

            for name in value.index():
                expected = np.mean(container[name])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingAverageDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingAverage, window=10, dependency=['x'])

    def testSecurityMovingAveragePickle(self):
        self.template_test_pickle(SecurityMovingAverage, window=10, dependency=['x'])

    def testSecurityMovingVariance(self):
        window = 10
        var = SecurityMovingVariance(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))

            var.push(data)

            if i <= 1:
                continue

            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = var.value
            for name in value.index():
                expected = np.var(self.dataSet[name]['close'][start:(i + 1)]) * (i + 1. - start) / (i - start)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))
        with self.assertRaises(ValueError):
            _ = SecurityMovingVariance(window, ['close', 'open'])

    def testSecurityMovingVarianceDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingVariance, window=10, dependency=['x'])

    def testSecurityMovingVariancePickle(self):
        self.template_test_pickle(SecurityMovingVariance, window=10, dependency=['x'])

    def testSecurityMovingStandardDeviation(self):
        window = 10
        std = SecurityMovingStandardDeviation(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))

            std.push(data)

            if i <= 1:
                continue

            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = std.value
            for name in value.index():
                expected = math.sqrt(
                    np.var(self.dataSet[name]['close'][start:(i + 1)]) * (i + 1. - start) / (i - start))
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected,
                                                                                               calculated))
        with self.assertRaises(ValueError):
            _ = SecurityMovingStandardDeviation(window, ['close', 'open'])

    def testSecurityMovingStandardDeviationDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingStandardDeviation, window=10, dependency=['x'])

    def testSecurityMovingStandardDeviationPickle(self):
        self.template_test_pickle(SecurityMovingStandardDeviation, window=10, dependency=['x'])

    def testSecurityMovingMax(self):
        window = 10
        ma1 = SecurityMovingMax(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = np.max(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingMax(window, ['close', 'open'])

    def testSecurityMovingMaxDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingMax, window=10, dependency=['x'])

    def testSecurityMovingMaxPickle(self):
        self.template_test_pickle(SecurityMovingMax, window=10, dependency=['x'])

    def testSecurityMovingMinimum(self):
        window = 10
        ma1 = SecurityMovingMin(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = np.min(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingMin(window, ['close', 'open'])

    def testSecurityMovingMinimumDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingMin, window=10, dependency=['x'])

    def testSecurityMovingMinimumPickle(self):
        self.template_test_pickle(SecurityMovingMin, window=10, dependency=['x'])

    def testSecurityMovingQuantile(self):
        window = 10
        mq = SecurityMovingQuantile(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mq.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mq.value
            for name in value.index():
                con = self.dataSet[name]['close'][start:(i + 1)]
                sorted_con = sorted(con)
                expected = sorted_con.index(self.dataSet[name]['close'][i]) / (len(sorted_con) - 1.)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingQuantileDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingQuantile, window=10, dependency=['x'])

    def testSecurityMovingQuantilePickle(self):
        self.template_test_pickle(SecurityMovingQuantile, window=10, dependency=['x'])

    def testSecurityMovingAllTrue(self):
        window = 3

        self.aapl['close'] = self.aapl['close'] > 0.
        self.ibm['close'] = self.ibm['close'] > 0.

        mq = SecurityMovingAllTrue(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mq.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mq.value
            for name in value.index():
                con = self.dataSet[name]['close'][start:(i + 1)]
                expected = np.all(con)
                calculated = value[name]
                self.assertEqual(expected, calculated, 'at index {0}\n'
                                                       'expected:   {1}\n'
                                                       'calculated: {2}'.format(i, expected, calculated))

    def testSecurityMovingAllTrueDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingAllTrue, window=10, dependency=SecurityLatestValueHolder('x') > 0.)

    def testSecurityMovingAllTruePickle(self):
        self.template_test_pickle(SecurityMovingAllTrue, window=10, dependency=SecurityLatestValueHolder('x') > 0.)

    def testSecurityMovingAnyTrue(self):
        window = 3

        self.aapl['close'] = self.aapl['close'] > 0.
        self.ibm['close'] = self.ibm['close'] > 0.

        mq = SecurityMovingAnyTrue(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            mq.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            if i < 1:
                continue

            value = mq.value
            for name in value.index():
                con = self.dataSet[name]['close'][start:(i + 1)]
                expected = np.any(con)
                calculated = value[name]
                self.assertEqual(expected, calculated, 'at index {0}\n'
                                                       'expected:   {1}\n'
                                                       'calculated: {2}'.format(i, expected, calculated))

    def testSecurityMovingAnyTrueDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingAnyTrue, window=10, dependency=SecurityLatestValueHolder('x') > 0.)

    def testSecurityMovingAnyTruePickle(self):
        self.template_test_pickle(SecurityMovingAnyTrue, window=10, dependency=SecurityLatestValueHolder('x') > 0.)

    def testSecurityMovingSum(self):
        window = 10
        ma1 = SecurityMovingSum(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = np.sum(self.dataSet[name]['close'][start:(i + 1)])
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

    def testSecurityMovingSumDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingSum, window=10, dependency='x')

    def testSecurityMovingSumPickle(self):
        self.template_test_pickle(SecurityMovingSum, window=10, dependency='x')

    def testSecurityMovingCountedPositive(self):
        window = 10
        ma1 = SecurityMovingCountedPositive(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                expected = np.sum(self.dataSet[name]['close'][start:(i + 1)] > 0.0)
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingCountedPositive(window, ['close', 'open'])

    def testSecurityMovingCountedPositiveDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingCountedPositive, window=10, dependency='x')

    def testSecurityMovingCountedPositivePickle(self):
        self.template_test_pickle(SecurityMovingCountedPositive, window=10, dependency='x')

    def testSecurityMovingPositiveAverage(self):
        window = 10
        ma1 = SecurityMovingPositiveAverage(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i + 1 - window

            value = ma1.value
            for name in value.index():
                sampled = list(filter(lambda x: x > 0, self.dataSet[name]['close'][start:(i + 1)]))
                if len(sampled) > 0:
                    expected = np.mean(sampled)
                else:
                    expected = 0.0
                calculated = value[name]
                self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                 'expected:   {1:.12f}\n'
                                                                 'calculated: {2:.12f}'.format(i, expected, calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingPositiveAverage(window, ['close', 'open'])

    def testSecurityMovingPositiveAverageDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingPositiveAverage, window=10, dependency='x')

    def testSecurityMovingPositiveAveragePickle(self):
        self.template_test_pickle(SecurityMovingPositiveAverage, window=10, dependency='x')

    def testSecurityMovingRSI(self):
        window = 10
        rsi = SecurityMovingRSI(window, ['close'])
        pos_avg = SecurityMovingPositiveDifferenceAverage(window, ['close'])
        neg_avg = SecurityMovingNegativeDifferenceAverage(window, ['close'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.aapl['close'][i],
                                  open=self.aapl['open'][i]),
                        ibm=dict(close=self.ibm['close'][i],
                                 open=self.ibm['open'][i]))
            rsi.push(data)
            pos_avg.push(data)
            neg_avg.push(data)

            value = rsi.value
            if i > 0:
                for name in value.index():
                    expected = pos_avg.value[name] / (pos_avg.value[name] - neg_avg.value[name]) * 100
                    calculated = value[name]
                    self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                     'expected:   {1:.12f}\n'
                                                                     'calculated: {2:.12f}'.format(i,
                                                                                                   expected,
                                                                                                   calculated))

    def testSecurityMovingRSIDeepcopy(self):
        self.template_test_deepcopy(SecurityMovingRSI, window=10, dependency='x')

    def testSecurityMovingRSIPickle(self):
        self.template_test_pickle(SecurityMovingRSI, window=10, dependency='x')

    def testSecurityMovingLogReturn(self):
        window = 10
        ma1 = SecurityMovingLogReturn(window, ['close'])
        self.newDataSet = copy.deepcopy(self.dataSet)
        self.newDataSet['aapl']['close'] = np.exp(self.newDataSet['aapl']['close'])
        self.newDataSet['aapl']['open'] = np.exp(self.newDataSet['aapl']['open'])
        self.newDataSet['ibm']['close'] = np.exp(self.newDataSet['ibm']['close'])
        self.newDataSet['ibm']['open'] = np.exp(self.newDataSet['ibm']['open'])

        for i in range(len(self.aapl['close'])):
            data = dict(aapl=dict(close=self.newDataSet['aapl']['close'][i],
                                  open=self.newDataSet['aapl']['open'][i]),
                        ibm=dict(close=self.newDataSet['ibm']['close'][i],
                                 open=self.newDataSet['ibm']['open'][i]))
            ma1.push(data)
            if i < window:
                start = 0
            else:
                start = i - window

            value = ma1.value
            for name in value.index():
                sampled = self.newDataSet[name]['close'][start:(i + 1)]
                if i >= 10:
                    expected = math.log(sampled[-1] / sampled[0])
                    calculated = value[name]
                    self.assertAlmostEqual(expected, calculated, 12, 'at index {0}\n'
                                                                     'expected:   {1:.12f}\n'
                                                                     'calculated: {2:.12f}'.format(i, expected,
                                                                                                   calculated))

        with self.assertRaises(ValueError):
            _ = SecurityMovingLogReturn(window, ['close', 'open'])

    def testSecurityMovingLogReturnDeepcopy(self):
        ma = SecurityMovingLogReturn(10, ['x'])

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        copied = copy.deepcopy(ma)

        for i, v in enumerate(np.random.rand(20)):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)
            copied.push(data)
            if i >= 10:
                for name in ma.value.index():
                    self.assertAlmostEqual(ma.value[name], copied.value[name])

    def testSecurityMovingLogReturnPickle(self):
        ma = SecurityMovingLogReturn(10, ['x'])

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(ma, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
        os.unlink(f.name)

        for i, v in enumerate(np.random.rand(20)):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)
            pickled.push(data)

            if i >= 10:
                for name in ma.value.index():
                    self.assertAlmostEqual(ma.value[name], pickled.value[name])

    def testSecurityMovingHistoricalWindow(self):
        window = 5
        mh = SecurityMovingHistoricalWindow(window, 'close')

        benchmark = {'aapl': deque(maxlen=window),
                     'ibm': deque(maxlen=window)}
        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i]},
                    'ibm': {'close': self.ibm['close'][i]}}

            mh.push(data)
            for name in benchmark:
                benchmark[name].append(data[name]['close'])

            if i >= 1:
                # check by get item methon
                container = mh.value
                for k in range(min(i + 1, window)):
                    calculated = mh[k]
                    for name in calculated.index():
                        self.assertAlmostEqual(calculated[name], benchmark[name][-1 - k],
                                               "at index {0} positon {1} and symbol {2}\n"
                                               "expected:   {3}\n"
                                               "calculated: {4}".format(i, k, name,
                                                                        benchmark[name][-1],
                                                                        calculated[name]))
                # check by value method
                for k in range(min(i + 1, window)):
                    for name in calculated.index():
                        self.assertAlmostEqual(container[name][k], benchmark[name][-1 - k],
                                               "at index {0} positon {1} and symbol {2}\n"
                                               "expected:   {3}\n"
                                               "calculated: {4}".format(i, k, name,
                                                                        benchmark[name][-1],
                                                                        container[name][k]))

    def testSecurityMovingHistoricalWindowDeepcopy(self):
        window = 10
        ma = SecurityMovingHistoricalWindow(window, ['x'])

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        copied = copy.deepcopy(ma)

        for name in ma.value.index():
            np.testing.assert_array_almost_equal(ma.value[name], copied.value[name])

        for v in np.random.rand(20):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)

        copied = copy.deepcopy(ma)
        for name in ma.value.index():
            np.testing.assert_array_almost_equal(ma.value[name], copied.value[name])

    def testSecurityMovingHistoricalWindowPickle(self):
        window = 10
        ma = SecurityMovingHistoricalWindow(window, ['x'])

        data = dict(aapl=dict(x=1.),
                    ibm=dict(x=2.))
        data2 = dict(aapl=dict(x=2.),
                     ibm=dict(x=3.))

        ma.push(data)
        ma.push(data2)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(ma, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            for name in ma.value.index():
                np.testing.assert_array_almost_equal(ma.value[name], pickled.value[name])
        os.unlink(f.name)

        for v in np.random.rand(20):
            data['aapl']['x'] = v
            data['ibm']['x'] = v + 1.
            ma.push(data)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(ma, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
            for name in ma.value.index():
                np.testing.assert_array_almost_equal(ma.value[name], pickled.value[name])
        os.unlink(f.name)

    def testValueHolderCompounding(self):
        window = 10
        ma1 = SecurityMovingAverage(window, 'close')
        compounded1 = SecurityMovingMax(2, ma1)
        compounded2 = SecurityMovingAverage(2, ma1)

        self.assertEqual(compounded1.window, window + 2)

        container = [np.nan, np.nan]
        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'close': self.aapl['close'][i], 'open': self.aapl['open'][i]}}
            ma1.push(data)
            compounded1.push(data)
            compounded2.push(data)

            container[i % 2] = ma1.value['aapl']

            if i >= 1:
                self.assertAlmostEqual(max(container), compounded1.value['aapl'], 12)
                self.assertAlmostEqual(np.mean((container)), compounded2.value['aapl'], 12)

    def testSecurityMovingResidue(self):
        window = 100
        mr = SecurityMovingResidue(window, ('y', 'x'))
        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'y': self.aapl['close'][i], 'x': self.aapl['open'][i]},
                    'ibm': {'y': self.ibm['close'][i], 'x': self.ibm['open'][i]}}
            mr.push(data)

            if i >= window - 1:
                for name in mr.value.index():
                    series_x = getattr(self, name)['open'][i - window + 1:i + 1]
                    series_y = getattr(self, name)['close'][i - window + 1:i + 1]
                    expected_res = series_y[-1] - np.dot(series_x, series_y) / np.dot(series_x, series_x) * series_x[-1]
                    self.assertAlmostEqual(mr.value[name], expected_res, msg= \
                        "at index {0} and symbol {1}\n"
                        "expected:   {2}\n"
                        "calculated: {3}".format(i, name, expected_res, mr.value[name]))

    def testSecurityMovingResidueDeepcopy(self):
        ma = SecurityMovingResidue(10, ['y', 'x'])

        data = dict(aapl=dict(x=1., y=2),
                    ibm=dict(x=2., y=3))
        data2 = dict(aapl=dict(x=2., y=3),
                     ibm=dict(x=3., y=4))

        ma.push(data)
        ma.push(data2)

        copied = copy.deepcopy(ma)

        for i, v in enumerate(np.random.rand(20)):
            data['aapl']['x'] = v
            data['aapl']['y'] = v + 1
            data['ibm']['x'] = v + 1.
            data['ibm']['y'] = v + 2.
            ma.push(data)
            copied.push(data)
            if i >= 10:
                for name in ma.value.index():
                    self.assertAlmostEqual(ma.value[name], copied.value[name])

    def testSecurityMovingResiduePickle(self):
        ma = SecurityMovingResidue(10, ['y', 'x'])

        data = dict(aapl=dict(x=1., y=2),
                    ibm=dict(x=2., y=3))
        data2 = dict(aapl=dict(x=2., y=3),
                     ibm=dict(x=3., y=4))

        ma.push(data)
        ma.push(data2)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(ma, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
        os.unlink(f.name)

        for i, v in enumerate(np.random.rand(20)):
            data['aapl']['x'] = v
            data['aapl']['y'] = v + 1
            data['ibm']['x'] = v + 1.
            data['ibm']['y'] = v + 2.
            ma.push(data)
            pickled.push(data)

            if i >= 10:
                for name in ma.value.index():
                    self.assertAlmostEqual(ma.value[name], pickled.value[name])

    def testSecurityMovingCorrelation(self):
        window = 100
        mr = SecurityMovingCorrelation(window, ('y', 'x'))
        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'y': self.aapl['close'][i], 'x': self.aapl['open'][i]},
                    'ibm': {'y': self.ibm['close'][i], 'x': self.ibm['open'][i]}}
            mr.push(data)

            if i >= window - 1:
                for name in mr.value.index():
                    series_x = getattr(self, name)['open'][i - window + 1:i + 1]
                    series_y = getattr(self, name)['close'][i - window + 1:i + 1]
                    expected_res = np.corrcoef(series_x, series_y)[0, 1]
                    self.assertAlmostEqual(mr.value[name], expected_res, msg= \
                        "at index {0} and symbol {1}\n"
                        "expected:   {2}\n"
                        "calculated: {3}".format(i, name, expected_res, mr.value[name]))

    def testSecurityMovingCorrelationDeepcopy(self):
        ma = SecurityMovingCorrelation(10, ['y', 'x'])

        data = dict(aapl=dict(x=1., y=2),
                    ibm=dict(x=2., y=3))
        data2 = dict(aapl=dict(x=2., y=3),
                     ibm=dict(x=3., y=4))

        ma.push(data)
        ma.push(data2)

        copied = copy.deepcopy(ma)

        for i, v in enumerate(np.random.rand(20)):
            data['aapl']['x'] = v
            data['aapl']['y'] = v + 1
            data['ibm']['x'] = v + 1.
            data['ibm']['y'] = v + 2.
            ma.push(data)
            copied.push(data)
            if i >= 10:
                for name in ma.value.index():
                    self.assertAlmostEqual(ma.value[name], copied.value[name])

    def testSecurityMovingCorrelationPickle(self):
        ma = SecurityMovingCorrelation(10, ['y', 'x'])

        data = dict(aapl=dict(x=1., y=2),
                    ibm=dict(x=2., y=3))
        data2 = dict(aapl=dict(x=2., y=3),
                     ibm=dict(x=3., y=4))

        ma.push(data)
        ma.push(data2)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(ma, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
        os.unlink(f.name)

        for i, v in enumerate(np.random.rand(20)):
            data['aapl']['x'] = v
            data['aapl']['y'] = v + 1
            data['ibm']['x'] = v + 1.
            data['ibm']['y'] = v + 2.
            ma.push(data)
            pickled.push(data)

            if i >= 10:
                for name in ma.value.index():
                    self.assertAlmostEqual(ma.value[name], pickled.value[name])

    def testSecurityMovingRank(self):
        window = 100
        mr = SecurityMovingRank(window, 'x')
        for i in range(len(self.aapl['close'])):
            data = {'aapl': {'y': self.aapl['close'][i], 'x': self.aapl['open'][i]},
                    'ibm': {'y': self.ibm['close'][i], 'x': self.ibm['open'][i]}}
            mr.push(data)

            if i >= window - 1:
                for name in mr.value.index():
                    series_x = getattr(self, name)['open'][i - window + 1:i + 1]
                    expected_res = np.argsort(series_x.argsort())[-1]
                    self.assertAlmostEqual(mr.value[name], expected_res, msg= \
                        "at index {0} and symbol {1}\n"
                        "expected:   {2}\n"
                        "calculated: {3}".format(i, name, expected_res, mr.value[name]))

    def testSecurityMovingRankDeepcopy(self):
        ma = SecurityMovingRank(10, 'x')

        data = dict(aapl=dict(x=1., y=2),
                    ibm=dict(x=2., y=3))
        data2 = dict(aapl=dict(x=2., y=3),
                     ibm=dict(x=3., y=4))

        ma.push(data)
        ma.push(data2)

        copied = copy.deepcopy(ma)

        for i, v in enumerate(np.random.rand(20)):
            data['aapl']['x'] = v
            data['aapl']['y'] = v + 0.1
            data['ibm']['x'] = v + 0.1
            data['ibm']['y'] = v + 0.2
            ma.push(data)
            copied.push(data)
            if i >= 10:
                for name in ma.value.index():
                    self.assertAlmostEqual(ma.value[name], copied.value[name])

    def testSecurityMovingRankPickle(self):
        ma = SecurityMovingRank(10, 'x')

        data = dict(aapl=dict(x=1., y=2),
                    ibm=dict(x=2., y=3))
        data2 = dict(aapl=dict(x=2., y=3),
                     ibm=dict(x=3., y=4))

        ma.push(data)
        ma.push(data2)

        with tempfile.NamedTemporaryFile('w+b', delete=False) as f:
            pickle.dump(ma, f)

        with open(f.name, 'rb') as f2:
            pickled = pickle.load(f2)
        os.unlink(f.name)

        for i, v in enumerate(np.random.rand(20)):
            data['aapl']['x'] = v
            data['aapl']['y'] = v + 0.1
            data['ibm']['x'] = v + 0.1
            data['ibm']['y'] = v + 0.2
            ma.push(data)
            pickled.push(data)

            if i >= 10:
                for name in ma.value.index():
                    self.assertAlmostEqual(ma.value[name], pickled.value[name])
