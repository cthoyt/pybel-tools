# -*- coding: utf-8 -*-

"""Types for filters."""

import warnings

from pybel.struct.filters.typing import EdgeIterator, EdgePredicate, EdgePredicates, NodePredicate, NodePredicates
from pybel.typing import Strings

__all__ = [
    'NodePredicate',
    'NodePredicates',
    'EdgeIterator',
    'EdgePredicate',
    'EdgePredicates',
    'Strings',
]

warnings.warn('pybel_tools.filters.typing has been moved to pybel.struct.filters.typing')
