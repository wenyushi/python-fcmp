from __future__ import print_function, division, absolute_import, unicode_literals

from python_fcmp.codegen import numpy, fcmp


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
        self._prg = None

    @property
    def prg(self):
        if self._prg is not None:
            return self._prg
        self._prg = getattr(fcmp, self.func)(self.ret, *self.args)
        return self._prg


class NumpyStmt(FCMPStmt):
    def __init__(self, func, args, ret, lineno, col_offset):
        super(NumpyStmt, self).__init__(func, args, ret, lineno, col_offset)

    @property
    def prg(self):
        if self._prg is not None:
            return self._prg
        self._prg = getattr(numpy, self.func)(self.ret, *self.args)
        return self._prg
