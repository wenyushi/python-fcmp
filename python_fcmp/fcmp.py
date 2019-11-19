from __future__ import print_function, division, absolute_import, unicode_literals

from .error import assert_fcmp_error
from python_fcmp import operator
from python_fcmp import function
import numpy as np

RECURSION_INDEX = ['i', 'j', 'm', 'n']
EXPLICIT_FUNCTION = ['compute']  # the function will explicitly present in FCMP code


def compute(out_dims, fcompute, ret=None):
    # fcompute should be fcmpstmt or string
    # assert_fcmp_error(type(fcompute) == FCMPStmt, "fcompute should be a lambda function type.")

    n_dims = len(out_dims)
    assert_fcmp_error(n_dims <= len(EXPLICIT_FUNCTION), "The length of out_dims "
                                                        "cannot be greater than {}.".format(len(EXPLICIT_FUNCTION)))

    code = ''
    for dim in range(n_dims):
        code += 4 * dim * ' '  # indent
        code += 'do {} = 1 to {};\n'.format(RECURSION_INDEX[dim], out_dims[dim])
    fcompute.ret = ret + '[{}]'.format(', '.join(RECURSION_INDEX[:n_dims]))  # A -> A[i, j]
    code = code + n_dims * 4 * ' ' + fcompute.prg

    for dim in range(n_dims, 0, -1):
        code += 4 * dim * ' '  # indent
        code += 'end;\n'
    return code
    # code = 'do {} = 0 to {} by 1;\n' \
    #        '    do {} = 0 to {} by 1;\n'.format()

    # return np.fromfunction(fcompute, shape, dtype = float)


def reshape(a, shape, ret=None):
    shape = [str(i) for i in shape]
    return 'call dynamic_array({}, {});'.format(a, ', '.join(shape))


def sum(a, axis, ret=None):
    # axis is a list
    # below should be put into iteration body
    # eg # lhs = fcmp.compute((shape,), lambda i: fcmp.sum(A[i, k], axis=k)
    # do i = 0 to shape by 1;
    #   do k_i = 0 to 10 by 1;
    #       lhs[i] = lhs[i] + A[i, k_i]
    a = a.replace(axis[0], axis[0] + '_i')
    code = axis[1].prg + 4 * ' '
    return code + ret + ' = ' + operator.add(ret, a) + ';\n' + 4 * ' ' + 'end;\n'


def reduce_axis(a, ret=None):
    # return 'do ' + function.range(a) + '\n'
    return 'do {} = {};\n'.format(ret+'_i', function.range(a))
