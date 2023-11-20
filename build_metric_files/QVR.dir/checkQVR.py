#! /usr/bin/env python
# Program to check MVR 

from netCDF4 import Dataset
import sys
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from copy import copy, deepcopy
import datetime
import time
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pylab import figure, show, legend, ylabel

# Dir where there is the temporary file TEMP.nc
dirin=sys.argv[1]
# Dir where there are the output plots
dirout=sys.argv[2]
# Start date of statistics
sdate=sys.argv[3]
# End date of statistics
edate=sys.argv[4]
# 0 if we want the plots only for the Med 1 if we want the plots for all regions
ar=sys.argv[5]

def plot_stats(sat, i, j, k, nmvar):
    start = datetime.datetime.strptime(sdate, "%Y%m%d")
    end = datetime.datetime.strptime(edate, "%Y%m%d")
    times = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days+1)]
    fig = plt.figure(figsize=(9, 5))
    plt.rc('xtick',labelsize=14)
    plt.rc('ytick',labelsize=14)
    ax = fig.add_subplot(111)
    if j==3:
        line1=ax.plot(times,np.sqrt(sat[:,0,i,j,k]),color='#000000', linestyle='solid',label='CL')
        line2=ax.plot(times,np.sqrt(sat[:,1,i,j,k]),color='#FF0000', linestyle='solid',label='AN')
        line3=ax.plot(times,np.sqrt(sat[:,2,i,j,k]),color='#00FFFF', linestyle='solid',label='10P')
        line4=ax.plot(times,np.sqrt(sat[:,3,i,j,k]),color='#F5F5DC', linestyle='solid',label='9P')
        line5=ax.plot(times,np.sqrt(sat[:,4,i,j,k]),color='#7FFF00', linestyle='solid',label='8P')
        line6=ax.plot(times,np.sqrt(sat[:,5,i,j,k]),color='#D2691E', linestyle='solid',label='7P')
        line7=ax.plot(times,np.sqrt(sat[:,6,i,j,k]),color='#FF7F50', linestyle='solid',label='6P')
        line8=ax.plot(times,np.sqrt(sat[:,7,i,j,k]),color='#FF00FF', linestyle='solid',label='5P')
        line9=ax.plot(times,np.sqrt(sat[:,8,i,j,k]),color='#FFD700', linestyle='solid',label='4P')
        line10=ax.plot(times,np.sqrt(sat[:,9,i,j,k]),color='#4B0082', linestyle='solid',label='3P')
        line11=ax.plot(times,np.sqrt(sat[:,10,i,j,k]),color='#FF00FF', linestyle='solid',label='2P')
        line12=ax.plot(times,np.sqrt(sat[:,11,i,j,k]),color='#0000FF', linestyle='solid',label='1P')
        line13=ax.plot(times,np.sqrt(sat[:,12,i,j,k]),color='#008000', linestyle='solid',label='SM')
        line14=ax.plot(times,np.sqrt(sat[:,13,i,j,k]),color='#800000', linestyle='solid',label='1F')
        line15=ax.plot(times,np.sqrt(sat[:,14,i,j,k]),color='#808000', linestyle='solid',label='2F')
        line16=ax.plot(times,np.sqrt(sat[:,15,i,j,k]),color='#000080', linestyle='solid',label='3F')
        line17=ax.plot(times,np.sqrt(sat[:,16,i,j,k]),color='#FFA500', linestyle='solid',label='4F')
        line18=ax.plot(times,np.sqrt(sat[:,17,i,j,k]),color='#DA70D6', linestyle='solid',label='5F')
        line19=ax.plot(times,np.sqrt(sat[:,18,i,j,k]),color='#800080', linestyle='solid',label='6F')
        line20=ax.plot(times,np.sqrt(sat[:,19,i,j,k]),color='#A0522D', linestyle='solid',label='7F')
        line21=ax.plot(times,np.sqrt(sat[:,20,i,j,k]),color='#C0C0C0', linestyle='solid',label='8F')
        line22=ax.plot(times,np.sqrt(sat[:,21,i,j,k]),color='#EE82EE', linestyle='solid',label='9F')
        line23=ax.plot(times,np.sqrt(sat[:,22,i,j,k]),color='#FFFF00', linestyle='solid',label='10F')
    else:
        line1=ax.plot(times,sat[:,0,i,j,k],color='#000000', linestyle='solid',label='CL')
        line2=ax.plot(times,sat[:,1,i,j,k],color='#FF0000', linestyle='solid',label='AN')
        line3=ax.plot(times,sat[:,2,i,j,k],color='#00FFFF', linestyle='solid',label='10P')
        line4=ax.plot(times,sat[:,3,i,j,k],color='#F5F5DC', linestyle='solid',label='9P')
        line5=ax.plot(times,sat[:,4,i,j,k],color='#7FFF00', linestyle='solid',label='8P')
        line6=ax.plot(times,sat[:,5,i,j,k],color='#D2691E', linestyle='solid',label='7P')
        line7=ax.plot(times,sat[:,6,i,j,k],color='#FF7F50', linestyle='solid',label='6P')
        line8=ax.plot(times,sat[:,7,i,j,k],color='#FF00FF', linestyle='solid',label='5P')
        line9=ax.plot(times,sat[:,8,i,j,k],color='#FFD700', linestyle='solid',label='4P')
        line10=ax.plot(times,sat[:,9,i,j,k],color='#4B0082', linestyle='solid',label='3P')
        line11=ax.plot(times,sat[:,10,i,j,k],color='#FF00FF', linestyle='solid',label='2P')
        line12=ax.plot(times,sat[:,11,i,j,k],color='#0000FF', linestyle='solid',label='1P')
        line13=ax.plot(times,sat[:,12,i,j,k],color='#008000', linestyle='solid',label='SM')
        line14=ax.plot(times,sat[:,13,i,j,k],color='#800000', linestyle='solid',label='1F')
        line15=ax.plot(times,sat[:,14,i,j,k],color='#808000', linestyle='solid',label='2F')
        line16=ax.plot(times,sat[:,15,i,j,k],color='#000080', linestyle='solid',label='3F')
        line17=ax.plot(times,sat[:,16,i,j,k],color='#FFA500', linestyle='solid',label='4F')
        line18=ax.plot(times,sat[:,17,i,j,k],color='#DA70D6', linestyle='solid',label='5F')
        line19=ax.plot(times,sat[:,18,i,j,k],color='#800080', linestyle='solid',label='6F')
        line20=ax.plot(times,sat[:,19,i,j,k],color='#A0522D', linestyle='solid',label='7F')
        line21=ax.plot(times,sat[:,20,i,j,k],color='#C0C0C0', linestyle='solid',label='8F')
        line22=ax.plot(times,sat[:,21,i,j,k],color='#EE82EE', linestyle='solid',label='9F')
        line23=ax.plot(times,sat[:,22,i,j,k],color='#FFFF00', linestyle='solid',label='10F')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
