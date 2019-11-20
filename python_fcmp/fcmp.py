from __future__ import print_function, division, absolute_import, unicode_literals

from .error import assert_fcmp_error
from python_fcmp import operator
from python_fcmp import function

RECURSION_INDEX = ['i', 'j', 'm', 'n']
EXPLICIT_FUNCTION = ['compute']  # the function will explicitly present in FCMP code


def compute(out_dims, fcompute, ret=None):
    # fcompute should be fcmpstmt or string
    # assert_fcmp_error(type(fcompute) == FCMPStmt, "fcompute should be a lambda function type.")
    n_dims = len(out_dims)
    if isinstance(out_dims, str):
        n_dims = 1
        out_dims = [out_dims]

    assert_fcmp_error(n_dims <= len(RECURSION_INDEX), "The length of out_dims "
                                                        "cannot be greater than {}.".format(len(RECURSION_INDEX)))
    # assign to
    # convert multi-dims access to one dimension subscript
    one_dim_subscript = ''
    if n_dims == 1:
        one_dim_subscript = 'i'
    else:
        for i, d in enumerate(out_dims[1:]):
            if i == 0:
                one_dim_subscript = operator.mul(d, '({})'.format(RECURSION_INDEX[i]))
            else:
                one_dim_subscript = operator.add(one_dim_subscript, operator.mul(d, '({})'.format(RECURSION_INDEX[i])))
        one_dim_subscript = operator.add(one_dim_subscript, RECURSION_INDEX[-1])
    ret = ret + '[{}]'.format(one_dim_subscript)  # A -> A[i * height + j]

    code = ''
    # out_dims loops
    for dim in range(n_dims):
        code += 4 * dim * ' '  # indent
        code += 'do {} = 1 to {};\n'.format(RECURSION_INDEX[dim], out_dims[dim])
    # compute core
    if isinstance(fcompute, str):
        code = code + (n_dims * 4 * ' ') + ret + ' = ' + fcompute
    else:
        fcompute.ret = ret  # A -> A[i, j]
        code = code + (n_dims * 4 * ' ') + fcompute.prg
    # loop end code
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
    code = ''
    if not isinstance(axis, list):
        axis = [axis]
    for i, ax in enumerate(axis):
        code = code + (4 * i * ' ') + ax[1].prg

    code = code + (4 * len(axis) * ' ') + ret + ' = ' + operator.add(ret, a) + ';\n'

    for i in range(len(axis), 0, -1):
        code = code + (4 * i * ' ') + 'end;\n'
    return code


def reduce_axis(a, ret=None):
    # return 'do ' + function.range(a) + '\n'
    return 'do {} = {};\n'.format(ret, function.range(a))
