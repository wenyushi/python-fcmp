from __future__ import print_function, division, absolute_import, unicode_literals


def lt(a, b):
    "Same as a < b."
    return '{} < {}'.format(a, b)


def le(a, b):
    "Same as a <= b."
    return '{} <= {}'.format(a, b)


def eq(a, b):
    "Same as a == b."
    return '{} eq {}'.format(a, b)


def ne(a, b):
    "Same as a != b."
    return '{} ne {}'.format(a, b)


def ge(a, b):
    "Same as a >= b."
    return '{} >= {}'.format(a, b)


def gt(a, b):
    "Same as a > b."
    return '{} > {}'.format(a, b)

# Logical Operations **********************************************************#


def not_(a):
    return 'not({})'.format(a)


def _or(a, b):
    return '{} | {}'.format(a, b)


def _and(a, b):
    return '{} & {}'.format(a, b)

# Mathematical/Bitwise Operations *********************************************#


def abs(a):
    "Same as abs(a)."
    return 'abs()'.format(a)


def add(a, b):
    "Same as a + b."
    return '({} + {})'.format(a, b)


def and_(a, b):
    "Same as a & b."
    return 'BAND({}, {})'.format(a, b)


def lshift(a, b):
    "Same as a << b."
    return 'BLSHIFT({}, {})'.format(a, b)


def mod(a, b):
    "Same as a % b."
    return 'mod({}, {})'.format(a, b)


def mul(a, b):
    "Same as a * b."
    return '({} * {})'.format(a, b)

def neg(a):
    "Same as -a."
    return '-{}'.format(a)


def or_(a, b):
    "Same as a | b."
    return 'BOR({}, {})'.format(a, b)


def pow(a, b):
    "Same as a ** b."
    return '{} ** {}'.format(a, b)


def rshift(a, b):
    "Same as a >> b."
    return 'BRSHIFT({}, {})'.format(a, b)


def sub(a, b):
    "Same as a - b."
    return '({} - {})'.format(a, b)


def truediv(a, b):
    "Same as a / b."
    return '({} / {})'.format(a, b)


def xor(a, b):
    "Same as a ^ b."
    return 'BXOR{}'.format(a, b)
