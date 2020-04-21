""" The module contains Python implementation of FCMP function. """
from __future__ import print_function, division, absolute_import, unicode_literals

import numpy as np
import math


def compute(out_dims, fcompute):
    """
    Construct a new array by computing over the shape domain.

    Parameters
    ----------
    out_dims : tuple
        Specifies the shape of the generated array.
    fcompute : FCMPStmt
        Specifies the input source expression.

    Returns
    -------
    :class:`string`

    """
    code = fcompute.__code__
    # out_ndim = ndim
    # if code.co_argcount == 0:
    #     arg_names = ["i%d" % i for i in range(ndim)]
    # else:
    #     arg_names = code.co_varnames[:code.co_argcount]
    #     out_ndim = code.co_argcount
    #
    # if out_ndim != len(arg_names):
    #     raise ValueError("fcompute do not match dimension, ndim=%d" % ndim)
    if isinstance(out_dims, int):
        out_dims = [out_dims]
    dim_var = [range(s) for s in out_dims]
    body = fcompute(*dim_var)
    return body


def reshape(a, shape):
    """ reshape doesn't present in fcmp code; it mainly uses for register fcmp variable. """
    return np.reshape(a, shape)


def sum(a, axis):
    '''srcDeltas_out = fcmp.compute((srcDepth), lambda i: fcmp.sum(srcY[i, ht, wd] - mean[i], [ht, wd]))'''
    np.sum(a, axis)
    return


def reduce_axis(a):
    """
    Create an iterator for reduction.

    Parameters
    ----------
    a : tuple
        Specifies the iteration range

    Returns
    -------
    :class:`string`

    """
    return range(a)

def floor(a):
    return math.floor(a)

def ceil(a):
    return math.ceil(a)