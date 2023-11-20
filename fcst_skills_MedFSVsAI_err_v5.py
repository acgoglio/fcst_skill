# AC Goglio Sep 2022
# Script for Forecast skill score
# Load condaE virtual env!

import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from netCDF4 import Dataset
import netCDF4 as ncdf
import datetime
from datetime import timedelta #datetime
import pandas as pd
import glob
from numpy import *
import warnings
from pylab import ylabel
import matplotlib.pylab as pl 
warnings.filterwarnings("ignore")

#####################################
# Read line arg
argv=sys.argv
year      = argv[1]
per_month = argv[2]
first_day = argv[3]
last_day  = argv[4]

# -- Workdir path -- 
workdir = '/work/oda/ag15419/tmp/Ana_Fcst/AI/monthly_comp_v5/'

# -- Period --
start_date = int(str(year)+str(per_month)+str(first_day))
end_date   = int(str(year)+str(per_month)+str(last_day))
print ('Working on period: ',start_date,end_date)

# -- Analysis type --
# To plot the time series set flag_ts = 1
flag_ts = 1
# to plot RMSD and ACC mean set flag_mean = 1
flag_mean = 1
# If you want to compute and plot a rolling mean set flag_rolling_mean = 1, otherwise all the values will be plotted
flag_rolling_mean = 0

# -- Area code --
area_names = ["Mediterranean Sea","Alboran Sea","South West Med western part","North West Med","South West Med eastern part","Tyrrhenian Sea southern part","Tyrrhenian Sea northern part","Ionian Sea western part","Ionian Sea south-eastern part","Ionian Sea north-eastern part","Adriatic Sea southern part","Adriatic Sea northern part","Levantine Sea western part","Aegean Sea","Levantine Sea central-northern part","Levantine Sea central-southern part","Levantine Sea eastern part"]

# --- Datasets Name ---
dataset_names=['ML model','Dynamic model']

# ---  Input archive ---
input_dir_1             = '/work/opa/ag22216/testVALFOR_18_AI_v5/out/'
input_dir_2             = '/work/opa/ag22216/testVALFOR_18_END/out/'
input_vars              = ['salinity','sla','sstl3s','sst','temperature'] # Do not change the order..
input_field_in_filename = ['TEMP','TEMP','TEMP','TEMP','TEMP'] #['PSAL','SSH','SSTL3S','SSTL4','TEMP']
udm                     = ['PSU','cm','$^{\circ}$C','$^{\circ}$C','$^{\circ}$C']

# --- Set the num of days to be included in the rolling mean for the time-series plot ---
if flag_ts == 1 and flag_rolling_mean == 1:
   rolling_mean_days = 2

#############################
# Input read and checks

# dates handling
start_yy   = int(str(start_date)[0:4])
end_yy     = int(str(end_date)[0:4])
start_mm   = int(str(start_date)[4:6])
end_mm     = int(str(end_date)[4:6])
start_dd   = int(str(start_date)[6:8])
end_dd     = int(str(end_date)[6:8])
#
#all_months_1 = list(range(1,12+1))
#all_months   = [str(i).zfill(2) for i in all_months_1]
all_months_1   = per_month
all_months   = str(all_months_1).zfill(2)
all_months   = np.array(all_months)
#all_days_1   = list(range(1,31+1))
all_days_1     = list(range(int(first_day),int(last_day)+1))
all_days     = [str(i).zfill(2) for i in all_days_1]
all_days     = np.array(all_days)

# Days per file (WARNING: if more than one day is provided in each file the code must be modified. Only ONE day option is implemented at the moment.)
days_num = 1

if start_date > end_date :
   print ('ERROR: start_date > end_date!!')
   quit()
else: 
   print ('PERIOD: ',start_date,end_date)

# Loop on Med areas
#for area_code,area_name in enumerate(area_names):
area_code=0
area_name=area_names[area_code]
print ('I am working on Med region: ',area_name)
  
