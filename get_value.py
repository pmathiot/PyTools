#!/usr/local/sci/bin/python2.7

# script to diagnose variable at a single point
# wrote by P. Mathiot 06/2016

import netCDF4 as nc
import numpy as np
import sys, re
import argparse
import glob, os
import matplotlib.pyplot as plt

def main():
    print ""
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f"   , metavar='file_name'        , help="names of input files "             , type=str, nargs="+", required=True)
    parser.add_argument("-ij"  , metavar='index'            , help="i-,j-index of the point to check"  , type=int, nargs=2  , required=True)
    parser.add_argument("-ll"  , metavar='lon/lat_var_name' , help="lon-,lat-variable name"            , type=str, nargs=2  , required=False)
    parser.add_argument("-time", metavar='time_name'        , help="time-variable name"                , type=str, nargs=1  , required=False)
    parser.add_argument("-v"   , metavar='var_name'         , help="variable list"                     , type=str, nargs="+", required=True)
    
    args = parser.parse_args()
    
    loc     = args.ij
    cvar_lst= args.v
    jloc=int(loc[1]) ; iloc=int(loc[0])
    
    cfile_lst=args.f
    if len(cfile_lst) == 1:
        cfile_lst=glob.glob(args.f[0])
        cfile_lst.sort()
    
    nfile=len(args.f)
    nvar =len(args.v)
    
    if nfile == 0:
        print 'E R R O R: get_value need at least one file.'
    
    if nfile == 1:
    
        cfile   = args.f[0]
    
        ncid = nc.Dataset(cfile)
        cvar_out = [cvar for cvar in cvar_lst if cvar not in ncid.variables.keys()]
    
        if cvar_out != []:
            print "E R R O R: "+" ".join(cvar_out),' not in '+cfile
        else:
            ctxtll='' ; ctxttime=''

            if args.ll:
                coord   = args.ll
                cvlon= coord[0]  ; cvlat=coord[1]
                rlon = ncid.variables[cvlon][jloc,iloc]
                rlat = ncid.variables[cvlat][jloc,iloc]
                ctxtll= "(ie lon={0:.3f},lat={1:.3f}) ".format( rlon, rlat)

            if args.time:
                cvtime  = args.time[0]
                rtime = nc.num2date(ncid.variables[cvtime][0].squeeze(), ncid.variables[cvtime].units, "noleap")
                ctxttime= "at time {0} ".format(rtime)

            print ""
            print "check value into file {0} at point i={1} and j={2} {3}{4}:".format(cfile, iloc, jloc, ctxtll, ctxttime)
            print "----------------------------"
            print ""
            for cvar in cvar_lst:
                # get unit
                cunit=''
                if 'units' in ncid.variables[cvar].ncattrs():
                    cunit= ncid.variables[cvar].units
                # do not fill data with missing value
                ncid.variables[cvar].set_auto_maskandscale(False)
                # get dim
                ndim = len(ncid.variables[cvar].dimensions)
                if ndim == 4:
                    data = ncid.variables[cvar][0,:,jloc,iloc]
                    if 1 in data.shape:
                        print "{0:<20s} ({1:>13s}) = ".format(cvar,cunit)+" ".join(["{0:14.6e}".format(rdat) for rdat in np.squeeze(data)])
                    else:
                        print "{0:<20s} ({1:>13s}) = ".format(cvar,cunit)+" ".join(["{0:14.6e}".format(rdat) for rdat in data[0]])
                        for k in range(1, data.shape[0]):    
                            print "{0:<39s}".format('')+" ".join(["{0:14.6e}".format(rdat) for rdat in data[k]])
                if ndim == 3:
                    data = ncid.variables[cvar][  0,jloc,iloc]
                    print "{0:<20s} ({1:>13s}) = {2:14.6e}".format(cvar, cunit, data)
                if ndim == 2:
                    data = ncid.variables[cvar][    jloc,iloc]
                    print "{0:<20s} ({1:>13s}) = {2:14.6e}".format(cvar, cunit, data)
        print ""
        ncid.close()
    
    if nfile > 1:
        nerr = 0
        for cfile in args.f[:]: 
            ncid = nc.Dataset(cfile)
            cvar_out = [cvar for cvar in cvar_lst if cvar not in ncid.variables.keys()]
            if cvar_out != []:
                print "E R R O R: "+" ".join(cvar_out),' not in '+cfile
                nerr += 1
            ncid.close()
        if (nerr > 0):
           sys.exit(666)
    
        data = np.zeros(shape=(nvar,nfile))
        cunit= []
        cname= []
        ndim = np.zeros(nvar)
        ncid = nc.Dataset(args.f[0])
        rlon = ncid.variables[clon][jloc,iloc]
        rlat = ncid.variables[clat][jloc,iloc]
        jvar=-1
        for cvar in cvar_lst:
            jvar+=1
            # fill name and unit vector for plot
            if 'units' in ncid.variables[cvar].ncattrs():
                cunit.append(ncid.variables[cvar].units)
            else:
                cunit.append([''])
            if 'long_name' in ncid.variables[cvar].ncattrs():
                cname.append(ncid.variables[cvar].long_name)
            else:
                cname.append(cvar)
            # fill dimension vector
            ndim [jvar]= len(ncid.variables[cvar].dimensions)
        ncid.close()
        crun=re.split('[._]',args.f[0].split('/')[-1])[0] #get run name (split with / and take the last one and split with special caractere and take the first one
    
        jt = -1
        print "check value at point (i={0},j={1}) or (lon={2:.3f},lat={3:.3f}) into file :".format(iloc, jloc, rlon, rlat)
        for cfile in args.f[:]:
            jt += 1
            print cfile
    
            ncid = nc.Dataset(cfile)
    
            for jvar in range(0,nvar):
                cvar = cvar_lst[jvar]
                ncid.variables[cvar].set_auto_maskandscale(False)
                jdim = ndim[jvar]
                if jdim == 4:
                    print ' E R R O R: case 4d not yet coded for multi file, exit ' 
                    sys.exit(666)
                if jdim == 3:
                    data[jvar,jt] = ncid.variables[cvar][  0,jloc,iloc]
                if jdim == 2:
                    data[jvar,jt] = ncid.variables[cvar][    jloc,iloc]
            ncid.close()
    
        plt.figure(figsize=(8.27,11.69))
        time=[(jt + 0.5)/12 for jt in range(0,nfile)]
        for jvar in range(0,nvar): 
            ax = plt.subplot(nvar,1,jvar+1)
            ax.plot(time[:],data[jvar,:],'-')
            ax.set_title(cname[jvar]+' at '+' ({:.3f},{:.3f}) in {} '.format(rlon, rlat,crun))
            ax.set_ylabel(cunit[jvar])
            ax.grid(True)
        plt.tight_layout()
        plt.savefig(crun+'_'+"_".join(cvar for cvar in cvar_lst)+'.eps', format='eps', dpi=150 )
        plt.show()
        
if __name__ == '__main__':
    main()
