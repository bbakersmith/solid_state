from dataclasses import dataclass
from typing import Optional

import parsimonious


grammar = parsimonious.Grammar(
    r"""
        query = path+
        path = (term+) path_separator?
        term = (term_pair / obj_name / state_name) term_separator?

        term_pair = obj_name state_name
        state_name = state_indicator name
        obj_name = ~"[A-Za-z0-9_-]+"
        name = ~"[A-Za-z0-9_-]+"
        path_separator = "," " "?
        term_separator = " "
        state_indicator = "."
    """
)


@dataclass
class Term:
    obj_name: Optional[str] = None
    state_name: Optional[str] = None


@dataclass
class Path:
    terms: list[Term]


@dataclass
class Query:
    paths: list[Path]


class Visitor(parsimonious.NodeVisitor):
    def visit_query(self, node, visited_children):
        return Query(visited_children)

    def visit_path(self, node, visited_children):
        return Path(visited_children[0])

    def visit_term(self, node, visited_children):
        return Term(**visited_children[0][0])

    def visit_term_pair(self, node, visited_children):
        return {**visited_children[0], **visited_children[1]}

    def visit_state_name(self, node, visited_children):
        return dict(state_name=visited_children[1])

    def visit_obj_name(self, node, visited_children):
        return dict(obj_name=node.text)

    def visit_name(self, node, visited_children):
        return node.text

    def generic_visit(self, node, visited_children):
        return visited_children or node


def parse(query):
    return Visitor().visit(grammar.parse(query))
