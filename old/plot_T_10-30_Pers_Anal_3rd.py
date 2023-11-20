# Emanuel Clementi 22-02-2019
# This script plots the timeseries diagnostics for 2 experiments


import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from netCDF4 import Dataset
import netCDF4 as ncdf
import datetime
import pandas as pd
import glob
from numpy import *
import warnings
from pylab import ylabel
warnings.filterwarnings("ignore")

pathdir='/data/oda/ec04916/DATA/QVR/'

figdir='/work/oda/ec04916/FIGURE/QVR/'

# VAR STRUCTURE: (time, forecasts, depths, metrics, areas)
# metric:   "number of data values",  "mean of product ",  "mean of reference",   "mean squared error" ;
SEASONini=['0101','0401','0701','1001']
SEASONfin=['0331','0630','0930','1231']

MONTHini=['0401','0501','0601']
MONTHfin=['0430','0531','0630']

MONTHini=['0101','0201','0301','0401','0501','0601','0701','0801','0901','1001','1101','1201']
MONTHfin=['0131','0228','0330','0430','0531','0630','0731','0831','0930','1031','1130','1231']

depth=1 #10-30m
depths=[10, 30, 150, 300, 600, 1000]
STAT_T16_an=[]
OBS_T16_an=[]
STAT_T16_fc3=[]
OBS_T16_fc3=[]
T16=[]
STAT_T24_an=[]
OBS_T24_an=[]
STAT_T24_fc3=[]
OBS_T24_fc3=[]
T24=[]
for year in range(2015,2021):
   for seas in range(0,4):
# 1/16
      filename16=pathdir+"product_quality_stats_MEDSEA-ANALYSIS-FORECAST-PHYS-006-001*"+str(year)+SEASONini[seas]+'_'+str(year)+SEASONfin[seas]+".nc"
      print(filename16)
      if glob.glob(filename16):
        file16=glob.glob(filename16)
        print(file16)
        fh16=ncdf.Dataset(file16[0],mode='r')
        AREA16        = fh16.variables['area_names'][:]
        METRIC16      = fh16.variables['metric_names'][:]
        FORECAST16    = fh16.variables['forecasts'][:]
        DEPTH16       = fh16.variables['depths'][:]
        TIME16        = fh16.variables['time'][:]
        TEMPERATURE16 = fh16.variables['stats_temperature'][:]
        fh16.close()
#Evaluates the time period
        ndays16=len(TIME16)
        data_ini16=datetime.date(1950, 1, 1) + datetime.timedelta(days=int(TIME16[0]))
        print(data_ini16)
        data_fin16=datetime.date(1950, 1, 1) + datetime.timedelta(days=int(TIME16[-1])+1)
        print(data_fin16)
        times16 = pd.date_range(str(data_ini16),periods=ndays16, freq = "1d")
#
        RMS_T16_an=np.sqrt(TEMPERATURE16[:,0,depth,3,0], where=(TEMPERATURE16[:,0,depth,0,0]!=0))
        STAT_T16_an.extend(RMS_T16_an)
        OBS_T16_an.extend(TEMPERATURE16[:,0,depth,0,0])

        RMS_T16_fc3=np.sqrt(TEMPERATURE16[:,3,depth,3,0], where=(TEMPERATURE16[:,3,depth,0,0]!=0))
        STAT_T16_fc3.extend(RMS_T16_fc3)
        OBS_T16_fc3.extend(TEMPERATURE16[:,3,depth,0,0])
        T16.extend(times16)

#1/24
      if year > 2016:
        filename24=pathdir+"product_quality_stats_MEDSEA-ANALYSIS-FORECAST-PHY-006-013*"+str(year)+SEASONini[seas]+'_'+str(year)+SEASONfin[seas]+".nc"
        print(filename24)
        if glob.glob(filename24):
          file24=glob.glob(filename24)
          print(file24)
          fh24=ncdf.Dataset(file24[0],mode='r')
          AREA24        = fh24.variables['area_names'][:]
          METRIC24      = fh24.variables['metric_names'][:]
          FORECAST24    = fh24.variables['forecasts'][:]
          DEPTH24       = fh24.variables['depths'][:]
          TIME24        = fh24.variables['time'][:]
          TEMPERATURE24 = fh24.variables['stats_temperature'][:]
          fh24.close()
#Evaluates the time period
          ndays24=len(TIME24)
          data_ini24=datetime.date(1950, 1, 1) + datetime.timedelta(days=int(TIME24[0]))
          print(data_ini24)
          data_fin24=datetime.date(1950, 1, 1) + datetime.timedelta(days=int(TIME24[-1])+1)
          print(data_fin24)
          times24 = pd.date_range(str(data_ini24),periods=ndays24, freq = "1d")

          RMS_T24_an=np.sqrt(TEMPERATURE24[:,0,depth,3,0], where=(TEMPERATURE24[:,0,depth,0,0]!=0))
          STAT_T24_an.extend(RMS_T24_an)
          OBS_T24_an.extend(TEMPERATURE24[:,0,depth,0,0])

          RMS_T24_fc3=np.sqrt(TEMPERATURE24[:,3,depth,3,0], where=(TEMPERATURE24[:,3,depth,0,0]!=0))
          STAT_T24_fc3.extend(RMS_T24_fc3)
          OBS_T24_fc3.extend(TEMPERATURE24[:,3,depth,0,0])
          T24.extend(times24)

