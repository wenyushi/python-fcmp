from __future__ import print_function, division, absolute_import, unicode_literals


class FCMPParserError(ValueError):
    """
    FCMP Parser Error
    """


def assert_fcmp_error(cond, error_msg):
    if not cond:
        raise FCMPParserError(error_msg)
