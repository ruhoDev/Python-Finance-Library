# -*- coding: utf-8 -*-
u"""
Created on 2015-2-20

@author: cheng.li
"""

from PyFin.Enums._BizDayConventions cimport BizDayConventions
from PyFin.Enums._DateGeneration cimport DateGeneration
from PyFin.Enums._TimeUnits cimport TimeUnits
from PyFin.DateUtilities.Date cimport Date
from PyFin.DateUtilities.Period cimport Period
from PyFin.DateUtilities.Calendar cimport Calendar
from PyFin.Env import Settings
from PyFin.Utilities.Asserts cimport require

cdef class Schedule(object):

    def __init__(self,
                 Date effectiveDate,
                 Date terminationDate,
                 Period tenor,
                 Calendar calendar,
                 int convention=BizDayConventions.Following,
                 int terminationConvention=BizDayConventions.Following,
                 int dateGenerationRule=DateGeneration.Forward,
                 bint endOfMonth=False,
                 Date firstDate=None,
                 Date nextToLastDate=None):

        cdef int i
        cdef size_t dateLen
        cdef Calendar nullCalendar
        cdef Date evalDate
        cdef int y
        cdef int periods
        cdef Date seed
        cdef Date temp
        cdef Date exitDate

        # Initialize private data
        self._effectiveDate = effectiveDate
        self._terminationDate = terminationDate
        self._tenor = tenor
        self._cal = calendar
        self._convention = convention
        self._terminationConvention = terminationConvention
        self._rule = dateGenerationRule
        self._dates = []
        self._isRegular = []

        if tenor < Period("1M"):
            self._endOfMonth = False
        else:
            self._endOfMonth = endOfMonth

        if not firstDate or firstDate == effectiveDate:
            self._firstDate = None
        else:
            self._firstDate = firstDate

        if not nextToLastDate or nextToLastDate == terminationDate:
            self._nextToLastDate = None
        else:
            self._nextToLastDate = nextToLastDate

        # in many cases (e.g. non-expired bonds) the effective date is not
        # really necessary. In these cases a decent placeholder is enough
        if not effectiveDate and not firstDate and dateGenerationRule == DateGeneration.Backward:
            evalDate = Settings.evaluationDate
            require(evalDate < terminationDate, ValueError, "null effective date")
            if nextToLastDate:
                y = int((nextToLastDate - evalDate) / 366) + 1
                effectiveDate = nextToLastDate - Period(length=y, units=TimeUnits.Years)
            else:
                y = int((terminationDate - evalDate) / 366) + 1
                effectiveDate = terminationDate - Period(length=y, units=TimeUnits.Years)
        else:
            require(effectiveDate, ValueError, "null effective date")

        require(effectiveDate < terminationDate, ValueError, "effective date ({0}) "
                                                                 "later than or equal to termination date ({1}"
        .format(effectiveDate, terminationDate))

        if tenor.length() == 0:
            self._rule = DateGeneration.Zero
        else:
            require(tenor.length() > 0, ValueError, "non positive tenor ({0:d}) not allowed".format(tenor.length()))

        if self._firstDate:
            if self._rule == DateGeneration.Backward or self._rule == DateGeneration.Forward:
                require(effectiveDate < self._firstDate < terminationDate, ValueError,
                            "first date ({0}) out of effective-termination date range [{1}, {2})"
                            .format(self._firstDate, effectiveDate, terminationDate))
                # we should ensure that the above condition is still
                # verified after adjustment
            elif self._rule == DateGeneration.Zero:
                raise ValueError("first date incompatible with {0:d} date generation rule".format(self._rule))
            else:
                raise ValueError("unknown rule ({0:d})".format(self._rule))

        if self._nextToLastDate:
            if self._rule == DateGeneration.Backward or self._rule == DateGeneration.Forward:
                require(effectiveDate < self._nextToLastDate < terminationDate, ValueError,
                            "next to last date ({0}) out of effective-termination date range [{1}, {2})"
                            .format(self._nextToLastDate, effectiveDate, terminationDate))
                # we should ensure that the above condition is still
                # verified after adjustment
            elif self._rule == DateGeneration.Zero:
                raise ValueError("next to last date incompatible with {0:d} date generation rule".format(self._rule))
            else:
                raise ValueError("unknown rule ({0:d})".format(self._rule))

        # calendar needed for endOfMonth adjustment
        nullCalendar = Calendar("Null")
        periods = 1

        if self._rule == DateGeneration.Zero:
            self._tenor = Period(length=0, units=TimeUnits.Years)
            self._dates.extend([effectiveDate, terminationDate])
            self._isRegular.append(True)
        elif self._rule == DateGeneration.Backward:
            self._dates.append(terminationDate)
            seed = terminationDate
            if self._nextToLastDate:
                self._dates.insert(0, self._nextToLastDate)
                temp = nullCalendar.advanceDate(seed,
                                                Period(length=-periods * self._tenor.length(), units=self._tenor.units()),
                                                convention, self._endOfMonth)
                if temp != self._nextToLastDate:
                    self._isRegular.insert(0, False)
                else:
                    self._isRegular.insert(0, True)
                seed = self._nextToLastDate

            exitDate = effectiveDate
            if self._firstDate:
                exitDate = self._firstDate

            while True:
                temp = nullCalendar.advanceDate(seed,
                                                Period(length=-periods * self._tenor.length(), units=self._tenor.units()),
                                                convention, self._endOfMonth)
                if temp < exitDate:
                    if self._firstDate and self._cal.adjustDate(self._dates[0], convention) != self._cal.adjustDate(
                            self._firstDate, convention):
                        self._dates.insert(0, self._firstDate)
                        self._isRegular.insert(0, False)
                    break
                else:
                    # skip dates that would result in duplicates
                    # after adjustment
                    if self._cal.adjustDate(self._dates[0], convention) != self._cal.adjustDate(temp, convention):
                        self._dates.insert(0, temp)
                        self._isRegular.insert(0, True)
                    periods += 1

            if self._cal.adjustDate(self._dates[0], convention) != self._cal.adjustDate(effectiveDate, convention):
                self._dates.insert(0, effectiveDate)
                self._isRegular.insert(0, False)

        elif self._rule == DateGeneration.Forward:
            self._dates.append(effectiveDate)

            seed = self._dates[-1]

            if self._firstDate:
                self._dates.append(self._firstDate)
                temp = nullCalendar.advanceDate(seed,
                                                Period(length=periods * self._tenor.length(), units=self._tenor.units()),
                                                convention, self._endOfMonth)
                if temp != self._firstDate:
                    self._isRegular.append(False)
                else:
                    self._isRegular.append(True)
                seed = self._firstDate

            exitDate = terminationDate
            if self._nextToLastDate:
                exitDate = self._nextToLastDate

            while True:
                temp = nullCalendar.advanceDate(seed,
                                                Period(length=periods * self._tenor.length(), units=self._tenor.units()),
                                                convention, self._endOfMonth)
                if temp > exitDate:
                    if self._nextToLastDate and self._cal.adjustDate(self._dates[-1],
                                                                     convention) != self._cal.adjustDate(
                            self._nextToLastDate, convention):
                        self._dates.append(self._nextToLastDate)
                        self._isRegular.append(False)
                    break
                else:
                    # skip dates that would result in duplicates
                    # after adjustment
                    if self._cal.adjustDate(self._dates[-1], convention) != self._cal.adjustDate(temp, convention):
                        self._dates.append(temp)
                        self._isRegular.append(True)
                    periods += 1

            if self._cal.adjustDate(self._dates[-1], terminationConvention) != self._cal.adjustDate(terminationDate,
                                                                                                    terminationConvention):
                self._dates.append(terminationDate)
                self._isRegular.append(False)
        else:
            raise ValueError("unknown rule ({0:d})".format(self._rule))

        # adjustments
        if self._endOfMonth and self._cal.isEndOfMonth(seed):
            # adjust to end of month
            if convention == BizDayConventions.Unadjusted:
                for i in range(len(self._dates) - 1):
                    self._dates[i] = Date.endOfMonth(self._dates[i])
            else:
                for i in range(len(self._dates) - 1):
                    self._dates[i] = self._cal.endOfMonth(self._dates[i])

            if terminationConvention != BizDayConventions.Unadjusted:
                self._dates[0] = self._cal.endOfMonth(self._dates[0])
                self._dates[-1] = self._cal.endOfMonth(self._dates[-1])
            else:
                if self._rule == DateGeneration.Backward:
                    self._dates[-1] = Date.endOfMonth(self._dates[-1])
                else:
                    self._dates[0] = Date.endOfMonth(self._dates[0])
        else:
            for i in range(len(self._dates) - 1):
                self._dates[i] = self._cal.adjustDate(self._dates[i], convention)

            if terminationConvention != BizDayConventions.Unadjusted:
                self._dates[-1] = self._cal.adjustDate(self._dates[-1], terminationConvention)

        # Final safety checks to remove extra next-to-last date, if
        # necessary.  It can happen to be equal or later than the end
        # date due to EOM adjustments (see the Schedule test suite
        # for an example).

        dateLen = len(self._dates)

        if dateLen >= 2 and self._dates[dateLen - 2] >= self._dates[-1]:
            self._isRegular[dateLen - 2] = (self._dates[dateLen - 2] == self._dates[-1])
            self._dates[dateLen - 2] = self._dates[-1]
            self._dates.pop()
            self._isRegular.pop()

        if len(self._dates) >= 2 and self._dates[1] <= self._dates[0]:
            self._isRegular[1] = (self._dates[1] == self._dates[0])
            self._dates[1] = self._dates[0]
            self._dates = self._dates[1:]
            self._isRegular = self._isRegular[1:]

        require(len(self._dates) >= 1, ValueError, "degenerate single date ({0}) schedule\n"
                                                       "seed date: {1}\n"
                                                       "exit date: {2}\n"
                                                       "effective date: {3}\n"
                                                       "first date: {4}\n"
                                                       "next to last date: {5}\n"
                                                       "termination date: {6}\n"
                                                       "generation rule: {7}\n"
                                                       "end of month: {8}\n"
        .format(self._dates[0],
                seed, exitDate,
                effectiveDate,
                firstDate,
                nextToLastDate,
                terminationDate,
                self._rule, self._endOfMonth))

    cpdef size_t size(self):
        return len(self._dates)

    cpdef Calendar calendar(self):
        return self._cal

    cpdef Period tenor(self):
        return self._tenor

    cpdef bint endOfMonth(self):
        return self._endOfMonth

    cpdef bint isRegular(self, size_t i):
        return self._isRegular[i-1]

    def __getitem__(self, item):
        return self._dates[item]

    def __deepcopy__(self, memo):
        return Schedule(self._effectiveDate,
                        self._terminationDate,
                        self._tenor,
                        self._cal,
                        self._convention,
                        self._terminationConvention,
                        self._rule,
                        self._endOfMonth,
                        self._firstDate,
                        self._nextToLastDate)

    def __reduce__(self):
        d = {}

        return Schedule, (self._effectiveDate,
                          self._terminationDate,
                          self._tenor,
                          self._cal,
                          self._convention,
                          self._terminationConvention,
                          self._rule,
                          self._endOfMonth,
                          self._firstDate,
                          self._nextToLastDate), d

    def __setstate__(self, state):
        pass

    def __richcmp__(self, Schedule other, int op):
        if op == 2:
            return self._effectiveDate == other._effectiveDate \
                   and self._terminationDate == other._terminationDate \
                   and self._tenor == other._tenor \
                   and self._cal == other._cal \
                   and self._convention == other._convention \
                   and self._terminationConvention == other._terminationConvention \
                   and self._rule == other._rule \
                   and self._endOfMonth == other._endOfMonth \
                   and self._firstDate == other._firstDate \
                   and self._nextToLastDate == other._nextToLastDate
