"""This module contains mutation operators which replace one
relational operator with another.

For each relational operator we generate a series of classes, one for
each *other* operator. These generated classes mutate nodes by
replaces the first operator with the second.

The generated classes are named `Replace<from-op>With<to-op>` where
`from-op` is the relational operator being replaced and `to-op` is the
replacement operator.

The global list `operators` also contains a all of the generated
classes. This list is primarily used for testing.
"""

import ast

from .operator import Operator


RELATIONAL_OPERATORS = {ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
                        ast.Is, ast.IsNot, ast.In, ast.NotIn}

operators = []

# For each relational operator A, create one class for each *other*
# relational operator B which replaces A with B in an AST.

for from_op in RELATIONAL_OPERATORS:
    for to_op in RELATIONAL_OPERATORS.difference({from_op}):
        operator_name = 'Replace{}With{}'.format(
            from_op.__name__, to_op.__name__)

        visit_func_name = 'visit_{}'.format(from_op.__name__)
        visit_func = lambda self, node: self.visit_mutation_site(node)

        new_op = type(
            operator_name,
            (Operator,),
            {'mutate': lambda self, node: to_op(),
             visit_func_name: visit_func,
             'from_op': from_op,
             '__repr__': lambda self: 'replace {} with {}'.format(
                 from_op.__name__, to_op.__name__)})

        globals()[operator_name] = new_op
        operators.append(new_op)