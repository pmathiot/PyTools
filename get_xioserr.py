#!/bin/python
from netCDF4 import Dataset
import numpy as np
import sys, re
import glob, os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-s" , metavar='suffix_name', help="names of suffix file name (xios error file)", type=str, nargs=1, required=True)
args = parser.parse_args()

csuf = args.s[0]

# sort list
file_lst=glob.glob(csuf+"_????.nc")
file_lst.sort()

nfind=0
for filename in file_lst:
    print filename, os.stat(filename).st_size
    if (os.stat(filename).st_size /= 0)
        print ''
        print ' ========================================================'
        print ' file name : filename contain an error'.format(filename) 
        print ' ========================================================'
        print ''
    nfind=nfind+1
    
if (nfind == 0L):
    print ' There no error in the xios error file '+csuf+'_????.nc'
