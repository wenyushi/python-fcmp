from __future__ import print_function, division, absolute_import, unicode_literals

from python_fcmp.codegen import operator


def build_one_dim_subscript(shape, indices):
    n_dims = len(shape)
    tmp = shape[-1]
    cum_shape = [tmp]
    for d in shape[-2::-1]:
        tmp = operator.mul(d, tmp)
        cum_shape.append(tmp)
    cum_shape = cum_shape[-1::-1]
    for i, d in enumerate(cum_shape[1:]):
        if i == 0:
            one_dim_subscript = operator.mul(d, '{}'.format(indices[i]))
        else:
            one_dim_subscript = operator.add(one_dim_subscript, operator.mul(d, '{}'.format(indices[i])))
    one_dim_subscript = one_dim_subscript + ' + ' + indices[n_dims - 1] + ' + 1'
    return one_dim_subscript
