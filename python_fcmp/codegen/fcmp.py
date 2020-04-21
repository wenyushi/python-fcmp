from __future__ import print_function, division, absolute_import, unicode_literals

from python_fcmp.error import assert_fcmp_error
from python_fcmp.codegen import operator
from python_fcmp.statement import FCMPStmt
from python_fcmp.utils import build_one_dim_subscript

ASSIGN_FUNCTION = ['floor', 'ceil']
EXPLICIT_FUNCTION = ['compute', 'zeros']  # the function will explicitly present in FCMP code
EXPLICIT_FUNCTION += ASSIGN_FUNCTION
__all__ = ['compute', 'reshape', 'sum', 'reduce_axis', 'lambda_', 'floor', 'ceil']


def compute(ret, out_dims, fcompute):
    """
    Construct a new array by computing over the shape domain.

    Parameters
    ----------
    ret : string
        Specifies the return variable of the FCMP function
    out_dims : tuple
        Specifies the shape of the generated array.
    fcompute : FCMPStmt
        Specifies the input source expression.

    Returns
    -------
    :class:`string`

    """
    # fcompute should be fcmpstmt(lambda function)
    assert_fcmp_error(type(fcompute) == FCMPStmt, "fcompute should be a lambda function type.")
    n_dims = len(out_dims)
    if isinstance(out_dims, str):
        n_dims = 1
        out_dims = [out_dims]
    lambda_args = fcompute.args[0]

    assert_fcmp_error(n_dims == len(lambda_args),
                      "The length of out_dims should be the same as the number of arguments in lambda function.")
    # assign to
    # convert multi-dims access to one dimension subscript
    if n_dims == 1:
        one_dim_subscript = lambda_args[0] + ' + 1'
    else:
        one_dim_subscript = build_one_dim_subscript(out_dims, lambda_args)
    ret = ret + '[{}]'.format(one_dim_subscript)  # A -> A[i * height + j]

    code = ''
    # out_dims loops
    for dim in range(n_dims):
        code += 4 * dim * ' '  # indent
        code += 'do {} = 0 to ({} - 1) by 1;\n'.format(lambda_args[dim], out_dims[dim])

    # compute core we can remove str check
    if isinstance(fcompute, str):
        code = code + (n_dims * 4 * ' ') + ret + ' = ' + fcompute + ';\n'
    else:
        fcompute.ret = ret  # A -> A[i, j]
        # indent correct
        snippet = fcompute.prg
        if snippet.count('\n') > 1:
            snippet = snippet.replace('\n', '\n' + ' ' * n_dims * 4)[: -len(' ' * n_dims * 4)]
        # compute core
        code = code + (n_dims * 4 * ' ') + snippet
    # loop end code
    for dim in range(1 - n_dims, 1, 1):
        code += 4 * -dim * ' '  # indent
        code += 'end;\n'
    return code
    # code = 'do {} = 0 to {} by 1;\n' \
    #        '    do {} = 0 to {} by 1;\n'.format()

    # return np.fromfunction(fcompute, shape, dtype = float)


def lambda_(ret, *args):
    """ for args, the last item is lambda function, the first few are lambda arguments"""
    func_core = args[-1]
    return ret + ' = ' + func_core + ';\n'


def reshape(ret, a, shape):
    """ reshape doesn't present in fcmp code; it mainly uses for register fcmp variable. """
    shape = [str(i) for i in shape]
    return 'call dynamic_array({}, {});'.format(a, ', '.join(shape))


def floor(ret, a):
    return 'floor({})'.format(a)


def ceil(ret, a):
    return 'ceil({})'.format(a)


def sum(ret, lambda_a, a, axis):
    """
    Sum of array elements over a given axis or a list of axes

    Parameters
    ----------
    ret : string
        Specifies the return variable of the FCMP function.
    a : string
        Summation function.
    axis FCMPStmt or list of FCMPStmt
        Axis or axes along which a sum is performed.

    Returns
    -------
    :class:`string`

    """
    # axis is a list
    # below should be put into iteration body
    # eg # lhs = fcmp.compute((shape,), lambda i: fcmp.sum(A[i, k], axis=k)
    # do i = 0 to shape by 1;
    #   do k_i = 0 to 10 by 1;
    #       lhs[i] = lhs[i] + A[i, k_i]
    code = ''
    if not isinstance(axis, list):
        axis = [axis]
    # loop header
    for i, ax in enumerate(axis):
        code = code + (4 * i * ' ') + ax[1].prg
    # if lambda_a != LAMBDA_EMPTY_ARGS:
    #     for l_a in lambda_a:
    #         a = a.replace(operator.add(l_a, 1), l_a)
    #         a = a.replace(l_a + ' + 1', l_a)

    # summation body
    code = code + (4 * len(axis) * ' ') + ret + ' = ' + operator.add(ret, a) + ';\n'
    # loop end
    for i in range(1 - len(axis), 1, 1):
        code = code + (4 * -i * ' ') + 'end;\n'
    return code


def reduce_axis(ret, a):
    """
    Create an iterator for reduction.

    Parameters
    ----------
    ret : string
        Specifies the return variable of the FCMP function
    a : tuple
        Specifies the iteration range

    Returns
    -------
    :class:`string`

    """
    # reduce_axis((0, 10)) python 0~9; fcmp 1~10
    if len(a) == 1:
        start = 0
        try:
            end = str(int(a[0]) - 1)
        except ValueError:
            end = '({} - 1)'.format(a[0])
    elif len(a) == 2:
        start = a[0]
        try:
            end = str(int(a[1]) - 1)
        except ValueError:
            end = '({} - 1)'.format(a[1])
    return 'do {} = {} to {} by {};\n'.format(ret, start, end, 1)

