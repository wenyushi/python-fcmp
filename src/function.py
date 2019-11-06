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


def range(*args, ):
    args = args[0]
    assert_fcmp_error(len(args) <= 3, "Range function can only accept at most 3 arguments")
    a = 1
    c = 1
    b = args[0]
    if len(args) == 1:
        b = args[0]
    elif len(args) == 2:
        a = args[0]
        b = args[1]
    elif len(args) == 3:
        a = args[0]
        b = args[1]
        c = args[2]
    return '{} to {} by {};'.format(a, b, c)


def len_(a):
    return 'dim({})'.format(a)
