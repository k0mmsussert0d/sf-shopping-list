import functools
from typing import Dict


class BaseDataOperationsClass:

    @staticmethod
    def merge_dict(source: Dict, destination: Dict) -> Dict:
        """
        run me with nosetests --with-doctest file.py

        >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
        >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
        >>> BaseDataOperationsClass.merge_dict(b, source) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
        True
        """
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                BaseDataOperationsClass.merge_dict(value, node)
            else:
                destination[key] = value

        return destination

    @staticmethod
    def merge(*dicts: Dict) -> Dict:
        return functools.reduce(BaseDataOperationsClass.merge_dict, dicts)