# Loop on vars
for var_idx,var in enumerate(input_vars):
       print ('I am working on var ',var)
   
       # Loop on vertical layers (1 plot each, if a combination is needed the arrays in the fields loop must include the depth index in the name)
       if var == 'salinity' or var == 'temperature':
          depths      = [10, 30, 60, 100, 150, 300, 600, 1000, 2000]
          depths_defn = ['0-10', '10-30', '30-60', '60-100', '100-150', '150-300', '300-600', '600-1000', '1000-2000']
       elif var == 'sla' or var == 'sst' or var == 'sstl3s':
          depths      = [0] 
          depths_defn = ['0']
   
       for depth_idx,depth in enumerate(depths):
         print ('I am working on vlev: ',depth)
   
         # Fields to be read and plot
         fields = [1, 0, -228, -204, -180, -156, -132, -108, -84, -60, -36, -12, 6, 12, 36, 60, 84, 108, 132, 156, 180, 204, 228]
         fields_defn_or = ['climatology','analysis','pers 228h','pers 204h','pers 180h','pers 156h','pers 132h','pers 108h','pers 84h','pers 60h','pers 36h','pers 12h','fcst 6h','fcst 1d','fcst 2d','fcst 3d','fcst 4d','fcst 5d','fcst 6d','fcst 7d','fcst 8d','fcst 9d','fcst 10d']
         # Loop on fields
         for field_idx,field in enumerate(fields): 
           # Work only on required fields
           if field == -156 or field == -132 or field == -108 or field == -84 or field == -60 or field == -36 or field == -12 or field == 12 or field == 36 or field == 60 or field == 84 or field == 108 or field == 132 or field == 156 :
             print ('I am going to extract ',fields_defn_or[field_idx])
             # Root Mean Squared Diff
             globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Mean Squared Diff
             globals()['msd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             globals()['msd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Standard Deviation
             globals()['std_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             globals()['std_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Variance
             globals()['var_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             globals()['var_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Anomaly Correlation
             globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Obs num
             globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Time var   
             time_var=[]

             # Loop on input files
             for yy in range(start_yy,end_yy+1):
                print ('Working on year',yy)
                # Loop on months
                mm = all_months
                #for mm in all_months :
                print ('Working on month',mm) 
                # Loop on days
                for dd in all_days :
                     print ('Working on day',dd)  
                     file_to_open_1=input_dir_1+str(yy)+str(mm)+str(dd)+'.'+input_field_in_filename[var_idx]+'.nc' 
                     file_to_open_2=input_dir_2+str(yy)+str(mm)+str(dd)+'.'+input_field_in_filename[var_idx]+'.nc'
                     #print ('I am working on files:',file_to_open_1,file_to_open_2)

                     # Check the existence of file 1 and open it
                     if glob.glob(file_to_open_1): 
                        print ('Found date ',yy,mm,dd)
                        print ('I am opening file: ',file_to_open_1)
                        fh_1 = ncdf.Dataset(file_to_open_1,mode='r')
                        time_r = fh_1.variables['time'][:]
                        # var(time, forecasts, depths, metrics, areas) ;
                        # metrics = number of data values,mean of product,mean of reference,mean squared error,variance of product,variance of reference,covariance,anomaly correlation
                        var_msd_1 = fh_1.variables['stats_'+var][:,field_idx,depth_idx,3,area_code]
                        var_var_1 = fh_1.variables['stats_'+var][:,field_idx,depth_idx,4,area_code]
                        var_acc_1 = fh_1.variables['stats_'+var][:,field_idx,depth_idx,7,area_code]
                        var_acc_1[var_acc_1 > 1000] = np.nan
                        var_obs_1  = fh_1.variables['stats_'+var][:,field_idx,depth_idx,0,area_code]
                        fh_1.close()
                        # Check the num of days
                        days_num_infile = len(np.array(time_r))
                        print ('days_num ',days_num_infile)
                        if days_num!= days_num_infile:
                           print ('WARNING: Issues with days num in the input file!')
                           print ('A single day is expected for each input file..')
                     else:
                        print ('WARNING: input file NOT found for date ',yy,mm,dd)
                        var_msd_1  = np.nan 
                        var_var_1  = np.nan
                        var_acc_1  = np.nan 
                        var_obs_1  = np.nan 

                     # check the existence of file 2 and open it
                     if glob.glob(file_to_open_2):
                        print ('Found date ',yy,mm,dd)
                        print ('I am opening file: ',file_to_open_2)
                        fh_2 = ncdf.Dataset(file_to_open_2,mode='r')
                        time_r_2 = fh_2.variables['time'][:]
                        # var(time, forecasts, depths, metrics, areas) ;
                        # metrics = number of data values,mean of product,mean of reference,mean squared error,variance of product,variance of reference,covariance,anomaly correlation
                        var_msd_2  = fh_2.variables['stats_'+var][:,field_idx,depth_idx,3,area_code]
                        var_var_2  = fh_2.variables['stats_'+var][:,field_idx,depth_idx,4,area_code]
                        var_acc_2 = fh_2.variables['stats_'+var][:,field_idx,depth_idx,7,area_code]
                        var_acc_2[var_acc_2 > 1000] = np.nan
                        var_obs_2  = fh_2.variables['stats_'+var][:,field_idx,depth_idx,0,area_code]
                        fh_2.close()
                        # Check the num of days
                        days_num_infile_2 = len(np.array(time_r_2))
                        print ('days_num ',days_num_infile_2)
                        if days_num!= days_num_infile_2:
                           print ('WARNING: Issues with days num in the input file!')
                           print ('A single day is expected for each input file..')
                     else:
                        print ('WARNING: input file NOT found for date ',yy,mm,dd)
                        var_msd_2  = np.nan
                        var_var_2  = np.nan
                        var_acc_2  = np.nan 
                        var_obs_2  = np.nan                     

                     # Compute the RMSD (time, forecasts, depths, metrics, areas) = sqrt(MSD)
                     try:
                        globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(sqrt(var_msd_1))  
                        globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(sqrt(var_msd_2)) 
                        globals()['msd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_msd_1)
                        globals()['msd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_msd_2)
                     # If nans do not take the square:
                     except:
                        globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nan) #(var_msd_1) 
                        globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nan) #(var_msd_2)
                        globals()['msd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nan) #(var_msd_1)
                        globals()['msd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nan) #(var_msd_2)

                     # Compute the STD (time, forecasts, depths, metrics, areas) = sqrt(VAR)


                     # Read the anomaly correlation
                     globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_acc_1)
                     globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_acc_2)

                     try:
                        globals()['std_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(sqrt(var_var_1))
                        globals()['std_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(sqrt(var_var_2))
                        globals()['var_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_var_1)
                        globals()['var_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_var_2)
                     # If nans do not take the square:
                     except:
                        globals()['std_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nan) #(var_msd_1) 
                        globals()['std_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nan) #(var_msd_2)
                        globals()['var_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nan) #(var_msd_1)
                        globals()['var_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nan) #(var_msd_2)


                     # Read the num of obs in first loop iteration
                     globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_obs_1)
                     globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_obs_2)

             # Compute the mean values on the whole period
             # Mean and percentiles of the RMSD and STD (if not nans..)
             try:
                globals()['mean_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)] = np.nanmean(globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                globals()['mean_std_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nanmean(globals()['std_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                globals()['q25_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.percentile(globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],25)
                globals()['q75_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.percentile(globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],75)
                globals()['std_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.std(globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             # If the values are nans
             except:
                globals()['mean_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)] = np.nan
                globals()['mean_std_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
                globals()['q25_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
                globals()['q75_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
                globals()['std_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
             # Mean of the MSD
             globals()['mean_msd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)] = np.nanmean(globals()['msd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             #
             try:
                globals()['mean_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)] = np.nanmean(globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                globals()['mean_std_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nanmean(globals()['std_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                globals()['q25_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.percentile(globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],25)
                globals()['q75_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.percentile(globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],75)
                globals()['std_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.std(globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             # If the values are nans
             except:
                globals()['mean_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)] = np.nan #globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
                globals()['mean_std_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
                globals()['q25_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
                globals()['q75_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
                globals()['std_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
             # Mean of the MSD
             globals()['mean_msd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)] = np.nanmean(globals()['msd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])

             # Mean of the ACC
             # Mean of the ACC (if not nans..)
             try:
                globals()['mean_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                globals()['q25_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.percentile(globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],25)
                globals()['q75_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.percentile(globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],75)
                globals()['std_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.std(globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             # If the values are nans
             except:
                globals()['mean_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)] = np.nan #globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
                globals()['q25_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
                globals()['q75_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
                globals()['std_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
             #
             try:
                globals()['mean_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                globals()['q25_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.percentile(globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],25)
                globals()['q75_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.percentile(globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],75)
                globals()['std_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.std(globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             # If the values are nans
             except:
                globals()['mean_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)] = np.nan #globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
                globals()['q25_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
                globals()['q75_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
                globals()['std_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]  = np.nan
             # Mean of the OBS
             globals()['mean_obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             globals()['mean_obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])

         print ('..Done!')  
   
         # Compute the date array
         time_var=pd.date_range(datetime.date(start_yy, start_mm, start_dd),datetime.date(end_yy, end_mm, end_dd))
         print ('time_var',time_var.shape,time_var)

         #####################
         if flag_mean == 1 :

            # MEAN PLOT RMSD and MSD
            fig = plt.figure(figsize=(8,10))
            plt.rc('font', size=12)
            fig_name = workdir+'qqmean_'+var+'_RMSD_MSD_'+str(depths_defn[depth_idx])+'_'+str(start_date)+'-'+str(end_date)+'_'+str(area_code)+'.png'
            print ('Plot: ',fig_name)

            # 1st PLOT: RMSD
            plt.subplot(2,1,1)
            # Plot each field
            fields_2_include=[-156, -132, -108, -84, -60, -36,-12, 12, 36, 60, 84, 108, 132, 156]
            fields_defn = ['1 Day','2 Day','3 Day','4 Day','5 Day','6 Day','7 Day']
            fields_defn =  np.array(fields_defn)
            p_rmsd_1=[]
            f_rmsd_1=[]
            p_rmsd_2=[]
            f_rmsd_2=[] 
            p_std_1=[]
            f_std_1=[]
            p_std_2=[]
            f_std_2=[]
            p_rmsd_q25_1=[]
            f_rmsd_q25_1=[]
            p_rmsd_q25_2=[]
            f_rmsd_q25_2=[]
            p_rmsd_q75_1=[]
            f_rmsd_q75_1=[]
            p_rmsd_q75_2=[]
            f_rmsd_q75_2=[]
            p_rmsd_std_1=[]
            f_rmsd_std_1=[]
            p_rmsd_std_2=[]
            f_rmsd_std_2=[]
            for field_idx,field in enumerate(fields_2_include):
                  if field <0 :
                     try:
                        p_rmsd_1.append(float(globals()['mean_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        p_std_1.append(float(globals()['mean_std_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        p_rmsd_q25_1.append(float(globals()['q25_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        p_rmsd_q75_1.append(float(globals()['q75_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        p_rmsd_std_1.append(float(globals()['std_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        p_rmsd_1.append(np.nan)
                        p_std_1.append(np.nan)
                        p_rmsd_q25_1.append(np.nan)
                        p_rmsd_q75_1.append(np.nan)
                        p_rmsd_std_1.append(np.nan)
                     try:
                        p_rmsd_2.append(float(globals()['mean_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        p_std_1.append(float(globals()['mean_std_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        p_rmsd_q25_2.append(float(globals()['q25_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        p_rmsd_q75_2.append(float(globals()['q75_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        p_rmsd_std_2.append(float(globals()['std_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        p_rmsd_2.append(np.nan)
                        p_std_2.append(np.nan)
                        p_rmsd_q25_2.append(np.nan)
                        p_rmsd_q75_2.append(np.nan)
                        p_rmsd_std_2.append(np.nan)
                  else:
                     try:
                        f_rmsd_1.append(float(globals()['mean_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        f_std_1.append(float(globals()['mean_std_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        f_rmsd_q25_1.append(float(globals()['q25_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        f_rmsd_q75_1.append(float(globals()['q75_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        f_rmsd_std_1.append(float(globals()['std_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        f_rmsd_1.append(np.nan)
                        f_std_1.append(np.nan)
                        f_rmsd_q25_1.append(np.nan)
                        f_rmsd_q75_1.append(np.nan)
                        f_rmsd_std_1.append(np.nan)
                     try:
                        f_rmsd_2.append(float(globals()['mean_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        f_std_2.append(float(globals()['mean_std_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        f_rmsd_q25_2.append(float(globals()['q25_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        f_rmsd_q75_2.append(float(globals()['q75_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                        f_rmsd_std_2.append(float(globals()['std_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        f_rmsd_2.append(np.nan)
                        f_std_2.append(np.nan)
                        f_rmsd_q25_2.append(np.nan)
                        f_rmsd_q75_2.append(np.nan)
                        f_rmsd_std_2.append(np.nan)
            #
            # Set the correct order to the persistence values
            p_rmsd_1=p_rmsd_1[::-1]
            p_rmsd_2=p_rmsd_2[::-1]
            p_rmsd_q25_1=p_rmsd_q25_1[::-1]
            p_rmsd_q25_2=p_rmsd_q25_2[::-1]
            p_rmsd_q75_1=p_rmsd_q75_1[::-1]
            p_rmsd_q75_2=p_rmsd_q75_2[::-1]
            p_rmsd_std_1=p_rmsd_std_1[::-1]
            p_rmsd_std_2=p_rmsd_std_2[::-1]

            # Concatenate the arrays:
            p_rmsd_q25q75_1 = np.stack((p_rmsd_q25_1,p_rmsd_q75_1), axis=0)    
            p_rmsd_q25q75_2 = np.stack((p_rmsd_q25_2,p_rmsd_q75_2), axis=0)
            f_rmsd_q25q75_1 = np.stack((f_rmsd_q25_1,f_rmsd_q75_1), axis=0)
            f_rmsd_q25q75_2 = np.stack((f_rmsd_q25_2,f_rmsd_q75_2), axis=0)

            print ('Prova',f_rmsd_std_1)
            plt.errorbar(fields_defn,p_rmsd_1,xerr=None,yerr=p_rmsd_std_1,fmt='o-',color="green",label='Mean RMSD Persistence '+dataset_names[0], markersize=8, capsize=20)
            plt.errorbar(fields_defn,f_rmsd_1,xerr=None,yerr=f_rmsd_std_1,fmt='o-',color="red",label='Mean RMSD Forecast '+dataset_names[0], markersize=8, capsize=20)
            plt.errorbar(fields_defn,p_rmsd_2,xerr=None,yerr=p_rmsd_std_2,fmt='o-',color="blue",label='Mean RMSD Persistence '+dataset_names[1], markersize=8, capsize=20)
            plt.errorbar(fields_defn,f_rmsd_2,xerr=None,yerr=f_rmsd_std_2,fmt='o-',color="orange",label='Mean RMSD Forecast '+dataset_names[1], markersize=8, capsize=20)

            ylabel("Mean RMSD ["+udm[var_idx]+']',fontsize=12)
            plt.grid('on')
            plt.legend(loc='upper left', ncol=1,  shadow=True, fancybox=True, framealpha=0.5, fontsize=12)
            plt.title(str(start_date)+'-'+str(end_date)+' Mean RMSD of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=12)
            
            
            #2nd PLOT: MSD
            plt.subplot(2,1,2)
            # Plot each field
            fields_2_include=[-156, -132, -108, -84, -60, -36,-12, 12, 36, 60, 84, 108, 132, 156]
            fields_defn = ['1 Day','2 Day','3 Day','4 Day','5 Day','6 Day','7 Day']
            fields_defn =  np.array(fields_defn)
            p_msd_1=[]
            f_msd_1=[]
            p_msd_2=[]
            f_msd_2=[]
            for field_idx,field in enumerate(fields_2_include):
                  if field <0 :
                     try:
                        p_msd_1.append(float(globals()['mean_msd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        p_msd_1.append(np.nan)
                     try:
                        p_msd_2.append(float(globals()['mean_msd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        p_msd_2.append(np.nan)
                  else:
                     try:
                        f_msd_1.append(float(globals()['mean_msd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        f_msd_1.append(np.nan)
                     try:
                        f_msd_2.append(float(globals()['mean_msd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        f_msd_2.append(np.nan)
            #
            # Set the correct order to the persistence values
            p_msd_1=p_msd_1[::-1]
            p_msd_2=p_msd_2[::-1]
            plt.plot(fields_defn,p_msd_1,'o-',color="green",label='Mean MSD Persistence '+dataset_names[0])
            plt.plot(fields_defn,f_msd_1,'o-',color="red",label='Mean MSD Forecast '+dataset_names[0])
            plt.plot(fields_defn,p_msd_2,'o-',color="blue",label='Mean MSD Persistence '+dataset_names[1])
            plt.plot(fields_defn,f_msd_2,'o-',color="orange",label='Mean MSD Forecast '+dataset_names[1])

            ylabel("Mean MSD ["+udm[var_idx]+'^2]',fontsize=12)
            plt.grid('on')
            plt.legend(loc='upper left', ncol=1,  shadow=True, fancybox=True, framealpha=0.5, fontsize=12)
            plt.title(str(start_date)+'-'+str(end_date)+' Mean MSD of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=12)

            plt.tight_layout()
            plt.savefig(fig_name,format='png',dpi=1200)
            plt.clf()


            # MEAN PLOT RMSD and ACC
            fig = plt.figure(figsize=(8,10))
            plt.rc('font', size=12)
            fig_name = workdir+'mean_'+var+'_RMSD_ACC_'+str(depths_defn[depth_idx])+'_'+str(start_date)+'-'+str(end_date)+'_'+str(area_code)+'.png'
            print ('Plot: ',fig_name)

            # 1st PLOT: RMSD
            plt.subplot(2,1,1)
            # Plot each field
            fields_2_include=[-156, -132, -108, -84, -60, -36,-12, 12, 36, 60, 84, 108, 132, 156]
            fields_defn = ['1 Day','2 Day','3 Day','4 Day','5 Day','6 Day','7 Day']
            fields_defn =  np.array(fields_defn)
            p_rmsd_1=[]
            f_rmsd_1=[]
            p_rmsd_2=[]
            f_rmsd_2=[]
            for field_idx,field in enumerate(fields_2_include):
                  if field <0 :
                     try:
                        p_rmsd_1.append(float(globals()['mean_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        p_rmsd_1.append(np.nan)
                     try:
                        p_rmsd_2.append(float(globals()['mean_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        p_rmsd_2.append(np.nan)
                  else:
                     try:
                        f_rmsd_1.append(float(globals()['mean_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        f_rmsd_1.append(np.nan)
                     try:
                        f_rmsd_2.append(float(globals()['mean_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        f_rmsd_2.append(np.nan)
            #
            # Set the correct order to the persistence values
            p_rmsd_1=p_rmsd_1[::-1]
            p_rmsd_2=p_rmsd_2[::-1]
            plt.plot(fields_defn,p_rmsd_1,'o-',color="green",label='Mean RMSD Persistence '+dataset_names[0])
            plt.plot(fields_defn,f_rmsd_1,'o-',color="red",label='Mean RMSD Forecast '+dataset_names[0])
            plt.plot(fields_defn,p_rmsd_2,'o-',color="blue",label='Mean RMSD Persistence '+dataset_names[1])
            plt.plot(fields_defn,f_rmsd_2,'o-',color="orange",label='Mean RMSD Forecast '+dataset_names[1])

            ylabel("Mean RMSD ["+udm[var_idx]+']',fontsize=12)
            plt.grid('on')
            plt.legend(loc='upper left', ncol=1,  shadow=True, fancybox=True, framealpha=0.5, fontsize=12)
            plt.title(str(start_date)+'-'+str(end_date)+' Mean RMSD of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=12)

            #2nd PLOT: ACC
            plt.subplot(2,1,2)
            # Plot each field
            p_acc_1=[]
            f_acc_1=[]
            p_acc_2=[]
            f_acc_2=[]
            for field_idx,field in enumerate(fields_2_include):
                  if field <0 :
                     try:
                        p_acc_1.append(float(globals()['mean_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        p_acc_1.append(np.nan)
                     try:
                        p_acc_2.append(float(globals()['mean_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        p_acc_2.append(np.nan)
                  else:
                     try:
                        f_acc_1.append(float(globals()['mean_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        f_acc_1.append(np.nan)
                     try:
                        f_acc_2.append(float(globals()['mean_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                     except:
                        f_acc_2.append(np.nan)

            # Set the correct order for the persistence values
            p_acc_1=p_acc_1[::-1]
            p_acc_2=p_acc_2[::-1]

            plt.plot(fields_defn,p_acc_1,'-o',color="green",label='Mean ACC Persistence '+dataset_names[0])
            plt.plot(fields_defn,f_acc_1,'-o',color="red",label='Mean ACC Forecast '+dataset_names[0])
            plt.plot(fields_defn,p_acc_2,'-o',color="blue",label='Mean ACC Persistence '+dataset_names[1])
            plt.plot(fields_defn,f_acc_2,'-o',color="orange",label='Mean ACC Forecast '+dataset_names[1])

            ylabel("Mean ACC",fontsize=12)
            plt.grid('on')
            plt.legend(loc='upper right', ncol=1,  shadow=True, fancybox=True, framealpha=0.5, fontsize=12)
            plt.title(str(start_date)+'-'+str(end_date)+' Mean ACC of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=12)

            plt.tight_layout()
            plt.savefig(fig_name,format='png',dpi=1200)
            plt.clf()
                                                                                                                                        
         #################### TIME SERIES PLOTS ####################3
         if flag_ts == 1 :

            # 1) RMSD TS PLOT
            fig = plt.figure(0,figsize=(11,5))
            plt.rc('font', size=12)
            fig_name = workdir+var+'_RMSD_'+str(depths_defn[depth_idx])+'_'+str(start_date)+'-'+str(end_date)+'_'+str(area_code)+'_nopers_obs.png'
            print ('Plot: ',fig_name)
      
            # Obs on the right axes 
            ax1 = fig.add_subplot(111)
            if flag_rolling_mean == 1:
               lo_1 = np.squeeze(pd.DataFrame(globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean())
            else:
               lo_1 = np.squeeze(np.array(globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))

            globals()['line_obs_1_'+str(field_idx)] = ax1.fill_between(time_var,lo_1,0,color="navy", label='Obs num '+dataset_names[0],alpha=0.4)

            if flag_rolling_mean == 1:
               lo_2 = np.squeeze(pd.DataFrame(globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean())
            else:
              lo_2 = np.squeeze(np.array(globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))

            globals()['line_obs_2_'+str(field_idx)] = ax1.fill_between(time_var,lo_2,0,color="red", label='Obs num '+dataset_names[1],alpha=0.2)

            ax1.yaxis.tick_right()
            ax1.yaxis.set_label_position("right")
            ylabel("N. OBS",fontsize=12,color="black")
            ax1.yaxis.label.set_color('gray')
            ax1.spines['right'].set_color('gray')
      
            # RMSDs on the left axes
            ax = fig.add_subplot(111, sharex=ax1, frameon=False)
      
            # Loop on fields to be plotted
            fields_2_include=[-156, -132, -108, -84, -60, -36,-12, 12, 36, 60, 84, 108, 132, 156]
            fields_defn_ts=['pers 156h','pers 132h','pers 108h','pers 84h','pers 60h','pers 36h','pers 12h','fcst 1d','fcst 2d','fcst 3d','fcst 4d','fcst 5d','fcst 6d','fcst 7d']
            # TMP to remove the persistence:
            #colors = pl.cm.jet_r(np.linspace(0,1,len(fields_2_include)))
            colors = pl.cm.jet_r(np.linspace(0,1,7))
            for field_idx,field in enumerate(fields_2_include):
                # Work only on required fields
                   if flag_rolling_mean == 1:
                      li = pd.DataFrame(np.squeeze(globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])).rolling(rolling_mean_days).mean()
                   else:
                      li = globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)] 
                      mean_li = np.mean(li)
                   # TMP to remove the persistence:
                   #globals()['line_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx],label=fields_defn_ts[field_idx]+' '+dataset_names[0]+' mean='+str(round(mean_li,3))+udm[var_idx],linewidth=1.5)
                   if field_idx > 6 :
                      globals()['line_1_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[0]+' mean='+str(round(mean_li,3))+udm[var_idx],marker='o',linestyle='-',linewidth=1.5)
                      #globals()['line_1_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[0]+' mean='+str(round(mean_li,3))+udm[var_idx]+'(t0='+str(np.round(li[0],3))+udm[var_idx]+')',marker='o',linestyle='-',linewidth=1.5)
                   #
                   if flag_rolling_mean == 1:
                      li_2 = pd.DataFrame(globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean()
                   else:
                      li_2 = globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
                      mean_li_2 = np.mean(li_2)
                   # TMP to remove the persistence:
                   #globals()['line_2_'+str(field_idx)] = ax.plot(time_var,li_2,color=colors[field_idx],label=fields_defn_ts[field_idx]+' '+dataset_names[1]+' mean='+str(round(mean_li_2,3))+udm[var_idx],linestyle='dashed',linewidth=1.5)
                   if field_idx > 6 :
                      globals()['line_2_'+str(field_idx)] = ax.plot(time_var,li_2,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[1]+' mean='+str(round(mean_li_2,3))+udm[var_idx],marker='*',linestyle='dashed',linewidth=1.5)
                      #globals()['line_2_'+str(field_idx)] = ax.plot(time_var,li_2,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[1]+' mean='+str(round(mean_li_2,3))+udm[var_idx]+'(t0='+str(np.round(li_2[0],3))+udm[var_idx]+')',marker='*',linestyle='dashed',linewidth=1.5)

            ylabel("RMSD ["+udm[var_idx]+']',fontsize=12)
            plt.axhline(linewidth=2, color='black')
            ax.grid('on')
            if flag_rolling_mean == 1:
               plt.title(var+' RMSD of '+str(rolling_mean_days)+' days avg at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=12)
            else:
               plt.title(var+' RMSD at '+str(depths_defn[depth_idx])+' m - '+str(start_date)+'-'+str(end_date)+' - '+ area_names[area_code] ,fontsize=12)
            #ax.xaxis.set_major_locator(mdates.YearLocator())
            #ax.xaxis.set_minor_locator(mdates.MonthLocator((1,4,7,10)))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator())
            #ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y"))
            #ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y-%m"))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
            ax.margins(x=0)
            plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
            ax.spines['right'].set_color('white')  

            # Legend
            # TMP to remove the persistence (ncol=1 instead on ncol=2):
            plt.legend(loc='lower right', ncol=1,  shadow=True, fancybox=True, framealpha=0.5, fontsize=6)
            
            # time axis range
            ax.set_xlim([time_var[0] - timedelta(days=1),time_var[-1] + timedelta(days=1)]) #([datetime.date(2014, 1, 26), datetime.date(2014, 2, 1)])

            plt.tight_layout()
            plt.savefig(fig_name,format='png',dpi=1200)
            plt.clf()

            # 2) MSD TS PLOT
            fig = plt.figure(0,figsize=(11,5))
            plt.rc('font', size=12)
            fig_name = workdir+var+'_MSD_'+str(depths_defn[depth_idx])+'_'+str(start_date)+'-'+str(end_date)+'_'+str(area_code)+'_nopers_obs.png'
            print ('Plot: ',fig_name)

            # Obs on the right axes 
            ax1 = fig.add_subplot(111)
            if flag_rolling_mean == 1:
               lo_1 = np.squeeze(pd.DataFrame(globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean())
            else:
               lo_1 = np.squeeze(np.array(globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
            globals()['line_obs_1_'+str(field_idx)] = ax1.fill_between(time_var,lo_1,0,color="navy", label='Obs num '+dataset_names[0],alpha=0.4)

            if flag_rolling_mean == 1:
               lo_2 = np.squeeze(pd.DataFrame(globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean())
            else:
               lo_2 = np.squeeze(np.array(globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))

            globals()['line_obs_2_'+str(field_idx)] = ax1.fill_between(time_var,lo_2,0,color="red", label='Obs num '+dataset_names[1],alpha=0.2)

            ax1.yaxis.tick_right()
            ax1.yaxis.set_label_position("right")
            ylabel("N. OBS",fontsize=12,color="black")
            ax1.yaxis.label.set_color('gray')
            ax1.spines['right'].set_color('gray')

            # RMSDs on the left axes
            ax = fig.add_subplot(111, sharex=ax1, frameon=False)

            # Loop on fields to be plotted
            fields_2_include=[-156, -132, -108, -84, -60, -36,-12, 12, 36, 60, 84, 108, 132, 156]
            fields_defn_ts=['pers 156h','pers 132h','pers 108h','pers 84h','pers 60h','pers 36h','pers 12h','fcst 1d','fcst 2d','fcst 3d','fcst 4d','fcst 5d','fcst 6d','fcst 7d']
            # TMP to remove the persistence:
            #colors = pl.cm.jet_r(np.linspace(0,1,len(fields_2_include)))
            colors = pl.cm.jet_r(np.linspace(0,1,7))
            for field_idx,field in enumerate(fields_2_include):
                # Work only on required fields
                   if flag_rolling_mean == 1:
                      li = pd.DataFrame(np.squeeze(globals()['msd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])).rolling(rolling_mean_days).mean()
                   else:
                      li = globals()['msd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
                      mean_li = np.mean(li)
                   # TMP to remove the persistence:
                   #globals()['line_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx],label=fields_defn_ts[field_idx]+' '+dataset_names[0]+' mean='+str(round(mean_li,3))+udm[var_idx]+'^2]',linewidth=1.5)
                   if field_idx > 6 :
                      globals()['line_1_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[0]+' mean='+str(round(mean_li,3))+udm[var_idx]+'^2]',marker='o',linestyle='-',linewidth=1.5)
                      #globals()['line_1_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[0]+' mean='+str(round(mean_li,3))+udm[var_idx]+'^2]'+'(t0='+str(np.round(li[0],3))+udm[var_idx]+'^2]'+')',marker='o',linestyle='-',linewidth=1.5)
                   #
                   if flag_rolling_mean == 1:
                      li_2 = pd.DataFrame(globals()['msd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean()
                   else:
                      li_2 = globals()['msd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
                      mean_li_2 = np.mean(li_2)
                   # TMP to remove the persistence:
                   #globals()['line_2_'+str(field_idx)] = ax.plot(time_var,li_2,color=colors[field_idx],label=fields_defn_ts[field_idx]+' '+dataset_names[1]+' mean='+str(round(mean_li_2,3))+udm[var_idx],linestyle='dashed',linewidth=1.5)
                   if field_idx > 6 :
                      globals()['line_2_'+str(field_idx)] = ax.plot(time_var,li_2,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[1]+' mean='+str(round(mean_li_2,3))+udm[var_idx],marker='*',linestyle='dashed',linewidth=1.5)
                      #globals()['line_2_'+str(field_idx)] = ax.plot(time_var,li_2,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[1]+' mean='+str(round(mean_li_2,3))+udm[var_idx]+'(t0='+str(np.round(li_2[0],3))+udm[var_idx]+')',marker='*',linestyle='dashed',linewidth=1.5)

            ylabel("MSD ["+udm[var_idx]+'^2]'+']',fontsize=12)
            plt.axhline(linewidth=2, color='black')
            ax.grid('on')
            if flag_rolling_mean == 1:
               plt.title(var+' MSD of '+str(rolling_mean_days)+' days avg at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=12)
            else:
               plt.title(var+' MSD at '+str(depths_defn[depth_idx])+' m - '+str(start_date)+'-'+str(end_date)+' - '+ area_names[area_code] ,fontsize=12)
            #ax.xaxis.set_major_locator(mdates.YearLocator())
            #ax.xaxis.set_minor_locator(mdates.MonthLocator((1,4,7,10)))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator())
            #ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y"))
            #ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y-%m"))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
            ax.margins(x=0)
            plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
            ax.spines['right'].set_color('white')

            # Legend
            # TMP to remove the persistence (ncol=1 instead on ncol=2):
            plt.legend(loc='lower right', ncol=1,  shadow=True, fancybox=True, framealpha=0.5, fontsize=6)

            # time axis range
            ax.set_xlim([time_var[0] - timedelta(days=1),time_var[-1] + timedelta(days=1)]) #([datetime.date(2014, 1, 26), datetime.date(2014, 2, 1)])

            plt.tight_layout()
            plt.savefig(fig_name,format='png',dpi=1200)
            plt.clf()

      
            # 3) ACC TS PLOT
            fig = plt.figure(0,figsize=(11,5))
            plt.rc('font', size=12)
            fig_name = workdir+var+'_ACC_'+str(depths_defn[depth_idx])+'_'+str(start_date)+'-'+str(end_date)+'_'+str(area_code)+'_nopers_obs.png'
            print ('Plot: ',fig_name)

            # Obs on the right axes 
            ax1 = fig.add_subplot(111)
            if flag_rolling_mean == 1:
               lo_1 = np.squeeze(pd.DataFrame(globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean())
            else:
               lo_1 = np.squeeze(np.array(globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
            globals()['line_obs_1_'+str(field_idx)] = ax1.fill_between(time_var,lo_1,0,color="navy", label='Obs num '+dataset_names[0],alpha=0.4)

            if flag_rolling_mean == 1:
               lo_2 = np.squeeze(pd.DataFrame(globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean())
            else:
               lo_2 = np.squeeze(np.array(globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))

            globals()['line_obs_2_'+str(field_idx)] = ax1.fill_between(time_var,lo_2,0,color="red", label='Obs num '+dataset_names[1],alpha=0.2)

            ax1.yaxis.tick_right()
            ax1.yaxis.set_label_position("right")
            ylabel("N. OBS",fontsize=12,color="black")
            ax1.yaxis.label.set_color('gray')
            ax1.spines['right'].set_color('gray')

            # ACCs on the left axes
            ax = fig.add_subplot(111, sharex=ax1, frameon=False)

            # Loop on fields to be plotted
            fields_2_include=[-156, -132, -108, -84, -60, -36,-12, 12, 36, 60, 84, 108, 132, 156]
            fields_defn_ts=['pers 156h','pers 132h','pers 108h','pers 84h','pers 60h','pers 36h','pers 12h','fcst 1d','fcst 2d','fcst 3d','fcst 4d','fcst 5d','fcst 6d','fcst 7d']
            # TMP to remove the persistence:
            #colors = pl.cm.jet_r(np.linspace(0,1,len(fields_2_include)))
            colors = pl.cm.jet_r(np.linspace(0,1,7))
            for field_idx,field in enumerate(fields_2_include):
                # Work only on required fields
                   if flag_rolling_mean == 1:
                      li = pd.DataFrame(np.squeeze(globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])).rolling(rolling_mean_days).mean()
                   else:
                      li = globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
                      mean_li = np.mean(li)
                   # TMP to remove the persistence:
                   #globals()['line_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx],label=fields_defn_ts[field_idx]+' '+dataset_names[0]+' mean='+str(round(mean_li,3)),linewidth=1.5)
                   if field_idx > 6 :
                      globals()['line_1_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[0]+' mean='+str(round(mean_li,3)),marker='o',linestyle='-',linewidth=1.5)
                      #globals()['line_1_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[0]+' mean='+str(round(mean_li,3))+'(t0='+str(np.round(li[0],3))+')',marker='o',linestyle='-',linewidth=1.5)
                   #
                   if flag_rolling_mean == 1:
                      li_2 = pd.DataFrame(globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean()
                   else:
                      li_2 = globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
                      mean_li_2 = np.mean(li_2)
                   # TMP to remove the persistence:
                   #globals()['line_2_'+str(field_idx)] = ax.plot(time_var,li_2,color=colors[field_idx],label=fields_defn_ts[field_idx]+' '+dataset_names[1]+' mean='+str(round(mean_li_2,3)),linestyle='dashed',linewidth=1.5)
                   if field_idx > 6 :
                      globals()['line_2_'+str(field_idx)] = ax.plot(time_var,li_2,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[1]+' mean='+str(round(mean_li_2,3)),marker='*',linestyle='dashed',linewidth=1.5)
                      #globals()['line_2_'+str(field_idx)] = ax.plot(time_var,li_2,color=colors[field_idx-7],label=fields_defn_ts[field_idx]+' '+dataset_names[1]+' mean='+str(round(mean_li_2,3))+'(t0='+str(np.round(li_2[0],3))+')',marker='*',linestyle='dashed',linewidth=1.5)

            ylabel("ACC ",fontsize=12)
            plt.axhline(linewidth=2, color='black')
            ax.grid('on')
            if flag_rolling_mean == 1:
               plt.title(var+' ACC of '+str(rolling_mean_days)+' days avg at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=12)
            else:
               plt.title(var+' ACC at '+str(depths_defn[depth_idx])+' m - '+str(start_date)+'-'+str(end_date)+' - '+ area_names[area_code] ,fontsize=12)
            #ax.xaxis.set_major_locator(mdates.YearLocator())
            #ax.xaxis.set_minor_locator(mdates.MonthLocator((1,4,7,10)))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator())
            #ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y"))
            #ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y-%m"))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
            ax.margins(x=0)
            plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
            ax.spines['right'].set_color('white')

            # Legend
            # TMP to remove the persistence (ncol=1 instead on ncol=2):
            plt.legend(loc='lower right', ncol=1,  shadow=True, fancybox=True, framealpha=0.5, fontsize=6)

            # time axis range
            ax.set_xlim([time_var[0] - timedelta(days=1),time_var[-1] + timedelta(days=1)]) #([datetime.date(2014, 1, 26), datetime.date(2014, 2, 1)])

            plt.tight_layout()
            plt.savefig(fig_name,format='png',dpi=1200)
            plt.clf()

   
         #######################
