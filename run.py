#!/usr/bin/env python

from os.path import dirname, join
import os
import sys
import subprocess

src_dir = os.path.abspath(dirname(__file__))

os.environ['PATH'] = join(src_dir, 'avl', 'bin') + os.pathsep + os.environ['PATH']

if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] = src_dir + os.pathsep + os.environ['PYTHONPATH']
else:
    os.environ['PYTHONPATH'] = src_dir

os.environ['ETS_TOOLKIT'] = 'wx'

proc = subprocess.Popen([sys.executable, join(src_dir, 'pyavl', 'ui', 'envisage', 'run.py')])

proc.wait()

