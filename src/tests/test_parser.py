from __future__ import print_function, division, absolute_import, unicode_literals

import ast

from ..parser import FCMPParser, python_to_fcmp
from ..decorator import *

source = \
'''
@cast_array('intervention_date', 'event_date')
def study_day(intervention_date, event_date):
    n=event_date-intervention_date
    m = 0
    a = [1, 2, 3]
    c = a[0]
    for i in range(3, 10):
        a = i
    (n > 0) & (n == 0 == m == 0)
    if n <= 0 and m > 0:
        n=n+1*4-121
    elif m == 0:
        m = 2
        n = 1
    return (n)
'''


@out_args('intervention_date')
@cast_array('intervention_date', 'event_date')
def study_day(intervention_date, event_date):
    n = event_date - intervention_date
    m = 0
    a = [1, 2, 3]
    c = a[0]
    for i in range(3, 10):
        a = i
    (n > 0) & (n == 0 == m == 0)
    if n <= 0 and m > 0:
        n=n+1*4-121
    elif m == 0:
        m = 2
        n = 1
    return n


@cast_array('a', 'b')
def dummy_function(a, b):
    b = 10


def test_parser():
    expr = ast.parse(source)

    par = FCMPParser()
    par.visit(expr)
    par.pretty_print()


def test_python_to_fcmp():
    python_to_fcmp(study_day, True)


def test_decorator():
    @cast_array('a', 'b')
    def dummy_function(a, b):
        b = 10
