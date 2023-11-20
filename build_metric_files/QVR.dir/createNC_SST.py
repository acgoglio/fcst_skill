#! /usr/bin/env python
# Program to create a NetCDF file

from netCDF4 import Dataset
from netCDF4 import num2date, date2num
from datetime import datetime, timedelta
import numpy as np
import sys
import csv

def fillvar(fileu, filed, nn):
    with open(fileu) as r:
     reader = csv.reader(r)
     count=0
     for row in reader:
         if count < 17:
#             print count
             if row[1] != '      nan':
                 sst[0,nn,0,4,count]=float(row[1])
             if row[2] != '     nan':
                 sst[0,nn,0,1,count]=273.15+float(row[2])
             if row[3] != '     nan':
                 sst[0,nn,0,5,count]=float(row[3])
             if row[4] != '     nan':
                 sst[0,nn,0,2,count]=273.15+float(row[4])
             if row[5] != '     nan':
                 sst[0,nn,0,6,count]=float(row[5])
             if row[6] != '     nan':
                 sst[0,nn,0,7,count]=float(row[6])
             count=count+1
    with open(filed) as rr:
     reader = csv.reader(rr)
     count=0
     for row in reader:
         if count < 17:
#             print count
             if row[1] != '      nan':
                 sst[0,nn,0,3,count]=(float(row[1]))**2
             if row[3] != '     nan':
                 sst[0,nn,0,0,count]=float(row[3])
             count=count+1
    return sst