#    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=5))
    datemin = np.datetime64(times[0], 'D')
    datemax = np.datetime64(times[-1], 'D') + np.timedelta64(1, 'D')
    ax.set_xlim(datemin, datemax)
    if nmvar=='TEMP' or nmvar=='PSAL':
        ax.set_title(metn[j]+' '+nmvar+' '+str(levdim[i])+'m\n'+arean[k] , fontsize=18)
    else:
        ax.set_title(metn[j]+' '+nmvar+'\n'+arean[k] , fontsize=18)
    ax.grid('on',linestyle='--') 
#    ax.legend(loc='best', ncol=8)
    fig.autofmt_xdate()
    plt.savefig(dirout+'/'+sglfile[j]+'_'+nmvar+'_l'+str(i)+'_a'+str(k)+'.png')
    plt.close('all')
    return(ax)

metn=['Number of data','Mean of product','Mean of reference','RMS','Variance of product','variance of reference','Covariance','Anomaly correlation']
sglfile=['NOBS','MP','MR','RMS','VP','VR','CO','AC']
arean=['Mediterranean Sea','Alboran Sea','South West Med western part',
       'North West Med','South West Med eastern part','Tyrrhenian Sea southern part',
       'Tyrrhenian Sea northern part','Ionian Sea western part',
       'Ionian Sea south-eastern part','Ionian Sea north-eastern part',
       'Adriatic Sea southern part','Adriatic Sea northern part',
       'Levantine Sea western part','Aegean Sea','Levantine Sea central-northern part',
       'Levantine Sea central-southern part','Levantine Sea eastern part']
var=['stats_temperature','stats_salinity','stats_sla','stats_sst','stats_sstl3s']
namevar=['TEMP','PSAL','SLA','SST_L4','SST_L3S']

fh = Dataset(dirin+'/TEMP.nc', mode='r')
levdim = fh.variables['depths'][:]
for n in range(len(var)):
    field = fh.variables[var[n]][:]
    if n<2:
        for jj in range(len(metn)):
            for ii in range(len(levdim)):
                if int(ar)==0:
                    plot_stats(field,ii,jj,0,namevar[n])
                else:
                    for kk in range(len(arean)): 
                        plot_stats(field,ii,jj,kk,namevar[n])
    else:
        for jj in range(len(metn)):
            if int(ar)==0:
                plot_stats(field,0,jj,0,namevar[n])
            else:
                for kk in range(len(arean)):    
                    plot_stats(field,0,jj,kk,namevar[n])
fh.close()
