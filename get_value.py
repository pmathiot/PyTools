"""
 script to diagnose variable at a single point
 wrote by P. Mathiot 06/2016
"""

from __future__ import print_function
import sys
import re
import argparse
import glob
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_time(ncid,cvtime,it):
    timeatt_dic = ncid.variables[cvtime].__dict__
    if 'calendar' in timeatt_dic.keys():
        ccal = timeatt_dic['calendar']
    rtime = nc.num2date(ncid.variables[cvtime][it].squeeze(), ncid.variables[cvtime].units, ccal)
    return rtime


def main():
    """
    script to diagnose variable at a single point.
    """
    print()

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", metavar='file_name', help="names of input files", type=str, nargs="+", required=True)
    parser.add_argument("-ij", metavar='index', help="i-,j-index of the point to check", type=int, nargs=2, required=True)
    parser.add_argument("-ll", metavar='lon/lat_var_name', help="lon-,lat-variable name", type=str, nargs=2, required=False)
    parser.add_argument("-time", metavar='time_name', help="time-variable name", type=str, nargs=1, required=False)
    parser.add_argument("-kt", metavar='time_index', help="time-index", type=int, nargs=1  , required=False)
    parser.add_argument("-v", metavar='var_name', help="variable list", type=str, nargs="+", required=True)

    args = parser.parse_args()

    if args.kt:
        it = args.kt[0]
    else:
        it=0

    loc = args.ij
    cvar_lst = args.v
    jloc = int(loc[1])
    iloc = int(loc[0])

    cfile_lst = args.f
    if len(cfile_lst) == 1:
        cfile_lst = glob.glob(args.f[0])
        cfile_lst.sort()

    nfile = len(args.f)
    nvar = len(args.v)

    if nfile == 0:
        print('E R R O R: get_value need at least one file.')
        sys.exit(666)

    ctxtll = ''
    ctxttime = ''
    cfile = args.f[0]
    ncid = nc.Dataset(cfile)

    if args.time:
        rtime = get_time(ncid, args.time[0], it)
        ctxttime = "at time {0} ".format(rtime)

    if args.ll:
        coord   = args.ll
        clon = coord[0]  ; clat=coord[1]
        rlon = ncid.variables[clon][jloc,iloc]
        rlat = ncid.variables[clat][jloc,iloc]
        ctxtll = "(ie lon = {0:.3f}, lat = {1:.3f}) ".format(rlon, rlat)

    if nfile == 1:

        cvar_out = [cvar for cvar in cvar_lst if cvar not in ncid.variables.keys()]

        if cvar_out != []:
            print("E R R O R: "+" ".join(cvar_out), ' not in '+cfile)
            sys.exit(666)
        else:
            print()
            print("check value into file {0} at point i = {1} and j = {2} {3}{4}:".format(cfile, iloc, jloc, ctxtll, ctxttime))
            print("----------------------------")
            print()
            for cvar in cvar_lst:
                # get unit
                cunit = ''
                if 'units' in ncid.variables[cvar].ncattrs():
                    cunit = ncid.variables[cvar].units
                # do not fill data with missing value
                ncid.variables[cvar].set_auto_maskandscale(False)
                # get dim
                ndim = len(ncid.variables[cvar].dimensions)
                if ndim == 4:
                    data = ncid.variables[cvar][it, :, jloc, iloc]
                    if 1 in data.shape:
                        print("{0:<20s} ({1:>13s}) = {2:14.6e}".format(cvar, cunit, data[0]))
                    else:
                        print("{0:<20s} ({1:>13s}) = {2:14.6e}".format(cvar, cunit, data[0]))
                        for k in range(1, data.shape[0]):
                            print("{0:<38s} {1:14.6e}".format('',data[k]))
                if ndim == 3:
                    data = ncid.variables[cvar][0, jloc, iloc]
                    print("{0:<20s} ({1:>13s}) = {2:14.6e}".format(cvar, cunit, data))
                if ndim == 2:
                    data = ncid.variables[cvar][jloc, iloc]
                    print("{0:<20s} ({1:>13s}) = {2:14.6e}".format(cvar, cunit, data))
        print()
        ncid.close()

    if nfile > 1:
        nerr = 0
        for cfile in args.f[:]:
            ncid = nc.Dataset(cfile)
            cvar_out = [cvar for cvar in cvar_lst if cvar not in ncid.variables.keys()]
            if cvar_out != []:
                print("E R R O R: "+" ".join(cvar_out), ' not in '+cfile)
                nerr += 1
            ncid.close()
        if nerr > 0:
            sys.exit(666)

        data = np.zeros(shape=(nvar, nfile))
        cunit = []
        cname = []
        ndim = np.zeros(nvar)
        nt = np.zeros(nfile)
        rtime = [None]*nfile
        
        jvar = -1
        ncid = nc.Dataset(args.f[0])
        for cvar in cvar_lst:
            jvar += 1
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
            ndim[jvar] = len(ncid.variables[cvar].dimensions)
        ncid.close()
#get run name (split with / and take the last one and split with special caractere and take the first one
        crun = re.split('[._]', args.f[0].split('/')[-1])[0]

        print("check value at point (i = {0}, j = {1}) or (lon = {2:.3f}, lat = {3:.3f}) into file :" \
            .format(iloc, jloc, rlon, rlat))
        for jt, cfile in enumerate(args.f):
            print(cfile)

            ncid = nc.Dataset(cfile)

            if args.time:
                rtime[jt] = get_time(ncid, args.time[0], it)._to_real_datetime()
            else:
                rtime = [(ifile + 0.5)/12 for ifile in range(0, nfile)]
            
            # use enumerate for jvar, cvar in enumerate(cvar_lst)
            for jvar, cvar in enumerate(cvar_lst):
                ncid.variables[cvar].set_auto_maskandscale(False)
                jdim = ndim[jvar]
                if jdim == 4:
                    print(' E R R O R: case 4d not yet coded for multi file, exit ')
                    sys.exit(666)
                if jdim == 3:
                    data[jvar, jt] = ncid.variables[cvar][0, jloc, iloc]
                if jdim == 2:
                    data[jvar, jt] = ncid.variables[cvar][jloc, iloc]
            ncid.close()

        plt.figure(figsize=(8.27, 11.69))
        for jvar in range(0, nvar):
            ax = plt.subplot(nvar, 1, jvar+1)
            ax.plot_date(rtime[:], data[jvar, :], '-')
            ax.set_title(cname[jvar]+' at '+' ({:.3f}, {:.3f}) in {} '.format(rlon, rlat, crun))
            ax.set_ylabel(cunit[jvar])
            ax.grid(True)

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
            plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig(crun+'_'+"_".join(cvar for cvar in cvar_lst)+'.eps', format='eps', dpi=150)
        plt.show()

if __name__ == '__main__':
    main()
