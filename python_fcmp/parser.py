from __future__ import print_function, division, absolute_import, unicode_literals

import sys
import ast
from pprint import pprint
from inspect import getsource

from python_fcmp import operator
from python_fcmp import function
from .statement import Stmt, FCMPStmt
from .error import assert_fcmp_error, FCMPParserError
from .decorator import unsupport_op_call
from .fcmp import EXPLICIT_FUNCTION

LAMBDA_EMPTY_ARGS = ['0']


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
        'abs': function.abs_,
        # 'compute': function.compute,
        # 'reshape': function.reshape,
        # 'iterator': function.iterator
    }

    def __init__(self):
        self.stmts = []
        self._fcmp_prg = None
        self.func_name = None
        self.variable_dict = dict()  # the dict stores fcmp variable and value

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
        ''' add expr statement in stmts list '''
        ret = self.visit(node.value)
        if type(ret) == str:
            self.stmts.append(Stmt(ret + ';',
                                   node.lineno,
                                   node.col_offset)
                              )
        else:
            self.stmts.append(ret)

    def visit_Assign(self, node):
        ''' add expr statement in stmts list '''
        # assign which concatenate all string together
        rhs = self.visit(node.value)
        assert_fcmp_error(len(node.targets) == 1, "So far only one valued assignment is supported!")
        lhs = node.targets[0]
        lhs = self.visit(lhs)
        # check rhs type
        if type(rhs) is not FCMPStmt:
            self.stmts.append(Stmt('{} = {};'.format(lhs, rhs),
                                   node.lineno,
                                   node.col_offset
                                   ))
        else:
            rhs.ret = lhs
            self.variable_dict[lhs] = rhs
            rhs.lineno = node.lineno
            rhs.col_offset = node.col_offset
            self.stmts.append(rhs)

    def visit_Name(self, node):
        return node.id

    @unsupport_op_call
    def visit_BinOp(self, node):
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        return FCMPParser._binop_maker[type(node.op)](lhs, rhs)

    @unsupport_op_call
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

    @unsupport_op_call
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

    @unsupport_op_call
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
        if isinstance(args, list):
            if arr in self.variable_dict:
                # get the variable's shape which is added into self.variable_dict via fcmp.reshape function
                t_dims = self.variable_dict[arr].args[1]
                # convert multi-dims access to one dimension subscript
                one_dim_subscript = ''
                for i, d in enumerate(t_dims[1:]):
                    if i == 0:
                        one_dim_subscript = operator.mul(d, '({})'.format(args[i]))
                    else:
                        one_dim_subscript = operator.add(one_dim_subscript, operator.mul(d, '({})'.format(args[i])))
                one_dim_subscript = operator.add(one_dim_subscript, '({})'.format(args[-1]))
                return '{}[{}]'.format(arr, one_dim_subscript)
            else:
                raise FCMPParserError("Please first reshape {} "
                                      "and then access the elements of it like multiple dimensions".format(arr))
                # return '{}[{}]'.format(arr, ', '.join(args))
        else:
            return '{}[{}]'.format(arr, args)

    def visit_Index(self, node):
        # if isinstance(node.value, ast.Tuple):
        #     # return self.visit(node.value)
        #     raise FCMPParserError("Multiple index doesn't support")
        # FCMP index starting from 1
        idx = self.visit(node.value)
        if not isinstance(node.value, ast.Tuple):
            idx = [idx]
        ret = []
        for i in range(len(idx)):
            try:
                ret.append(str(int(idx[i]) + 1))
            except ValueError:
                ret.append('{} + {}'.format(idx[i], '1'))
        return ret[0] if len(ret) == 1 else ret

    @unsupport_op_call
    def visit_Call(self, node):
        # Only support fcmp function pointer
        if isinstance(node.func, ast.Attribute):
            f_name = self.visit(node.func)
            args = []
            for n in node.args:
                # check if there are any fcmp function variable in the node.args
                # if the arg is a list
                if type(n) == ast.List:
                    arg = self.visit(n)  # string
                    arg = arg[1:-1].split(', ')
                    # remap variable
                    tmp = []
                    for a in arg:
                        if a in self.variable_dict:
                            tmp.append(tuple((a, self.variable_dict[a])))
                        else:
                            tmp.append(a)
                    args.append(tmp)
                # if the arg is a variable
                else:
                    arg = self.visit(n)
                    if arg in self.variable_dict:
                        args.append(tuple((arg, self.variable_dict[arg])))
                    else:
                        args.append(arg)

            # return FCMPStmt which store rich info
            return FCMPStmt(f_name, args, None, node.lineno, node.col_offset)
        else:  # non function pointer call
            assert_fcmp_error(isinstance(node.func, ast.Name),
                              "Only id-function function or FCMP call is supported so far!")
            func_id = node.func.id
            args = [self.visit(i) for i in node.args]
            return FCMPParser._callop_maker[func_id](args)  # return a string

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
        # for end statement
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

    def visit_Attribute(self, node):
        buf = self.visit(node.value)
        assert_fcmp_error(buf == 'fcmp',
                          "Only FCMP call is supported so far!")

        return node.attr  # return fcmp function name

    def visit_Lambda(self, node):
        _attr = 'id' if sys.version_info[0] < 3 else 'arg'  # To make py2 and 3 compatible
        args = [getattr(arg, _attr) for arg in node.args.args]  # put into body as variables
        if len(args) == 0:
            # place holder for no argument passed
            args = [LAMBDA_EMPTY_ARGS]
        else:
            args = [args]
        # below should be put into iteration body
        # eg # lhs = fcmp.compute((shape,), lambda i: fcmp.sum(A[i, k], axis=k)
        # do i = 0 to shape by 1;
        #   do k_i = 0 to k by 1;
        #       lhs[i] = lhs[i] + A[i, k_i]
        # lambda doesn't need shape
        # ret = []  # what should be stored, string or FCMPStmt
        # for i in range(len(node.body)):
        #     ret.append(self.visit(node.body[i]))
        f_stmt = self.visit(node.body)
        if isinstance(f_stmt, str):
            # lambda function doesn't include any fcmp function
            pure_lambda_stmt = FCMPStmt('lambda_', args + [f_stmt], None, node.lineno, node.col_offset)
            # dummy_f_stmt.prg = f_stmt
            return pure_lambda_stmt
        # adding lambda arguments into FCMPStmt's args
        f_stmt.args = args + f_stmt.args if isinstance(f_stmt.args, list) else [f_stmt.args]
        return f_stmt

    def visit_Tuple(self, node):
        return tuple(self.visit(i) for i in node.elts)

    @property
    def fcmp_prg(self):
        # self.stmts = sorted(self.stmts)
        self._fcmp_prg = ''
        pre_lineno = self.stmts[0].lineno
        pre_col_offset = self.stmts[0].col_offset
        for stmt in self.stmts:
            if type(stmt) is FCMPStmt:
                if stmt.func not in EXPLICIT_FUNCTION:
                    continue
            # current line number that is the same as prior line number will append statement after prior statement
            if stmt.lineno == pre_lineno and stmt.col_offset <= pre_col_offset:
                self._fcmp_prg = self._fcmp_prg[:-1] + stmt.prg + '\n'
            else:
                self._fcmp_prg += ' ' * stmt.col_offset
                code = stmt.prg
                if code.count('\n') > 1:
                    code = code.replace('\n', '\n' + ' ' * stmt.col_offset)[: -len(' ' * stmt.col_offset)]
                self._fcmp_prg += code
                self._fcmp_prg += '\n'
                pre_lineno = stmt.lineno
        return self._fcmp_prg

    def pretty_print(self):
        pprint(self.fcmp_prg, width=200)


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
                     funcTable=dict(name=function_tbl_name, replace=1))

