from __future__ import print_function, division, absolute_import, unicode_literals

from .error import assert_fcmp_error


def cast_array(*args):
    ret = []
    for arg in args[0]:
        ret.append('{}[*]'.format(arg))
    return ret


def out_args(*args):
    ret = [arg for arg in args[0]]
    return 'outargs ' + ', '.join(ret) + ';'


def range(*args):
    args = args[0]
    assert_fcmp_error(len(args) <= 3, "Range function can only accept at most 3 arguments")
    a = 0
    c = 1
    try:
        b = str(int(args[0]) - 1)
    except ValueError:
        b = '{} - 1'.format(args[0])
    if len(args) == 1:
        try:
            b = str(int(args[0]) - 1)
        except ValueError:
            b = '{} - 1'.format(args[0])
    elif len(args) == 2:
        a = args[0]
        try:
            b = str(int(args[1]) - 1)
        except ValueError:
            b = '{} - 1'.format(args[1])
    elif len(args) == 3:
        a = args[0]
        try:
            b = str(int(args[1]) - 1)
        except ValueError:
            b = '{} - 1'.format(args[1])
        c = args[2]
    return '{} to {} by {};'.format(a, b, c)


def len_(a):
    return 'dim({})'.format(a[0])


def max_(*args):
    res = [str(arg) for arg in args[0]]
    return 'max({})'.format(', '.join(res))


def min_(*args):
    res = [str(arg) for arg in args[0]]
    return 'min({})'.format(', '.join(res))


def mean_(*args):
    res = [str(arg) for arg in args[0]]
    return 'mean({})'.format(', '.join(res))


def sum_(*args):
    res = [str(arg) for arg in args[0]]
    return 'sum({})'.format(', '.join(res))


def pow_(a, b):
    return 'pow({}, {})'.format(a, b)


def int_(a):
    return 'int({})'.format(a[0])


def abs_(a):
    return 'abs({})'.format(a[0])