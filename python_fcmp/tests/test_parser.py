from __future__ import print_function, division, absolute_import, unicode_literals

import ast

from ..parser import FCMPParser, python_to_fcmp
from ..decorator import *
from ..error import assert_fcmp_error
from python_fcmp import fcmp

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


@out_args('y_out')
@cast_array('srcY', 'weights', 'y_out')
def for_loop(srcHeight, srcWidth, srcDepth, srcY, weights, y_out):
    margin = 100.0
    n_feature = int(len(srcY) / 3)
    ap = 0.0
    an = 0.0
    for i in range(n_feature):
        ap_d = (srcY[i] - srcY[n_feature + i]) ** 2
        an_d = (srcY[i] - srcY[2 * n_feature + i]) ** 2
        ap = ap + ap_d
        an = an + an_d
    diff = ap - an + margin
    #     diff = 1.0 + margin
    if diff > 0.0:
        y_out[0] = diff
    else:
        y_out[0] = 0.0
    #     y_out[0] = max(diff + margin, 0.0)
    return y_out[0]


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
    code = python_to_fcmp(cyclic_lr, True)
    assert_fcmp_error(code == 'function cyclic_lr(rate, iterNum, batch, initRate);\n'
                              '    num_batch_per_epoch = 10;\n'
                              '    step_size = 10;\n'
                              '    max_lr = 0.01;\n'
                              '    batch_cum = ((num_batch_per_epoch * iterNum) + batch);\n'
                              '    cycle = int(((batch_cum / (2 * step_size)) + 1));\n'
                              '    x = abs((((batch_cum / step_size) - (2 * cycle)) + 1));\n'
                              '    rate = (initRate + ((max_lr - initRate) * max(0, (1 - x))));\n'
                              '    return (rate);\n'
                              'endsub;\n', "")


def test_python_to_fcmp():
    code = python_to_fcmp(study_day, True)
    assert_fcmp_error(code == 'function study_day(intervention_date[*], event_date[*]);outargs intervention_date;\n'
                              '    n = (event_date - intervention_date);\n'
                              '    m = 0;\n'
                              '    a = [1, 2, 3];\n'
                              '    c = a[1];\n'
                              '    do i = 3 to 9 by 1;\n'
                              '        a = i;\n'
                              '    end;\n'
                              '    BAND(n > 0, n eq 0 & 0 eq m & m eq 0);\n'
                              '    if n <= 0 & m > 0 then do;\n'
                              '        n = ((n + (1 * 4)) - 121);\n'
                              '    end;\n'
                              '    else \n'
                              '         if m eq 0 then do;\n'
                              '        m = 2;\n'
                              '        n = 1;\n'
                              '         end;\n'
                              '    end;\n'
                              '    return ;\n'
                              'endsub;\n', "")


def test_back_prop():
    code = python_to_fcmp(back_prop, True)
    assert_fcmp_error(code == 'function back_prop(srcHeight, srcWidth, srcDepth, srcY[*], Y[*], weights[*], deltas[*], gradient_out[*], srcDeltas_out[*]);outargs gradient_out, srcDeltas_out;\n' \
                              '    gradient_out[1] = (deltas[1] * srcY[1] ** 2);\n'
                              '    gradient_out[2] = deltas[1];\n' \
                              '    srcDeltas_out[1] = (deltas[1] * (((2 * weights[1]) * srcY[1]) + weights[2]));\n' \
                              '    return ;\n'
                              'endsub;\n', "")


def test_decorator():
    @cast_array('a', 'b')
    def dummy_function(a, b):
        b = 10


def test_for_loop():
    code = python_to_fcmp(for_loop, True)


def code_fcmp_func():
    shape = 20
    A = 1
    A = fcmp.reshape(A, (20, 10))
    k = fcmp.reduce_axis((0, 10))
    lhs = fcmp.compute((shape,), lambda i: fcmp.sum(A[i, k], k))


def test_fcmp_function():
    code = python_to_fcmp(code_fcmp_func, True)


@out_args('y_out')  # pass by reference
@cast_array('srcY', 'weights', 'y_out')  # declare the arguments as array type
def compute_forward(srcHeight, srcWidth, srcDepth, srcY, weights, y_out):
    margin = 2.0
    n_feature = int(srcWidth / 3)
    ap = 0.0
    an = 0.0
    k = fcmp.reduce_axis((0, n_feature))
    ap = fcmp.compute((1,), lambda: fcmp.sum((srcY[k] - srcY[n_feature + k]) ** 2, k))
    # an = fcmp.compute((1,), lambda: fcmp.sum((srcY[k] - srcY[2 * n_feature + k]) ** 2, k))
    # for i in range(n_feature):
    #     ap = ap + (srcY[i] - srcY[n_feature + i]) ** 2
    #     an = an + (srcY[i] - srcY[2 * n_feature + i]) ** 2
    ap = ap ** 0.5
    an = an ** 0.5
    diff = ap - an + margin
    y_out[0] = max(diff, 0.0)
    return y_out[0]


def test_compute():
    code = python_to_fcmp(compute_forward, True)


@out_args('y_out')  # pass by reference
@cast_array('srcY', 'weights', 'y_out')  # declare the arguments as array type
def compute_forward2(srcHeight, srcWidth, srcDepth, srcY, weights, y_out):
    wd = fcmp.reduce_axis((0, srcWidth))
    ht = fcmp.reduce_axis((0, srcHeight))
    eps = 0.000001
    srcY = fcmp.reshape(srcY, (srcDepth, srcHeight, srcWidth))
    mean = fcmp.compute((srcDepth), lambda i: fcmp.sum(srcY[i, ht, wd] / srcHeight / srcWidth, [ht, wd]))
    var = fcmp.compute((srcDepth), lambda i: fcmp.sum((srcY[i, ht, wd] - mean[i]) ** 2 / srcHeight / srcWidth, [ht, wd]))
    y_out = fcmp.compute((srcDepth, srcHeight, srcWidth), lambda i, j, m:
                         (srcY[i, j, m] - mean[m]) / (var[m] + eps) ** 0.5)
    return y_out[0]

def test_compute2():
    code = python_to_fcmp(compute_forward2, True)