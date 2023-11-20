#!/usr/bin/env python

import sys
from netCDF4 import Dataset
import numpy as np
from copy import copy, deepcopy
from SeaOverLand import  seaoverland
from mpl_toolkits import basemap 


argv=sys.argv
var='votemper'
nc_file = argv[1]
fh = Dataset(nc_file, mode='r')
# dopo la ridistribuzione dei processori a partire dalla simu_v16, nav_lon e nav_lat sono incompleti
#lon = fh.variables['nav_lon'][:] 
#lat = fh.variables['nav_lat'][:]
dep = fh.variables['deptht'][:]
tim = fh.variables['time_counter'][:]
temp = fh.variables[var][:]
unit = fh.variables[var].units
#fill = fh.variables[var]._FillValue
fh.close()

flt = Dataset('MFS_24_y_mdt_final_full.nc', mode='r')
lon = flt.variables['lon'][:]
lat = flt.variables['lat'][:]
flt.close()

temp2=np.squeeze(temp[0,0,:,:])
fill=float(0)
temp2[temp2>1e10]=fill

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

temp_int=basemap.interp(temp_sol,lon,lat,lonsst,latsst,checkbounds=False, masked=False, order=1)

aa=np.shape(temp_int)

f1 = Dataset('int_'+nc_file,'w',format='NETCDF4_CLASSIC')
lat=f1.createDimension('lat',aa[0])
lon=f1.createDimension('lon',aa[1])
nlon=f1.createVariable('nav_lon','f4',('lat','lon'))
nlat=f1.createVariable('nav_lat','f4',('lat','lon'))
nlon[:,:]=lonsst
nlat[:,:]=latsst
sst_int=f1.createVariable('sst_int', 'f4', ('lat', 'lon'))
sst_int[:,:]=temp_int
f1.close()


