from __future__ import print_function, division, absolute_import, unicode_literals


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
