#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/1
# IDE: PyCharm

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.

    Besides, also, something is better than nothing
    """
    result = {}
    for dictionary in dict_args:
        for k,v in dictionary.items():
            if k in result:
                result[k] = result[k] if result[k] else v
            else:
                result[k] = v
        result.update(dictionary)
    return result