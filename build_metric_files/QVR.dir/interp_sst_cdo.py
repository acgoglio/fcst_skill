#!/usr/bin/env python

import sys
from netCDF4 import Dataset
import numpy as np
from copy import copy, deepcopy
from SeaOverLand import  seaoverland


argv=sys.argv
var='votemper'
nc_file = argv[1]
fh = Dataset(nc_file, mode='r')
olon = fh.variables['nav_lon'][:] 
olat = fh.variables['nav_lat'][:]
dep = fh.variables['deptht'][:]
tim = fh.variables['time_counter'][:]
temp = fh.variables[var][:]
#unit = fh.variables[var].units
fh.close()

flt = Dataset('MFS_24_y_mdt_final_full.nc', mode='r')
lon = flt.variables['lon'][:]
lat = flt.variables['lat'][:]
flt.close()

temp2=np.squeeze(temp[0,0,:,:])
fill=float(0)
temp2[temp2>1e10]=fill
#temp2[np.where(np.isnan(temp2))]=fill

lat=np.squeeze(lat[:,0])
lon=np.squeeze(lon[0,:])


fs=Dataset('sample_sst.nc','r')
lon_sst=fs.variables['lon'][:]
lat_sst=fs.variables['lat'][:]
fs.close()

lonsst,latsst=np.meshgrid(lon_sst,lat_sst)

mask = (temp2 == fill) 

temp2 = np.ma.MaskedArray(temp2,  mask=mask)
temp_sol=seaoverland(temp2,150)

f1 = Dataset('test_'+nc_file,'w',format='NETCDF4_CLASSIC')
lat=f1.createDimension('lat',380)
lon=f1.createDimension('lon',1307)
nlon=f1.createVariable('nav_lon','f4',('lat','lon'))
nlat=f1.createVariable('nav_lat','f4',('lat','lon'))
nlon[:,:]=olon
nlat[:,:]=olat
sst_int=f1.createVariable('sst_int', 'f4', ('lat', 'lon'))
sst_int[:,:]=temp_sol
f1.close()


