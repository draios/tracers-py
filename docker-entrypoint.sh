#!/bin/sh
rm -fr __pycache__/
py.test $* test.py 
