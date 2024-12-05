from __future__ import annotations

import re
from typing import Callable, List, Optional, Tuple

class ReTree(object):
    _children: List[ReTree]
    _match: re.Match
    _group_index: int
    _root: ReTree
    _parent: Optional[ReTree]

    # Used to prevent external code from using __init__
    __unique_key = object()

    def __init__(self, unique_key: object, group_index: int, parent: Optional[ReTree]=None, match: Optional[re.Match]=None) -> None:

        # Prevent external use of __init__
        assert(unique_key is ReTree.__unique_key), \
             'ReTree\'s cannot be constructed with default constructor/initializer. Please use TODO'

        has_parent = parent is not None
        is_root = match is not None
        assert(has_parent is not is_root), \
            'Must specify exactly one of either "parent" (if a child node) or "match" (if the root node)'

        self._children = []
        self._group_index = group_index
        if parent is not None:
            self._match = parent.match
            self._root = parent.root
            self._parent = parent
        elif match is not None:
            self._match = match
            self._parent = None
            self._root = self

    @classmethod
    def from_match(cls, match: Optional[re.Match]) -> Optional[ReTree]:
        """Converts a regex match object into a regex match tree."""
        if match is None:
            return None
        root = cls(cls.__unique_key, 0, match=match)

        lastindex = len(match.groups())

        for group_index in range(1, lastindex + 1):
            root._add(group_index)
        return root

    @classmethod
    def pattern_match(cls, pattern: re.Pattern, text: str) -> Optional[ReTree]:
        """
        Tests if string matches pattern and returns results as regex match tree.
        """
        match = pattern.match(text)
        if match:
            return cls.from_match(match)
        else:
            return None

    def __str__(self) -> str:
        return self.text

    @property
    def children(self) -> List[ReTree]:
        return self._children

    @property
    def match(self) -> re.Match:
        return self._match

    @property
    def index(self) -> int:
        return self._group_index

    @property
    def parent(self) -> Optional[ReTree]:
        return self._parent

    @property
    def root(self) -> ReTree:
        return self._root

    @property
    def span(self) -> Tuple[int, int]:
        return self._match.span(self._group_index)

    @property
    def text(self) -> str:
        return self._match.group(self._group_index)

    def is_root(self) -> bool:
        return self.root == self

    def has_children(self) -> bool:
        return len(self._children) > 0

    def get_depth(self) -> int:
        if not self.has_children():
            return 1
        depths = [(c.get_depth() + 1) for c in self.children]
        return max(depths)

    def do_for_all(self, func: Callable[[ReTree],None]) -> None:
        func(self)
        for c in self.children:
            c.do_for_all(func)

    def display(self, show_index: bool=False) -> None:
        rtd = ReTreeDisplay()
        rtd.print_tree(self, show_index=show_index)

    def _add(self, group_index: int) -> bool:
        """Adds sub-match group to tree. Used in initial construction."""
        # Check that given group index corresponds to subgroup of this group
        if not self._contains_group_index(group_index):
            return False

        # Check if given group is a subgroup of any of this group's children
        added = any([ child._add(group_index) for child in self._children ])

        # If not, then it must be a direct child of this group
        if not added:
            self._add_new_child(group_index)
        return True

    def _add_new_child(self, child_index: int) -> ReTree:
        """Creates new child node and appends to this group's children."""
        child = ReTree(ReTree.__unique_key, child_index, parent=self)
        self._children.append(child)
        return child

    def _contains_group_index(self, group_index: int) -> bool:
        """Checks if match group with given index is within this match group."""
        span1 = self.span
        span2 = self.match.span(group_index)
        return span1[0] <= span2[0] and span1[1] >= span2[1]



class ReTreeDisplay(object):

    def get_index_fmt(self, node: ReTree) -> int:
        return len(str(node.match.lastindex))

    def print_tree(self, node: ReTree, indent: str='', show_index: bool=False) -> None:
        if show_index:
            index_fmt = '%-' + str(self.get_index_fmt(node) + 1) + 'd'
            index_str = index_fmt % node.index
            print('%s%-s%-s' % (index_str, indent, node.text))
        else:
            print('%-s%-s' % (indent, node.text))
        for c in node.children:
            self.print_tree(c, indent=indent + '  ', show_index=show_index)
