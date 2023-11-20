#! /usr/bin/env python

from netCDF4 import Dataset
import numpy as np 
import sys
import xarray as xr
import pandas as pd

filein=sys.argv[1]

dsG = xr.open_dataset(filein)
tg = dsG.variables['TEMP'][:]
sg = dsG.variables['PSAL'][:]
tgb = np.where(np.isnan(tg), 9.96921e+36, tg)
sgb = np.where(np.isnan(sg), 9.96921e+36, sg)
#Dataset.close()


fileout=sys.argv[2]
#input file
dsin = Dataset(filein)

#output file
dsout = Dataset(fileout, "w", format="NETCDF3_CLASSIC")

# copy global attributes all at once via dictionary
dsout.setncatts(dsin.__dict__)

#Copy dimensions
for dname, the_dim in dsin.dimensions.items():
    if dname != 'TIME':
#        print dname, len(the_dim)
        dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)

time = dsout.createDimension('TIME', None)

# Copy variables
for v_name, varin in dsin.variables.items():
    if v_name != 'TEMP' and v_name != 'PSAL':
        outVar = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
#        print v_name, varin.datatype
    # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
        outVar[:] = varin[:]
    elif v_name == 'TEMP':
        outVar = dsout.createVariable(v_name, np.float32, varin.dimensions,fill_value= 9.96921e+36)
        outVar[:] = tgb[:]
    else:
        outVar = dsout.createVariable(v_name, np.float32, varin.dimensions,fill_value= 9.96921e+36)
        outVar[:] = sgb[:]
#        outVar._FillValue = '9.96921e+36f' 
# close the output file

dsout.close()

