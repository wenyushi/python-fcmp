"""
Decorator of Python function.
The implementation decorator is in src/function.py
"""
from __future__ import print_function, division, absolute_import, unicode_literals

import functools


def cast_array(*args):
    """ cast argument in python function as array type. """
    def decorator_wrapper(func):
        print('Arguments, {}, are casted to array type'.format(', '.join(args)))

        @ functools.wraps(func)
        def _wrapper(*args, **kwargs):
            func(*args, **kwargs)
        return _wrapper
    return decorator_wrapper


def out_args(*args):
    """ declare args as outargs. For details, please check FCMP documentation. """
    def decorator_wrapper(func):
        print('Arguments, {}, are declared as outargs.'.format(', '.join(args)))

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            func(*args, **kwargs)
        return _wrapper
    return decorator_wrapper
