#! /usr/bin/env python
# Program to modify a NetCDF file

import netCDF4 as nc
import numpy as np

filename='/work/ag22216/mfs_efs1_20200909_20200909_s_T.nc'
ncfile = nc.Dataset(filename,'r+')
nav_lat = ncfile.variables['nav_lat'][:]
nav_latn= np.ones((nav_lat.shape[0],nav_lat.shape[1]))
nav_latp= np.ones((nav_lat.shape[1]))
nav_latp[:]= 46.
nav_latn[0:252,:]=nav_lat[1:,:]
nav_latn[252,:]=nav_latp[:]
ncfile.variables['nav_lat'][:] = nav_latn
ncfile.close()
