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
    return
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
    return


@out_args('gradient_out', 'srcDeltas_out')
@cast_array('srcY', 'Y', 'weights', 'deltas', 'gradient_out', 'srcDeltas_out')
def back_prop(srcHeight, srcWidth, srcDepth, srcY, Y, weights,
              deltas, gradient_out, srcDeltas_out):
    gradient_out[0] = deltas[0] * (srcY[0] ** 2)
    gradient_out[1] = deltas[0]
    srcDeltas_out[0] = deltas[0] * (2 * weights[0] * srcY[0] + weights[1])
    return


def cyclic_lr(rate, iterNum, batch, initRate):
    num_batch_per_epoch = 10
    step_size = 10
    max_lr = 0.01
    batch_cum = num_batch_per_epoch * iterNum + batch
    cycle = int(batch_cum / (2 * step_size) + 1)
    x = abs(batch_cum / step_size - 2 * cycle + 1)
    rate = initRate + (max_lr - initRate) * max(0, 1-x)
    return rate


@cast_array('a', 'b')
def dummy_function(a, b):
    b = 10


def test_parser():
    expr = ast.parse(source)

    par = FCMPParser()
    par.visit(expr)
    par.pretty_print()


def test_cyclic_lr():
    python_to_fcmp(cyclic_lr, True)


def test_python_to_fcmp():
    python_to_fcmp(study_day, True)


def test_back_prop():
    code = python_to_fcmp(back_prop, True)
    print(code)



def test_decorator():
    @cast_array('a', 'b')
    def dummy_function(a, b):
        b = 10
