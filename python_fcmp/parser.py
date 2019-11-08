from __future__ import print_function, division, absolute_import, unicode_literals

import sys
import ast
from pprint import pprint
from inspect import getsource

from python_fcmp import operator
from python_fcmp import function
from .statement import Stmt
from .error import assert_fcmp_error, FCMPParserError
from .decorator import unsupport_op_order


class FCMPParser(ast.NodeVisitor):
    """
    FCMPParser
    The class is used for parsing Python and convert it to FCMP code

    Returns
    -------
    :class:`Model`

    """
    _binop_maker = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.BitOr: operator.or_,
        ast.BitAnd: operator.and_,
        ast.BitXor: operator.xor,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.And: operator._and,
        ast.Or: operator._or,
        ast.Pow: operator.pow
    }

    _unaryop_maker = {
        ast.USub: operator.neg,
        ast.Not: operator.not_
    }

    _callop_maker = {
        'cast_array': function.cast_array,
        'out_args': function.out_args,
        'range': function.range,
        'len': function.len_,
        'max': function.max_,
        'min': function.min_,
        'mean': function.mean_,
        'pow': function.pow_,
        'sum': function.sum_,
        'int': function.int_,
        'abs': function.abs_
    }

    def __init__(self):
        self.stmts = []
        self._fcmp_prg = None
        self.func_name = None

    def visit_Module(self, node):
        assert_fcmp_error(len(node.body) == 1, "Only one-function source code will be fed to this parser!")
        return self.visit(node.body[0])

    def visit_FunctionDef(self, node):
        if self.func_name is None:
            self.func_name = node.name
        # lst = [self.visit(stmt) for stmt in node.body]
        _attr = 'id' if sys.version_info[0] < 3 else 'arg'  # To make py2 and 3 compatible

        args = [getattr(arg, _attr) for arg in node.args.args]

        # decorator to declare argument data type
        str_out_args = ''
        for dc in node.decorator_list:
            if dc.func.id == 'cast_array':
                ret = self.visit(dc)
                for r in ret:
                    args[args.index(r[:-3])] = r
                    # args = args.replace(r[:-3], r)

            if dc.func.id == 'out_args':
                str_out_args = self.visit(dc)

        args = ', '.join(args)
        stmt = Stmt('function {}({});{}'.format(self.func_name, args, str_out_args),
                    node.lineno,
                    node.col_offset)
        self.stmts.append(stmt)
        for i in range(len(node.body)):
            self.visit(node.body[i])
        # endsub
        self.stmts.append(Stmt('endsub;',
                               -1,
                               node.col_offset
                               )
                          )

    def visit_Expr(self, node):
        ret = self.visit(node.value)
        self.stmts.append(Stmt(ret + ';',
                               node.lineno,
                               node.col_offset)
                          )

    def visit_Assign(self, node):
        # assign which concatenate all string together
        rhs = self.visit(node.value)
        assert_fcmp_error(len(node.targets) == 1, "So far only one valued assignment is supported!")
        lhs = node.targets[0]
        lhs = self.visit(lhs)
        stmt = Stmt('{} = {};'.format(lhs, rhs),
                    node.lineno,
                    node.col_offset
                    )
        self.stmts.append(stmt)

    def visit_Name(self, node):
        return node.id

    @unsupport_op_order
    def visit_BinOp(self, node):
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        return FCMPParser._binop_maker[type(node.op)](lhs, rhs)

    @unsupport_op_order
    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        return FCMPParser._unaryop_maker[type(node.op)](operand)

    def visit_If(self, node):
        cond = self.visit(node.test)
        # put cond into if statement
        self.stmts.append(Stmt('if {} then do;'.format(cond.prg),
                               node.lineno,
                               node.col_offset
                               )
                          )

        # Return no IfThenElse if proven
        # if isinstance(cond, _expr.UIntImm):
        #     if cond.value:
        #         return visit_list_to_block(self.visit, node.body)
        #     if node.orelse:
        #         return visit_list_to_block(self.visit, node.orelse)
        #     return util.make_nop()

        # if_body = visit_list_to_block(self.visit, node.body)
        for i in range(len(node.body)):
            self.visit(node.body[i])

        self.stmts.append(Stmt('end;',
                               -1,
                               node.col_offset
                               )
                          )

        if len(node.orelse) > 0:
            if isinstance(node.orelse[0], ast.If):
                self.stmts.append(Stmt('else ',
                                       node.orelse[0].lineno,
                                       node.col_offset
                                       )
                                  )
                for i in range(len(node.orelse)):
                    self.visit(node.orelse[i])
                self.stmts.append(Stmt('end;',
                                       -1,
                                       node.col_offset
                                       )
                                  )
            else:
                self.stmts.append(Stmt('else do;',
                                       node.lineno,
                                       node.col_offset
                                       )
                                  )
                for i in range(len(node.orelse)):
                    self.visit(node.orelse[i])
                self.stmts.append(Stmt('end;',
                                       -1,
                                       node.col_offset
                                       )
                                  )

    @unsupport_op_order
    def visit_Compare(self, node):
        ops = [self.visit(node.left)]
        ops += [self.visit(i) for i in node.comparators]
        res = []
        for i in range(len(node.ops)):
            lhs = ops[i]
            rhs = ops[i + 1]
            res.append(FCMPParser._binop_maker[type(node.ops[i])](lhs, rhs))
        if len(res) == 1:
            return Stmt(res[0],
                        node.lineno,
                        node.col_offset
                        )
        ret = FCMPParser._binop_maker[ast.And](res[0], res[1])
        for i in range(2, len(res)):
            ret = FCMPParser._binop_maker[ast.And](ret, res[i])

        return Stmt(ret,
                    node.lineno,
                    node.col_offset
                    )

    @unsupport_op_order
    def visit_BoolOp(self, node):
        # n = len(node.values)
        # if n == 1:
        #     return operator.not_(self.visit(node.values[0]))
        assert_fcmp_error(isinstance(node.op, (ast.And, ast.Or)), "Binary is supposed to be either and or or!")
        values = [self.visit(i).prg for i in node.values]
        return Stmt(FCMPParser._binop_maker[type(node.op)](*values),
                    node.lineno,
                    node.col_offset
                    )

    def visit_Num(self, node):
        return node.n

    def visit_Str(self, node):
        return node.s

    def visit_List(self, node):
        # raise FCMPParserError("List is not supported to be parsed.")
        items = [str(self.visit(i)) for i in node.elts]
        return '[{}]'.format(', '.join(items))

    def visit_Subscript(self, node):
        # should return a string
        args = self.visit(node.slice)
        arr = self.visit(node.value)
        return '{}[{}]'.format(arr, args)

    def visit_Index(self, node):
        if isinstance(node.value, ast.Tuple):
            # return self.visit(node.value)
            raise FCMPParserError("Multiple index doesn't support")
        # FCMP index starting from 1
        ret = self.visit(node.value)
        try:
            return str(int(ret) + 1)
        except ValueError:
            return '{} + {}'.format(ret, '1')

    @unsupport_op_order
    def visit_Call(self, node):
        # Yet, no function pointer supported
        assert_fcmp_error(isinstance(node.func, ast.Name),
                          "Only id-function function call is supported so far!")
        func_id = node.func.id
        args = [self.visit(i) for i in node.args]
        return FCMPParser._callop_maker[func_id](args)  # 1 to 10

    def visit_For(self, node):
        # for i in range() or for i in list/array

        # node.iter should return a string
        ret_str = self.visit(node.iter)
        assert_fcmp_error(isinstance(node.target, ast.Name),
                          "The loop iterator should be a variable!")

        _name = node.target.id  # target do i=1 to 10
        self.stmts.append(Stmt('do {} = {}'.format(_name, ret_str),
                               node.lineno,
                               node.col_offset)
                          )

        for i in range(len(node.body)):
            self.visit(node.body[i])

        self.stmts.append(Stmt('end;',
                               -1,
                               node.col_offset
                               )
                          )

    def visit_Return(self, node):
        val = '' if node.value is None else '({})'.format(self.visit(node.value))
        self.stmts.append(Stmt('return {};'.format(val),
                               node.lineno,
                               node.col_offset
                               )
                          )
    @property
    def fcmp_prg(self):
        # self.stmts = sorted(self.stmts)
        self._fcmp_prg = ''
        pre_lineno = self.stmts[0].lineno
        pre_col_offset = self.stmts[0].col_offset
        for stmt in self.stmts:
            # current line number that is the same as prior line number will append statement after prior statement
            if stmt.lineno == pre_lineno and stmt.col_offset <= pre_col_offset:
                self._fcmp_prg = self._fcmp_prg[:-1] + stmt.prg + '\n'
            else:
                self._fcmp_prg += ' ' * stmt.col_offset
                self._fcmp_prg += stmt.prg
                self._fcmp_prg += '\n'
                pre_lineno = stmt.lineno
        return self._fcmp_prg

    def pretty_print(self):
        pprint(self.fcmp_prg)


def python_to_fcmp(func, print=False):
    """
    Convert Python code to FCMP code

    Parameters
    ----------
    func : function
        Specifies the Python function to be converted
    print : bool, optional
        Whether to pretty print FCMP function
        Default: False

    Returns
    -------
    :class:`Str`

    """
    python_source_code = getsource(func)
    expr = ast.parse(python_source_code)
    parser = FCMPParser()
    parser.visit(expr)
    if print:
        parser.pretty_print()
    return parser.fcmp_prg


def register_fcmp_routines(conn, routine_code, function_tbl_name):
    """
    Register FCMP Routines on CAS

    Parameters
    ----------
    conn : CAS
        Specifies the CAS connection object.
    routine_code : string
        specifies the FCMP code.
    function_tbl_name : string
        Specifies the name of CAS function table.

    """
    if not conn.has_actionset('fcmpact'):
        conn.loadactionset(actionSet = 'fcmpact', _messagelevel = 'error')
    conn.addRoutines(routineCode=routine_code, package = 'pkg', saveTable=1,
                     funcTable=dict(name=function_tbl_name, caslib="casuser", replace=1))

