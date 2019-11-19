"""
Decorator of Python function.
The implementation decorator is in python_fcmp/function.py
"""
from __future__ import print_function, division, absolute_import, unicode_literals

import functools

from .error import FCMPParserError


def cast_array(*args):
    """ cast argument in python function as array type. """
    def decorator_wrapper(func):
        print('Arguments, {}, are casted to array type'.format(', '.join(args)))

        @ functools.wraps(func)
        def _wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return _wrapper
    return decorator_wrapper


def out_args(*args):
    """ declare args as outargs. For details, please check FCMP documentation. """
    def decorator_wrapper(func):
        print('Arguments, {}, are declared as outargs.'.format(', '.join(args)))

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return _wrapper
    return decorator_wrapper


def unsupport_op_call(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as k:
            raise FCMPParserError("The operator or order, {}, is not supported yet.".format(k.args[0]))

    return _wrapper