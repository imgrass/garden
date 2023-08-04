from lark import Lark, Transformer, v_args
from lark.lexer import Token
from lark.tree import Tree
from textwrap import dedent
import json


class DemoTransformer(Transformer):

    def _get_import(self, tree: Tree) -> dict:
        path = []
        class_name = None

        for arg in tree.children:
            if isinstance(arg, Token):
                if arg.value[0] != ' ':
                    path.append(arg.value)
            elif isinstance(arg, Tree) and arg.data == 'class_name':
                class_name = arg.children[0].value
            else:
                raise Exception('xxx')

        return {
            'path': '.'.join(path),
            'class': class_name
        }

    def _get_variable_arg(self, argument: Tree) -> dict:
        if len(argument.children) != 1:
            raise Exception('xxx')

        arg: Tree = argument.children[0]
        rule = arg.data

        if rule == 'literal':
            return {
                'type': 'literal',
                'content': arg.children[0].value
                    }
        elif rule == 'variable':
            return {
                'type': 'variable',
                'content': arg.children[0].value
            }
        else:
            raise Exception('...')

    def _get_function_argument(self, argument: Tree) -> dict:
        if len(argument.children) != 1:
            raise Exception('xxxx')

        arg = argument.children[0]

        if isinstance(arg, Tree):
            arg: Tree
            if arg.data == 'formal_var':
                return {
                    'type': 'variable',
                    'content': self._get_variable_arg(arg)
                }
            else:
                raise Exception('xxx')
        elif isinstance(arg, Token):
            arg: Token
            return {
                'type': 'placeholder',
                'content': arg.value
            }
        else:
            raise Exception('xxx')

    def _get_function(self, function: Tree) -> dict:
        func_name = None
        arguments = []

        for child in function.children:
            if isinstance(child, Token):
                child: Token
                if child.type != 'WS_INLINE':
                    raise Exception('xxxx')
                continue

            child: Tree
            rule = child.data
            if rule == 'func_name':
                func_name = child.children[0].value
            elif rule == 'argument':
                arguments.append(self._get_function_argument(child))
            else:
                raise Exception('xxxx')

        return {
            'name': func_name,
            'arguments': arguments
        }

    def _get_sub_func(self, sub_func: Tree) -> dict:
        sub_func_name_tree: Token = sub_func.children[0]
        if sub_func_name_tree.type != 'CNAME':
            raise Exception('xxx')
        sub_func_name = sub_func_name_tree.value

        arguments = []

        for child in sub_func.children[1:]:
            if isinstance(child, Token):
                child: Token
                if child.type != 'WS_INLINE':
                    raise Exception('xxx')
                continue

            child: Tree
            rule = child.data
            if rule != 'argument':
                raise Exception('xxx')

            arguments.append(self._get_function_argument(child))

        return {
            'name': sub_func_name,
            'arguments': arguments
        }

    def _get_function_group(self, function_group: Tree) -> dict:
        children = []

        func_name_tree: Tree = function_group.children[0]
        if func_name_tree.data != 'func_name':
            raise Exception('xxx')
        func_name = func_name_tree.children[0].value

        for child in function_group.children[1:]:
            if isinstance(child, Token):
                child: Token
                if child.type not in ('WS_INLINE', 'NEWLINE'):
                    raise Exception('xxxx')
                continue

            child: Tree
            rule = child.data
            if rule != 'sub_func':
                raise Exception('xxx')

            children.append(self._get_sub_func(child))

        return {
            'name': func_name,
            'children': children
        }

    def _get_assignment(self, assignment: Tree) -> dict:
        variable = None
        value = []

        variable_tree: Tree = assignment.children[0]
        if variable_tree.data != 'variable':
            raise Exception('xxx')

        variable = variable_tree.children[0].value

        for child in assignment.children[1:]:
            if isinstance(child, Token):
                child: Token
                if child.type not in ('WS_INLINE', 'NEWLINE'):
                    raise Exception('xxx')
                continue

            child: Tree
            if child.data != 'assign_value':
                raise Exception('xxx')

            variable_tree: Tree = child.children[0]
            if variable_tree.data != 'literal':
                raise Exception('xxx')

            variable_tree: Token = variable_tree.children[0]
            value.append(variable_tree.value)

        return {
            'variable': variable,
            'value': value
        }

    def _get_statements(self, statements: Tree) -> list:
        result = []

        for statement in statements.children:

            if isinstance(statement, Token):
                statement: Token
                if statement.type != 'NEWLINE':
                    raise Exception('xxx')
                continue

            statement: Tree
            rule = statement.data

            if rule != 'statement':
                raise Exception('xxxxx')

            if len(statement.children) != 1:
                raise Exception('xxxxxxx')

            cur_statement: Tree = statement.children[0]
            if not isinstance(cur_statement, Tree):
                raise Exception('xxx')

            cur_rule = cur_statement.data
            if cur_rule == 'function':
                result.append({
                    'type': 'function',
                    'content': self._get_function(cur_statement)
                })
            elif cur_rule == 'function_group':
                result.append({
                    'type': 'function_group',
                    'content': self._get_function_group(cur_statement)
                })
            elif cur_rule == 'assignment':
                result.append({
                    'type': 'assignment',
                    'content': self._get_assignment(cur_statement)
                })
            else:
                raise Exception('xxx')

        return result

    @v_args(inline=True)
    def program(self, *args):
        word = []
        name = None
        _import = None
        _statements = None

        for arg in args:
            # if isinstance(arg, Token):
            #     print(f' > ({arg}) => {arg.type} .. {arg.value}')
            # else:
            #     print(f' = ({arg}) => {arg.data.type}')

            if name is None:
                if isinstance(arg, Token):
                    arg: Token
                    if arg.type == 'NEWLINE':
                        name = ''.join(word).strip(' ')
                    else:
                        word.append(arg.value)
                elif isinstance(arg, Tree) and arg.data.value == 'hyphen':
                    word.append('-')
                else:
                    raise Exception('xxx')
            else:
                if isinstance(arg, Token):
                    if arg.type != 'NEWLINE':
                        raise Exception('...')
                elif isinstance(arg, Tree):
                    arg: Tree
                    rule = arg.data.value
                    if rule == 'import':
                        _import = self._get_import(arg)

                    elif rule == 'statements':
                        _statements = self._get_statements(arg)
                else:
                    raise Exception('xxx')

        return {
            'name': name,
            'import': _import,
            'statements': _statements
        }


