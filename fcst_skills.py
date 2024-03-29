# AC Goglio Sep 2022
# Script for Forecast skill score
# Load condaE virtual env!

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from netCDF4 import Dataset
import netCDF4 as ncdf
import datetime
#from datetime import datetime
import pandas as pd
import glob
from numpy import *
import warnings
from pylab import ylabel
import matplotlib.pylab as pl 
warnings.filterwarnings("ignore")

#####################################

# -- Workdir path -- 
workdir = '/work/oda/ag15419/tmp/Ana_Fcst/AI/prova_AI/'

# -- Period --
start_date = 20210801
end_date   = 20220731

# -- Analysis type --
flag_mean = 1

# -- Area code --
area_names = ["Mediterranean Sea","Alboran Sea","South West Med western part","North West Med","South West Med eastern part","Tyrrhenian Sea southern part","Tyrrhenian Sea northern part","Ionian Sea western part","Ionian Sea south-eastern part","Ionian Sea north-eastern part","Adriatic Sea southern part","Adriatic Sea northern part","Levantine Sea western part","Aegean Sea","Levantine Sea central-northern part","Levantine Sea central-southern part","Levantine Sea eastern part"]

# ---  Input archive ---
input_dir               = '/work/opa/ag22216/testVALFOR_18_AI/out/'
input_vars              = ['salinity','sla','sstl3s','sst','temperature'] # Do not change the order..
input_field_in_filename = ['TEMP','TEMP','TEMP','TEMP','TEMP'] #['PSAL','SSH','SSTL3S','SSTL4','TEMP']
udm                     = ['PSU','cm','$^{\circ}$C','$^{\circ}$C','$^{\circ}$C']

# --- Type of vertical subdivision: layers 1 or dept 0 ---
layers_flag = 1

#############################
# Input read and checks

# dates handling
start_yy   = int(str(start_date)[0:4])
end_yy     = int(str(end_date)[0:4])
start_mm   = int(str(start_date)[4:6])
end_mm   = int(str(end_date)[4:6])
start_dd   = int(str(start_date)[6:8])
end_dd   = int(str(end_date)[6:8])
#
all_months_1 = list(range(1,12+1))
all_months = [str(i).zfill(2) for i in all_months_1] 
all_months = np.array(all_months)
all_days_1 = list(range(1,31+1))
all_days = [str(i).zfill(2) for i in all_days_1]
all_days = np.array(all_days)

# Days per file (WARNING: if more than one day is provided in each file the code must be modified. Only ONE day option is implemented at the moment.)
days_num = 1

if start_date > end_date :
   print ('ERROR: start_date > end_date!!')
   quit()
else: 
   print ('PERIOD: ',start_date,end_date)

