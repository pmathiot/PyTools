import numpy as np
from netCDF4 import Dataset
import argparse
import sys

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f"  , metavar='file_name'       , help="names of input files" , type=str  , nargs=1, required=True)
    parser.add_argument("-v"  , metavar='var_name'        , help="depth variable"       , type=str  , nargs=1, required=True)
    parser.add_argument("-z"  , metavar='depth of the map', help="depth of the map"     , type=float, nargs=1, required=True)
    args=parser.parse_args()
    return args

def get_k_level(z0, cfile, cvar):
    # open netcdf
    ncid = Dataset(cfile)
    zdep = ncid.variables[cvar][:].squeeze()

    err0=99999.
    for jk in range(0,len(zdep)):
        if np.abs(zdep[jk]-z0) < err0:
            jk0=jk
            err0=np.abs(zdep[jk]-z0)
    print 'the closest level to the requiered depth ('+str(z0)+' m ) is: '+str(jk0)+' ( '+str(zdep[jk0])+' m ) [WARNING PYTHON CONVENTION]'
    return jk0

def main():
    # get arguments
    args=get_arguments() 
    # compute level
    jk  =get_k_level(args.z[0], args.f[0], args.v[0])

if __name__ == '__main__':
    main()
