'''
# script to check if 2 netcdf file are the same include report on
# variable, dimension, attributes name and value
# wrote by P. Mathiot 10/2018
'''

from __future__ import print_function
import argparse
import sys
import numpy as np
import netCDF4 as nc

def print_progress(itsk, ntsk):
    """
    print a task progress bar
    Argumments: current task number and total task number
    """
    ctxt = ' '*int(100.0/ntsk*(ntsk-itsk))
    print('|{:=>100}|'.format(ctxt), end='\r')
    sys.stdout.flush()

def list_intersection(lst1, lst2):
    """
    compute the intersection of list

    Arguments: 2 lists (not sure it works for list of object)
    Return: list with the list intersection
    """

    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def list_symmetricdiff(lst1, lst2):
    """
    compute the symmetric difference from list

    Arguments: 2 lists (not sure it works for list of object)
    Return: list with the symmetric difference
    """

    lst3 = [el for el in lst1+lst2 if el not in lst1 or el not in lst2]
    return lst3

def check_attlist(dict1, dict2, ctxt):
    """
    compute keys which are in one dictionnary but not in the other
    and display the selected item

    Arguments:
    arg1, arg2 : dictionary1
    arg3       : txt to personalise the print

    Return:
    integer 0/1: 0 = the 2 dictionary keys are the same
                 1 = the 2 dictionary keys are different
    """

    # python set and intersection are not used to keep order
    lstdiff = list_symmetricdiff(dict1.keys(), dict2.keys())
    nerror = 0
    if lstdiff != []:
        print('\n  WARNING {:<20} list are different.'.format(ctxt))
        print('          {:<20} listed below are only in one of the files (no check on these):'.format(ctxt))
        print('          '+', '.join(['{:<15}'.format(att) for att in lstdiff]), end='')
        nerror = 1
    add_whiteline(nerror)

def check_attvalue(dict1, dict2, ctxt):
    """
    check value for common keys in 2 dictionnary
    and display the differences if there is some

    Arguments:
    arg1, arg2 : dictionary1
    arg3       : txt to personalise the print
    """

    # I am not using 'set' as it is much easier to keep the order when going through the print
    # same order as in ncdump
    lstequa = list_intersection(dict1.keys(), dict2.keys())
    nerror = 0
    if lstequa != []:
        for att in lstequa:
            if dict1[att] != dict2[att]:
                print('\n  WARNING {} {:<20} have different value: {:<40} | {:<40}        (file1 val. | file2 val.)' \
                    .format(ctxt, att, str(dict1[att]), str(dict2[att])), end='')
                nerror = 1
    add_whiteline(nerror)

def check_dimvalue(dict1, dict2, ctxt):
    """
    check value for common nc dimesions dictionnary
    and display the differences if there is some

    Arguments:
    arg1, arg2 : nc dimension dictionary1
    arg3       : txt to personalise the print
    """

    # I am not using set as it is much easier to keep the order when going through the print
    # same order as ncdump
    lstequa = list_intersection(dict1.keys(), dict2.keys())
    nerror = 0
    if lstequa != set():
        for att in lstequa:
            if len(dict1[att]) != len(dict2[att]):
                print('\n  WARNING {} {:<15} have different size: {: 4d} | {: 4d}         (file1 val. | file2 val.)' \
                    .format(ctxt, att, len(dict1[att]), len(dict2[att])), end='')
                nerror = 1
    add_whiteline(nerror)

def check_attlistandvalue(dict1, dict2, ctxt):
    '''
    check atrributes and value
    Method: run check_attlist and check_attvalue
    '''
    check_attlist(dict1, dict2, ctxt)
    check_attvalue(dict1, dict2, ctxt)

def add_whiteline(nerror):
    '''
    add empty line if nerror is not 0
    '''

    if nerror != 0:
        print()

def main():
    '''
    check if 2 nc files are exactly the same.
    check include details on variable, dimension, attribute name and value + nc4 attributes
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", metavar='file_list', help="input file name", type=str, nargs=2, required=True)
    parser.add_argument("-v", metavar='variable_list', help="variable name liste to check", type=str, nargs="+")
    parser.add_argument("--ncatt", help="check netcdf attribute as deflation, chunksize ...", action='store_true')

    args = parser.parse_args()

    cfile1 = args.f[0]
    cfile2 = args.f[1]
    lncatt = args.ncatt

    nc1 = nc.Dataset(cfile1)
    nc2 = nc.Dataset(cfile2)

    print()
    print('dimension checks ...')
    check_attlist(nc1.dimensions, nc2.dimensions, 'dimensions')
    check_dimvalue(nc1.dimensions, nc2.dimensions, 'dimensions')
    print()

    print('global attribute check ...')
    nc1glo_dic = nc1.__dict__
    nc2glo_dic = nc2.__dict__
    check_attlistandvalue(nc1glo_dic, nc2glo_dic, 'global')
    print()

    print('variable name check ...')
    if args.v:
        varlst = args.v
    else:
        check_attlist(nc1.variables, nc2.variables, 'variables')
    print()

    print('variable attribute check ...')
    varlst = list_intersection(nc1.variables.keys(), nc2.variables.keys())
    for ivar, name in enumerate(varlst, 1):

        print_progress(ivar, len(varlst))

        nc1var_dic = nc1.variables[name].__dict__
        if lncatt:
            nc1var_dic['_ChunkSizes'] = nc1.variables[name].chunking()
            nc1var_dic['_Endianness'] = nc1.variables[name].endian()
            nc1var_dic.update(nc1.variables[name].filters())

        nc2var_dic = nc2.variables[name].__dict__
        if lncatt:
            nc2var_dic['_ChunkSizes'] = nc2.variables[name].chunking()
            nc2var_dic['_Endianness'] = nc2.variables[name].endian()
            nc2var_dic.update(nc2.variables[name].filters())

        check_attlistandvalue(nc1var_dic, nc2var_dic, '{:<12} att'.format(name))

    print('\n')
    print('variable data check ...')
    for ivar, name in enumerate(varlst, 1):

        print_progress(ivar, len(varlst))
        data1 = nc1.variables[name][...]
        data2 = nc2.variables[name][...]
        if not np.array_equal(data1, data2):
            print('\n WARNING {:<15} data are different'.format(name))
            data_diff = data1 - data2
            idx_max = np.unravel_index(np.argmax(data_diff), data_diff.shape)
            idx_min = np.unravel_index(np.argmin(data_diff), data_diff.shape)
            print('max (idx, diff, data1, data2) : {}, {}, {}, {}'.format(idx_max, data_diff[idx_max], data1[idx_max], data2[idx_max])) 
            print('min (idx, diff, data1, data2) : {}, {}, {}, {}'.format(idx_min, data_diff[idx_min], data1[idx_min], data2[idx_min]))
            print()
    print('\n')

if __name__ == '__main__':
    main()