rootgrp = Dataset("SST.nc", "w", format="NETCDF4")
string_length = rootgrp.createDimension("string_length", 35)
time = rootgrp.createDimension("time", None)
areas = rootgrp.createDimension("areas", 17)
surface = rootgrp.createDimension("surface", 1)
forecasts = rootgrp.createDimension("forecasts", 1)
metrics = rootgrp.createDimension("metrics", 8)
# AREA_NAMES
area_names = rootgrp.createVariable("area_names","c",("areas","string_length",))
area_names.long_name = "area names"
area_names.description = "region over which statistics are aggregated"
# (1)Alboran Sea, (2) South West Med 1 (western part), (4) South West Med 2 (eastern part), (3) North West Med, (6) Tyrrhenian Sea 1 (northern part), (5) Tyrrhenian Sea 2 (southern part), (11) Adriatic Sea 1 (northern part), (10) Adriatic Sea 2 (southern part), (7) Ionian Sea 1 (western part), (9) Ionian Sea 2 (north-eastern part), (8) Ionian Sea 2 (south-eastern part), (13) Aegean Sea, (12) Levantine Sea 1 (western part), (14) Levantine Sea 2 (central-northern part), (15) Levantine Sea 3 (central southern part), (16) Levantine Sea 4 (eastern part).
areanames=np.chararray((17, 35))
areanames[0,:]=['M','e','d','i','t','e','r','r','a','n','e','a','n',' ','S','e','a',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']                        
areanames[1,:]=['A','l','b','o','r','a','n',' ','S','e','a',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
areanames[2,:]=['S','o','u','t','h',' ','W','e','s','t',' ','M','e','d',' ','w','e','s','t','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ',' ',' ']        
areanames[3,:]=['N','o','r','t','h',' ','W','e','s','t',' ','M','e','d',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']                     
areanames[4,:]=['S','o','u','t','h',' ','W','e','s','t',' ','M','e','d',' ','e','a','s','t','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ',' ',' ']       
areanames[5,:]=['T','y','r','r','h','e','n','i','a','n',' ','S','e','a',' ','s','o','u','t','h','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ',' ']       
areanames[6,:]=['T','y','r','r','h','e','n','i','a','n',' ','S','e','a',' ','n','o','r','t','h','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ',' ']
areanames[7,:]=['I','o','n','i','a','n',' ','S','e','a',' ','w','e','s','t','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']            
areanames[8,:]=['I','o','n','i','a','n',' ','S','e','a',' ','s','o','u','t','h','-','e','a','s','t','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ']
areanames[9,:]=['I','o','n','i','a','n',' ','S','e','a',' ','n','o','r','t','h','-','e','a','s','t','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ']
areanames[10,:]=['A','d','r','i','a','t','i','c',' ','S','e','a',' ','s','o','u','t','h','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ',' ',' ',' ']
areanames[11,:]=['A','d','r','i','a','t','i','c',' ','S','e','a',' ','n','o','r','t','h','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ',' ',' ',' ']         
areanames[12,:]=['L','e','v','a','n','t','i','n','e',' ','S','e','a',' ','w','e','s','t','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ',' ',' ',' ']         
areanames[13,:]=['A','e','g','e','a','n',' ','S','e','a',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
areanames[14,:]=['L','e','v','a','n','t','i','n','e',' ','S','e','a',' ','c','e','n','t','r','a','l','-','n','o','r','t','h','e','r','n',' ','p','a','r','t']
areanames[15,:]=['L','e','v','a','n','t','i','n','e',' ','S','e','a',' ','c','e','n','t','r','a','l','-','s','o','u','t','h','e','r','n',' ','p','a','r','t']
areanames[16,:]=['L','e','v','a','n','t','i','n','e',' ','S','e','a',' ','e','a','s','t','e','r','n',' ','p','a','r','t',' ',' ',' ',' ',' ',' ',' ',' ',' ']

area_names[:,:]=areanames
# METRIC_NAMES
metric_names = rootgrp.createVariable("metric_names","c",("metrics","string_length",))
metric_names.long_name = "metric names"
metricnames=np.chararray((8, 35))

metricnames[0,:]=['n','u','m','b','e','r',' ','o','f',' ','d','a','t','a',' ','v','a','l','u','e','s',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
metricnames[1,:]=['m','e','a','n',' ','o','f',' ','p','r','o','d','u','c','t',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
metricnames[2,:]=['m','e','a','n',' ','o','f',' ','r','e','f','e','r','e','n','c','e',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
metricnames[3,:]=['m','e','a','n',' ','s','q','u','a','r','e','d',' ','e','r','r','o','r',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
metricnames[4,:]=['v','a','r','i','a','n','c','e',' ','o','f',' ','p','r','o','d','u','c','t',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
metricnames[5,:]=['v','a','r','i','a','n','c','e',' ','o','f',' ','r','e','f','e','r','e','n','c','e',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
metricnames[6,:]=['c','o','v','a','r','i','a','n','c','e',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
metricnames[7,:]=['a','n','o','m','a','l','y',' ','c','o','r','r','e','l','a','t','i','o','n',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
metric_names[:,:]=metricnames

# FORECASTS
nna=sys.argv[4]
forecasts = rootgrp.createVariable("forecasts","f4",("forecasts",))
forecasts.long_name = "forecast lead time"
forecasts.units = "hours"
if int(nna)==0:
    forecast=np.array([1])
elif int(nna)==1:
    forecast=np.array([0])
elif int(nna)==2:
    forecast=np.array([-228])
elif int(nna)==3:
    forecast=np.array([-204])
elif int(nna)==4:
    forecast=np.array([-180])
elif int(nna)==5:
    forecast=np.array([-156])
elif int(nna)==6:
    forecast=np.array([-132])
elif int(nna)==7:
    forecast=np.array([-108])
elif int(nna)==8:
    forecast=np.array([-84])
elif int(nna)==9:
    forecast=np.array([-60])
elif int(nna)==10:
    forecast=np.array([-36])
elif int(nna)==11:
    forecast=np.array([-12])
elif int(nna)==12:
    forecast=np.array([6])
elif int(nna)==13:
    forecast=np.array([12])
elif int(nna)==14:
    forecast=np.array([36])
elif int(nna)==15:
    forecast=np.array([60])
elif int(nna)==16:
    forecast=np.array([84])
elif int(nna)==17:
    forecast=np.array([108])
elif int(nna)==18:
    forecast=np.array([132])
elif int(nna)==19:
    forecast=np.array([156])
elif int(nna)==20:
    forecast=np.array([180])
elif int(nna)==21:
    forecast=np.array([204])
else:
    forecast=np.array([228])
forecasts[:]=forecast

# TEMP

stats_sst = rootgrp.createVariable("stats_sst","f4",("time", "forecasts", "surface", "metrics", "areas",),fill_value=9999)
#stats_sst.Fill_Value = 9999
stats_sst.parameter = "Sea Surface Temperature" 
stats_sst.reference = "SST L4 from OSI TAC"
stats_sst.units = "K"
sst=np.ones((1,1,1,8,17))
sst[sst == 1 ]=9999
fileanS=sys.argv[1]
fileanE=sys.argv[2]
#nna=sys.argv[3]
sst=fillvar(fileanS,fileanE,0)
stats_sst[:,:,:,:,:] = sst

# TIME
time = rootgrp.createVariable("time","f4",("time",))
time.long_name = "validity time" 
time.units = "days since 01-01-1950 00:00:00" 

date=sys.argv[3]
yyyy=int(date[0:4])
mm=int(date[4:6])
dd=int(date[6:8])

dates=datetime(yyyy,mm,dd)  
time_num=dates.toordinal()
dateso=datetime(1950,1,1)
time_numo=dateso.toordinal()
A=time_num-time_numo+0.5

time[:]=A
# GLOBAL ATTRIBUTE

rootgrp.contact = "alessandro.grandi@cmcc.it"
rootgrp.product = "MEDSEA-ANALYSISFORECAST-PHY-006-013"
rootgrp.institution = "Centro Euro-Mediterraneo sui Cambiamenti Climatici - CMCC, Italy"
#rootgrp.NCO = "4.4.9"

rootgrp.close()