if __name__ == '__main__':

    grammar = r"""
        program: "Program:" (WS_INLINE? hyphen* CNAME)+ NEWLINE \
                 import NEWLINE \
                 "Begin" NEWLINE \
                 statements \
                 "End" NEWLINE?

        import: "Import:" WS_INLINE (CNAME ".")+ CNAME ":" class_name
        statements: (statement NEWLINE)+
        statement: function
                 | function_group
                 | assignment
        function: func_name (WS_INLINE argument)*
        function_group: func_name WS_INLINE "->" \
                        (NEWLINE sub_func)+ NEWLINE "<-"
        assignment: variable WS_INLINE? "=" assign_value \
                    ("," (WS_INLINE? assign_value | \
                          WS_INLINE? "\\" NEWLINE assign_value))*
                  | variable WS_INLINE? "=" function


        hyphen: "-"
        func_name: /\.[A-Z][-_a-zA-Z0-9]*/
        class_name: CNAME
        sub_func: CNAME (WS_INLINE argument)*
        argument: NUMBER | CNAME | formal_var
        formal_var: "{" literal "}" | "{" variable "}"
        literal: NUMBER | SIGNED_NUMBER | CNAME
        variable: "$" CNAME | "${" CNAME "}"
        assign_value: literal

        %import common.WS_INLINE
        %import common.CNAME
        %import common.UCASE_LETTER
        %import common.LETTER
        %import common.DIGIT
        %import common.NUMBER
        %import common.SIGNED_NUMBER
        %import common.NEWLINE
        %import common.WS

        %ignore WS
    """

    parser = Lark(grammar, start='program', parser='lalr', transformer=DemoTransformer())

    body = r'''
        Program: Insert Red-Black tree
        Import: imgrass_horizon.lib.x:Demo
        Begin
            .Initialize empty tree

            .Insert {1000}
            .Expect ->
                as {root} node
            <-

            .Insert {500}
            .Expect ->
                search {left} branch of {1000}
                as {leaf} node
            <-

            $insert_seq = 1500, 250, 1750, 1250, 125, 65, 2000, 95, 2500, \
                          350, 750, 400, 380

            .Insert {$insert_seq} on left branch 300.1

            .Validate ->
                is valid red black tree
            <-

            .Insert 390
            .Expect ->
                search {left} branch of {1000}
                search {right} branch of {250}
                search {left} branch of {500}
                search {right} branch of {380}
                search {left} branch of {400}
                fixup {black_uncle} {RL}
            <-

        End
    '''

    result = parser.parse(body)
    print(json.dumps(result, indent=4))
