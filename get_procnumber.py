#!/bin/python
from netCDF4 import Dataset
import numpy as np
import sys, re
import glob, os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-s" , metavar='suffix_name', help="names of suffix file name"        , type=str, nargs=1, required=False)
parser.add_argument("-l" , metavar='layout_name', help="layout file name"                 , type=str, nargs=1, required=False)
parser.add_argument("-ij", metavar='index'      , help="i-,j-index of the point to check" , type=int, nargs=2, required=True)

args = parser.parse_args()

loc  = args.ij
jloc=int(loc[1]) ; iloc=int(loc[0])

nfind=0
# sort list
if args.s:
    csuf = args.s[0]

    file_lst=glob.glob(csuf+"_????.nc")
    file_lst.sort()

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

elif args.l:
    clayout=args.l[0]

    nfid=open(clayout)
    # skip header
    for i in range(3):
       cline=nfid.readline()
#
#    while cline:
    line=nfid.readline()
    while line:
        cline=map(int,line.split())
        narea= cline[0]
        ibl  = cline[7]
        jbl  = cline[8]
        itr  = ibl + cline[1]
        jtr  = jbl + cline[2]
        #
        # check if in the file
        if ((ibl<=iloc<=itr) and (jbl<=jloc<=jtr)):
            nfind += 1
            print ''
            print ' ========================================================'
            print ' point ({},{}) is located on the local domain number: {} '.format(iloc,jloc,narea)
            print ''
            print ' coordinate of the local domain are ({},{}) and ({},{})'.format(ibl,jbl,itr,jtr)
            print ' ========================================================'
            print ''
        line=nfid.readline()
else:
    print ' ERROR: need a -s or -l'

if (nfind == 0):
    print ' The point ({},{}) is not located on available NEMO subdomain. It may be on a removed land processor '.format(iloc,jloc) 
