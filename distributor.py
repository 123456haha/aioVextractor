#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/2
# IDE: PyCharm

from extractor import *

def distribute(webpage_url):
    """
    Search for the suitable existed InfoExtractor

    :return:
    Extractor: An instance of Extractor if suitable InfoExtractor existed
    str: "No suitable InfoExtractor is provided" if no suitable InfoExtractor
    """
    for ie in gen_extractor_classes():
        if ie.suitable(webpage_url):
            return ie
        else:
            continue
    else:
        return "No suitable InfoExtractor is provided"


if __name__ == '__main__':
    pass
