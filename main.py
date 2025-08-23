"""Main entry point moved top process.txt.

author: Peter Karacsonyi
date:   8/20/2025
"""

import sys

from importlib.machinery import SOURCE_SUFFIXES

SOURCE_SUFFIXES.append('.txt')

sys.path_importer_cache.clear()

import process

process.main()