# Loop on Med areas
for area_code,area_name in enumerate(area_names):
   print ('I am working on Med region: ',area_name)
  
   # Loop on vars
   for var_idx,var in enumerate(input_vars):
       print ('I am working on var ',var)
   
       # Loop on vertical layers (1 plot each, if a combination is needed the arrays in the fields loop must include the depth index in the name)
       if var == 'salinity' or var == 'temperature':
          if layers_flag == 1:
             depths_defn = ['0-10', '10-30', '30-60', '60-100', '100-150', '150-300' ]#, '300-600', '600-1000', '1000-2000']
          elif layers_flag == 0:
             depths_defn = ['1', '3', '5', '8', '11', '19', '30', '51', '73','98','153','203','250','304','399','556','756','971']
       elif var == 'sla' or var == 'sst' or var == 'sstl3s':
          depths      = [0] 
          depths_defn = ['0']
   
       for depth_idx,depth in enumerate(depths_defn):
         print ('I am working on vlev: ',depth)
   
         # Fields to be read and plot
         fields = [1, 0, -228, -204, -180, -156, -132, -108, -84, -60, -36, -12, 6, 12, 36, 60, 84, 108, 132, 156, 180, 204, 228]
         fields_defn = ['climatology','analysis','pers 228h','pers 204h','pers 180h','pers 156h','pers 132h','pers 108h','pers 84h','pers 60h','pers 36h','pers 12h','fcst 6h','fcst 1d','fcst 2d','fcst 3d','fcst 4d','fcst 5d','fcst 6d','fcst 7d','fcst 8d','fcst 9d','fcst 10d']
         # Loop on fields
         for field_idx,field in enumerate(fields): 
           # Work only on required fields
           if field == -156 or field == -132 or field == -108 or field == -84 or field == -60 or field == -36 or field == -12 or field == 12 or field == 36 or field == 60 or field == 84 or field == 108 or field == 132 or field == 156 :
             print ('I am going to extract ',fields_defn[field_idx])
             # Root Mean Squared Diff
             globals()['rmsd_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             ## Bias computed as mean of product - mean of reference
             #globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Anomaly Correlation
             globals()['acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Obs num
             globals()['obs_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Time var   
             time_var=[]

             # Loop on input files
             for yy in range(start_yy,end_yy+1):
                print ('Working on year',yy)
                for mm in all_months :
                   #print ('Working on month',mm) 
                   for dd_dir in all_days :
                    for dd in all_days :
                     #print ('Working on day',dd)  
                     file_to_open=input_dir+str(yy)+str(mm)+str(dd)+'.'+input_field_in_filename[var_idx]+'.nc' 
                     #input_dir+str(yy)+str(mm)+str(dd_dir)+'/'+str(yy)+str(mm)+str(dd)+'.'+input_field_in_filename[var_idx]+'.nc'
                     #print ('I am working on file:',file_to_open)
                     # check the existence of the file and open it
                     if glob.glob(file_to_open): 
                        print ('Found date ',yy,mm,dd)
                        print ('I am opening file: ',file_to_open)
                        fh = ncdf.Dataset(file_to_open,mode='r')
                        time_r = fh.variables['time'][:]
                        # var(time, forecasts, depths, metrics, areas) ;
                        var_msd  = fh.variables['stats_'+var][:,field_idx,depth_idx,3,area_code]
                        #var_bias = fh.variables['stats_'+var][:,field_idx,depth_idx,1,area_code] - fh.variables['stats_'+var][:,field_idx,depth_idx,2,area_code]
                        #var_bias[var_bias > 1000] = np.nan
                        var_acc = fh.variables['stats_'+var][:,field_idx,depth_idx,7,area_code]
                        var_acc[var_acc > 1000] = np.nan
                        var_obs  = fh.variables['stats_'+var][:,field_idx,depth_idx,0,area_code]
                        fh.close()
                        # Check the num of days
                        days_num_infile = len(np.array(time_r))
                        print ('days_num ',days_num_infile)
                        if days_num!= days_num_infile:
                           print ('WARNING: Issues with days num in the input file!')
                           print ('A single day is expected for each input file..')
                     else:
                        #print ('WARNING: input file NOT found for date ',yy,mm,dd)
                        var_msd   = np.nan #np.empty(days_num)
                        #var_bias  = np.nan np.empty(days_num)
                        var_acc  = np.nan #np.empty(days_num)
                        var_obs   = np.nan #np.empty(days_num)
                    
                     # Compute the RMSD (time, forecasts, depths, metrics, areas) ad sqrt(msd)
                     try:
                        globals()['rmsd_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(sqrt(var_msd))
                     except:
                        print ('ISSUES',str(field),str(depth),var,var_msd)
                        globals()['rmsd_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_msd) 
                     # Read the bias
                     #globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_bias) 
                     # Read the anomaly correlation coefficient
                     globals()['acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_acc) 
                     # Read the num of obs in first loop iteration
                     globals()['obs_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_obs) 
             # compute the mean values on the whole period
             # Mean of the RMSD
             globals()['mean_rmsd_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['rmsd_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             # Mean of the ACC
             try: # TMP
                globals()['mean_acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             except:
                print ('ISSUES',str(field),str(depth),var,globals()['acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                globals()['mean_acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=globals()['acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
             # Mean of the OBS
             globals()['mean_obs_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['obs_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
         print ('..Done!')  
   
         # Compute the date array
         time_var=pd.date_range(datetime.date(start_yy, start_mm, start_dd),datetime.date(end_yy, end_mm, end_dd))
         print ('time_var',time_var.shape,time_var)

         #####################
         if flag_mean == 1 :

            # MEAN PLOT
            fig = plt.figure(figsize=(12,15))
            plt.rc('font', size=18)
            fig_name = workdir+'mean_'+var+'_RMSD_ACC_'+str(depth)+'_'+str(start_yy)+'-'+str(end_yy)+'_'+str(area_code)+'.png'
            print ('Plot: ',fig_name)

            # PLOT 1: RMSD
            plt.subplot(2,1,1)
            # Plot each field
            fields_2_include=[-156, -132, -108, -84, -60, -36,-12, 12, 36, 60, 84, 108, 132, 156]
            fields_defn = ['1 Day','2 Day','3 Day','4 Day','5 Day','6 Day','7 Day']
            fields_defn =  np.array(fields_defn)
            p_rmsd=[]
            f_rmsd=[] 
            for field_idx,field in enumerate(fields_2_include):
                  if field <0 :
                     try: 
                        p_rmsd.append(float(globals()['mean_rmsd_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        p_rmsd.append(np.nan)
                  else:
                     try:
                        f_rmsd.append(float(globals()['mean_rmsd_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        f_rmsd.append(np.nan)
                  #
            # Set the correct order to the persistence values
            p_rmsd=p_rmsd[::-1]
            #print ('PROVA p:',p_rmsd)
            #print ('PROVA f:',f_rmsd)
            plt.plot(fields_defn,p_rmsd,'o-',color="green",label='Mean RMSD Persistence')
            plt.plot(fields_defn,f_rmsd,'o-',color="red",label='Mean RMSD Forecast')
            ylabel("Mean RMSD ["+udm[var_idx]+']',fontsize=16)
            plt.grid('on')
            plt.legend(loc='upper left', ncol=1,  shadow=True, fancybox=True, framealpha=0.5,fontsize=16) 
            plt.title(str(start_date)+'-'+str(end_date)+' Mean RMSD of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=18)
            

            # PLOT 2: ACC
            plt.subplot(2,1,2)
            # Plot each field
            p_acc=[]
            f_acc=[]
            for field_idx,field in enumerate(fields_2_include):
                  if field <0 :
                     try:
                        p_acc.append(float(globals()['mean_acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        p_acc.append(np.nan)
                  else:
                     try:
                        f_acc.append(float(globals()['mean_acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        f_acc.append(np.nan)
            # Set the correct order to the persistence values
            p_acc=p_acc[::-1]
            #print ('PROVA p:',p_acc)
            #print ('PROVA f:',f_acc)
            plt.plot(fields_defn,p_acc,'-o',color="green",label='Mean ACC Persistence')
            plt.plot(fields_defn,f_acc,'-o',color="red",label='Mean ACC Forecast')
            ylabel("Mean ACC",fontsize=16) #["+udm[var_idx]+']',fontsize=16)
            plt.grid('on')
            plt.legend(loc='upper right', ncol=1,  shadow=True, fancybox=True, framealpha=0.5,fontsize=16)
            plt.title(str(start_date)+'-'+str(end_date)+' Mean ACC of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=18)

            plt.tight_layout()
            plt.savefig(fig_name,format='png',dpi=1200)
            plt.clf()
                                                                                                                                        
