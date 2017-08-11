#!/bin/python
from netCDF4 import Dataset
import numpy as np
import sys, re
import glob, os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-s" , metavar='suffix_name', help="names of suffix file name"        , type=str, nargs=1, required=True)
parser.add_argument("-ij", metavar='index'      , help="i-,j-index of the point to check" , type=int, nargs=2, required=True)

args = parser.parse_args()

csuf = args.s[0]
loc  = args.ij
jloc=int(loc[1]) ; iloc=int(loc[0])

# sort list

file_lst=glob.glob(csuf+"_????.nc")
file_lst.sort()

nfind=0

for file in file_lst:
    ncid = Dataset(file)
    [ibl,jbl]=ncid.DOMAIN_position_first
    if ((ibl<=iloc) and (jbl<=jloc)):
        [itr,jtr]=ncid.DOMAIN_position_last
        # as data comes from ocean output (fortran convention, we add +1
        [ibl,jbl] = np.array([ibl,jbl]) + 1
        [itr,jtr] = np.array([itr,jtr]) + 1
        # get narea (find all number in file)
        narea = re.findall(r'\d+', file)[0]

# check if in the file
        if ((ibl<=iloc<=itr) and (jbl<=jloc<=jtr)):
            nfind += 1
            print ''
            print ' ========================================================'
            print ' point ({},{}) is located on the local domain number: {} '.format(iloc,jloc,narea)
            print ''
            print ' coordinate of the local domain are ({},{}) and ({},{})'.format(ibl,jbl,itr,jtr)
            print ''
            print ' file name : {}_{}.nc'.format(csuf,narea)
            print ' ========================================================'
            print ''
    
    ncid.close()

if (nfind == 0):
    print ' The point ({},{}) is not located on available NEMO subdomain. It may be on a removed land processor '.format(iloc,jloc) 