#monthly 1/24
   for mm in range(0,11):
      if year > 2018:
        filename24=pathdir+"product_quality_stats_MEDSEA-ANALYSIS-FORECAST-PHY-006-013*"+str(year)+MONTHini[mm]+'_'+str(year)+MONTHfin[mm]+".nc"
        print(filename24)
        if glob.glob(filename24):
          file24=glob.glob(filename24)
          print(file24)
          fh24=ncdf.Dataset(file24[0],mode='r')
          AREA24        = fh24.variables['area_names'][:]
          METRIC24      = fh24.variables['metric_names'][:]
          FORECAST24    = fh24.variables['forecasts'][:]
          DEPTH24       = fh24.variables['depths'][:]
          TIME24        = fh24.variables['time'][:]
          TEMPERATURE24 = fh24.variables['stats_temperature'][:]
          fh24.close()
#Evaluates the time period
          ndays24=len(TIME24)
          data_ini24=datetime.date(1950, 1, 1) + datetime.timedelta(days=int(TIME24[0]))
          print(data_ini24)
          data_fin24=datetime.date(1950, 1, 1) + datetime.timedelta(days=int(TIME24[-1])+1)
          print(data_fin24)
          times24 = pd.date_range(str(data_ini24),periods=ndays24, freq = "1d")

          RMS_T24_an=np.sqrt(TEMPERATURE24[:,0,depth,3,0], where=(TEMPERATURE24[:,0,depth,0,0]!=0))
          STAT_T24_an.extend(RMS_T24_an)
          OBS_T24_an.extend(TEMPERATURE24[:,0,depth,0,0])

          RMS_T24_fc3=np.sqrt(TEMPERATURE24[:,3,depth,3,0], where=(TEMPERATURE24[:,3,depth,0,0]!=0))
          STAT_T24_fc3.extend(RMS_T24_fc3)
          OBS_T24_fc3.extend(TEMPERATURE24[:,3,depth,0,0])
          T24.extend(times24)
  
STAT_T16_an_ma=pd.DataFrame(STAT_T16_an).rolling(30).mean()
OBS_T16_an_ma=pd.DataFrame(OBS_T16_an).rolling(30).mean()
STAT_T24_an_ma=pd.DataFrame(STAT_T24_an).rolling(30).mean()
OBS_T24_an_ma=pd.DataFrame(OBS_T24_an).rolling(30).mean()

STAT_T16_fc3_ma=pd.DataFrame(STAT_T16_fc3).rolling(30).mean()
OBS_T16_fc3_ma=pd.DataFrame(OBS_T16_fc3).rolling(30).mean()
STAT_T24_fc3_ma=pd.DataFrame(STAT_T24_fc3).rolling(30).mean()
OBS_T24_fc3_ma=pd.DataFrame(OBS_T24_fc3).rolling(30).mean()

aa=np.shape(STAT_T16_an_ma)
bb=np.shape(OBS_T16_an_ma)
cc=np.shape(T16)
cc=np.shape(OBS_T24_an_ma)

##PLOT TEMPERATURE
fig = plt.figure(0,figsize=(11,5))
# the right  axes --> OBS
ax1 = fig.add_subplot(111)
plt.fill_between(T16,OBS_T16_an_ma[0],color="plum", alpha=0.4)
plt.fill_between(T24,OBS_T24_an_ma[0],color="lightblue", alpha=0.4)
ax1.yaxis.tick_right()
ax1.yaxis.set_label_position("right")
ax1.set_ylim([0,1000])
ylabel("N. OBS",fontsize=16)

#the left axes --> RMS
ax = fig.add_subplot(111, sharex=ax1, frameon=False)
line1 = ax.plot(T16,STAT_T16_an_ma[0],'-r',label='MED-PHY 1/16 AN',linewidth=1.5)
line2 = ax.plot(T24,STAT_T24_an_ma[0],'-b',label='MED-PHY 1/24 AN',linewidth=1.5)
line3 = ax.plot(T16,STAT_T16_fc3_ma[0],'--r',label='MED-PHY 1/16 FC3',linewidth=1.5)
line4 = ax.plot(T24,STAT_T24_fc3_ma[0],'--b',label='MED-PHY 1/24 FC3',linewidth=1.5)

ylabel("RMSD",fontsize=16)
leg = plt.legend(loc='upper right', ncol=2,  shadow=True, fancybox=True, fontsize=12)
leg.get_frame().set_alpha(0.3)
ax.grid('on')
plt.title('Temperature RMSD @ 10-30m Analysis & 3rd Day Forecast' ,fontsize=16)
ax.set_ylim([0.2,2.0])
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_minor_locator(mdates.MonthLocator((1,4,7,10)))
ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y"))
ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
ax.margins(x=0)
plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
#plt.savefig(figdir+'TEMP_RMSD_10-30_AN_3RD_MED_ma.jpg')
plt.savefig(figdir+'TEMP_RMSD_10-30_AN_3RD_MED_ma.png',format='png',dpi=1200)
##
