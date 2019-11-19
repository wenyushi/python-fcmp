from __future__ import print_function, division, absolute_import, unicode_literals

from . import fcmp


class Stmt:
    def __init__(self, prg, lineno, col_offset):
        self._prg = prg
        self.lineno = lineno
        self.col_offset = col_offset

    @property
    def prg(self):
        return self._prg

    def __str__(self):
        return self.prg

    def __lt__(self, other):
        if self.lineno == other.lineno:
            return self.col_offset < other.col_offset
        else:
            return self.lineno < other.col_offset


class FCMPStmt(Stmt):
    '''
    FCMP Statement
    Refers to the statement invoked by the function in fcmp.py

    '''
    def __init__(self, func, args, ret, lineno, col_offset):
        self.func = func
        self.args = args
        self.ret = ret
        self.lineno = lineno
        self.col_offset = col_offset

    @property
    def prg(self):
        return getattr(fcmp, self.func)(*self.args, self.ret)

    def __str__(self):
        return self.prg

    def __lt__(self, other):
        if self.lineno == other.lineno:
            return self.col_offset < other.col_offset
        else:
            return self.lineno < other.col_offset