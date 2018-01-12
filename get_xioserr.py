#!/bin/python
# author: Pierre mathiot (09/2017)

import glob, os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s" , metavar='suffix_name', help="names of suffix file name (xios error file)", type=str, nargs=1, required=True)
    args = parser.parse_args()
    
    csuf = args.s[0]
    
    # sort list
    file_lst=glob.glob(csuf+"_????.err")
    file_lst.sort()
    
    nfind=0
    for filename in file_lst:
        if (os.stat(filename).st_size != 0):
            print ''
            print ' ========================================================'
            print ' file name : {} contain an error'.format(filename) 
            print ' ========================================================'
            print ''
            with open(filename, 'rb') as file:
                for line in file:
                    print line,
    
            nfind=nfind+1
        
    if (nfind == 0):
        print ''
        print ' There no error in the xios error file '+csuf+'_????.nc'
        print ''
    
if __name__ == '__main__':
    main()
