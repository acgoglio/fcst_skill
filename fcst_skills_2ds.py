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
workdir = '/work/oda/ag15419/tmp/Ana_Fcst/AI/prova_comp_1m/'

# -- Period --
start_date = 20220101
end_date   = 20220131

# -- Analysis type --
flag_ts = 0
flag_mean = 1

# -- Area code --
area_names = ["Mediterranean Sea","Alboran Sea","South West Med western part","North West Med","South West Med eastern part","Tyrrhenian Sea southern part","Tyrrhenian Sea northern part","Ionian Sea western part","Ionian Sea south-eastern part","Ionian Sea north-eastern part","Adriatic Sea southern part","Adriatic Sea northern part","Levantine Sea western part","Aegean Sea","Levantine Sea central-northern part","Levantine Sea central-southern part","Levantine Sea eastern part"]

# --- Datasets Name ---
dataset_names=['VALFOR_18','VALFOR_18_END']

# ---  Input archive ---
input_dir_1             = workdir
input_dir_2             = '/work/opa/ag22216/testVALFOR_18_END/out/' #'/work/oda/ag15419/tmp/Ana_Fcst/AI/prova_comp_1mb/'
input_vars              = ['sla'] #['salinity','sla','sstl3s','sst','temperature'] # Do not change the order..
input_field_in_filename = ['TEMP'] #['TEMP','TEMP','TEMP','TEMP','TEMP'] #['PSAL','SSH','SSTL3S','SSTL4','TEMP']
udm                     = ['cm'] #['PSU','cm','$^{\circ}$C','$^{\circ}$C','$^{\circ}$C']

## --- Set the num of days to be included in the rolling mean for the time-series plot ---
#rolling_mean_days = 30

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
all_months_1 = list(range(1,12+1))
all_months   = [str(i).zfill(2) for i in all_months_1] 
all_months   = np.array(all_months)
all_days_1   = list(range(1,31+1))
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
for area_code,area_name in enumerate(area_names):
   print ('I am working on Med region: ',area_name)
  
   # Loop on vars
   for var_idx,var in enumerate(input_vars):
       print ('I am working on var ',var)
   
       # Loop on vertical layers (1 plot each, if a combination is needed the arrays in the fields loop must include the depth index in the name)
       if var == 'salinity' or var == 'temperature':
          depths      = [10, 30, 60, 100, 150, 300 ]  #300, 600, 1000, 2000]
          depths_defn = ['0-10', '10-30', '30-60', '60-100', '100-150', '150-300' ] #'150-300', '300-600', '600-1000', '1000-2000']
       elif var == 'sla' or var == 'sst' or var == 'sstl3s':
          depths      = [0] 
          depths_defn = ['0']
   
       for depth_idx,depth in enumerate(depths):
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
             globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
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
                for mm in all_months :
                   #print ('Working on month',mm) 
                   for dd_dir in all_days :
                    for dd in all_days :
                     #print ('Working on day',dd)  
                     file_to_open_1=input_dir_1+str(yy)+str(mm)+str(dd)+'.'+input_field_in_filename[var_idx]+'.nc' 
                     file_to_open_2=input_dir_2+str(yy)+str(mm)+str(dd)+'.'+input_field_in_filename[var_idx]+'.nc'
                     #input_dir+str(yy)+str(mm)+str(dd_dir)+'/'+str(yy)+str(mm)+str(dd)+'.'+input_field_in_filename[var_idx]+'.nc'
                     #print ('I am working on files:',file_to_open_1,file_to_open_2)
                     # check the existence of file 1 and open it
                     if glob.glob(file_to_open_1): 
                        print ('Found date ',yy,mm,dd)
                        print ('I am opening file: ',file_to_open_1)
                        fh_1 = ncdf.Dataset(file_to_open_1,mode='r')
                        time_r = fh_1.variables['time'][:]
                        # var(time, forecasts, depths, metrics, areas) ;
                        var_msd_1  = fh_1.variables['stats_'+var][:,field_idx,depth_idx,3,area_code]
                        var_acc_1 = fh_1.variables['stats_'+var][:,field_idx,depth_idx,7,area_code]
                        print ('File 1 max:',np.nanmax(var_acc_1))
                        var_acc_1[var_acc_1 > 1000] = np.nan
                        var_obs_1  = fh_1.variables['stats_'+var][:,field_idx,depth_idx,0,area_code]
                        print ('var_obs:',var_obs_1)
                        fh_1.close()
                        # Check the num of days
                        days_num_infile = len(np.array(time_r))
                        print ('days_num ',days_num_infile)
                        if days_num!= days_num_infile:
                           print ('WARNING: Issues with days num in the input file!')
                           print ('A single day is expected for each input file..')
                     else:
                        #print ('WARNING: input file NOT found for date ',yy,mm,dd)
                        var_msd_1   = np.nan #np.empty(days_num)
                        var_acc_1  = np.nan #np.empty(days_num)
                        var_obs_1   = np.nan #np.empty(days_num)
                     # check the existence of file 2 and open it
                     if glob.glob(file_to_open_2):
                        print ('Found date ',yy,mm,dd)
                        print ('I am opening file: ',file_to_open_2)
                        fh_2 = ncdf.Dataset(file_to_open_2,mode='r')
                        time_r_2 = fh_2.variables['time'][:]
                        # var(time, forecasts, depths, metrics, areas) ;
                        var_msd_2  = fh_2.variables['stats_'+var][:,field_idx,depth_idx,3,area_code]
                        var_acc_2 = fh_2.variables['stats_'+var][:,field_idx,depth_idx,7,area_code]
                        print ('File 2 max:',np.nanmax(var_acc_2))
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
                        #print ('WARNING: input file NOT found for date ',yy,mm,dd)
                        var_msd_2  = np.nan
                        var_acc_2  = np.nan #np.empty(days_num)
                        var_obs_2  = np.nan #np.empty(days_num)                    

                     # Compute the RMSD (time, forecasts, depths, metrics, areas) ad sqrt(msd)
                     try:
                        globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(sqrt(var_msd_1))  
                        globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(sqrt(var_msd_2))
                     except:
                        globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_msd_1) 
                        globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_msd_2)
                     # Read the anomaly correlation
                     globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_acc_1)
                     globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_acc_2)
                     # Read the num of obs in first loop iteration
                     globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_obs_1)
                     globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_obs_2)
             # compute the mean values on the whole period
             # Mean of the RMSD
             try:
                globals()['mean_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             except:
                globals()['mean_rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=globals()['rmsd_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
             try:
                globals()['mean_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             except:
                globals()['mean_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
             # Mean of the ACC
             try:
                globals()['mean_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             except:
                globals()['mean_acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=globals()['acc_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
             try:
                globals()['mean_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             except:
                globals()['mean_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]
             # Mean of the OBS
             globals()['mean_obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['obs_1_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             globals()['mean_obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
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
            print ('PROVA Persistence rmsd',var,str(depth),dataset_names[0],p_rmsd_1)
            print ('PROVA Persistence rmsd',var,str(depth),dataset_names[1],p_rmsd_2)
            print ('PROVA Forecast rmsd',var,str(depth),dataset_names[0],f_rmsd_1)
            print ('PROVA Forecast rmsd',var,str(depth),dataset_names[1],f_rmsd_2)
            plt.plot(fields_defn,p_rmsd_1,'o-',color="green",label='Mean RMSD Persistence '+dataset_names[0])
            plt.plot(fields_defn,f_rmsd_1,'o-',color="red",label='Mean RMSD Forecast '+dataset_names[0])
            plt.plot(fields_defn,p_rmsd_2,'o-',color="blue",label='Mean RMSD Persistence '+dataset_names[1])
            plt.plot(fields_defn,f_rmsd_2,'o-',color="orange",label='Mean RMSD Forecast '+dataset_names[1])

            ylabel("Mean RMSD ["+udm[var_idx]+']',fontsize=16)
            plt.grid('on')
            plt.legend(loc='upper left', ncol=1,  shadow=True, fancybox=True, framealpha=0.5, fontsize=16)
            plt.title(str(start_date)+'-'+str(end_date)+' Mean RMSD of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=18)
            #plt.title(str(start_yy)+'/'+str(start_mm)+'/'+str(start_dd)+'-'+str(end_yy)+'/'+str(end_mm)+'/'+str(end_dd)' Mean RMSD of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=18)
            

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
            # Set the correct order to the persistence values
            p_acc_1=p_acc_1[::-1]
            p_acc_2=p_acc_2[::-1]
            print ('PROVA Persistence acc',var,str(depth),dataset_names[0],p_acc_1)
            print ('PROVA Persistence acc',var,str(depth),dataset_names[1],p_acc_2)
            print ('PROVA Forecast acc',var,str(depth),dataset_names[0],f_acc_1)
            print ('PROVA Forecast acc',var,str(depth),dataset_names[1],f_acc_2)
            plt.plot(fields_defn,p_acc_1,'-o',color="green",label='Mean ACC Persistence '+dataset_names[0])
            plt.plot(fields_defn,f_acc_1,'-o',color="red",label='Mean ACC Forecast '+dataset_names[0])
            plt.plot(fields_defn,p_acc_2,'-o',color="blue",label='Mean ACC Persistence '+dataset_names[1])
            plt.plot(fields_defn,f_acc_2,'-o',color="orange",label='Mean ACC Forecast '+dataset_names[1])

            ylabel("Mean ACC",fontsize=16)
            plt.grid('on')
            plt.legend(loc='upper right', ncol=1,  shadow=True, fancybox=True, framealpha=0.5, fontsize=16)
            plt.title(str(start_date)+'-'+str(end_date)+' Mean ACC of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=18)

            plt.tight_layout()
            plt.savefig(fig_name,format='png',dpi=1200)
            plt.clf()
                                                                                                                                        
#         ####################
#         if flag_ts == 1 :
#            # TS PLOT
#            fig = plt.figure(0,figsize=(11,5))
#            fig_name = workdir+var+'_RMSD_BIAS_'+str(depth)+'_'+str(start_yy)+'-'+str(end_yy)+'_'+str(area_code)+'.png'
#            print ('Plot: ',fig_name)
#      
#            # Obs on the right axes 
#            ax1 = fig.add_subplot(111)
#            if var != 'sst':
#               lo = np.squeeze(pd.DataFrame(globals()['obs_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean())
#            else:
#               print('WARNING: sstl3 obs for sst..')
#            print ('obs',globals()['obs_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean()
#            print ('lo',lo.shape,lo)
#            globals()['line_obs_'+str(field_idx)] = ax1.fill_between(time_var,lo,0,color="gray", label='Obs num',alpha=0.4)
#            ax1.yaxis.tick_right()
#            ax1.yaxis.set_label_position("right")
#            ylabel("N. OBS",fontsize=16,color="gray")
#            ax1.yaxis.label.set_color('gray')
#            ax1.spines['right'].set_color('gray')
#      
#            # First plot
#            ###plt.subplot(2,1,1)
#            # RMSDs and BIAS on the left axes
#            ax = fig.add_subplot(111, sharex=ax1, frameon=False)
#      
#            # Loop on fields to be plotted
#            colors = pl.cm.jet_r(np.linspace(0,len(fields)))
#            for field_idx,field in reversed(list(enumerate(fields))):
#                print ('IDX',field_idx,colors[field_idx])
#                if field != -12 :
#                   li = pd.DataFrame(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean()
#                   q11 = pd.DataFrame(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.25)
#                   q31 = pd.DataFrame(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.75)
#                   globals()['line_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx],label=fields_defn[field_idx],linewidth=1.5)
#                   q1q3=np.squeeze(np.array([[q11],[q31]]))
#                   #globals()['point_'+str(field_idx)] = ax.errorbar(time_var,li,yerr=q1q3,color=colors[field_idx],linewidth=1.5)
#                   #globals()['line_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx],label=fields_defn[field_idx],linewidth=1.5)
#                   #if field != 1 :
#                   li2 = pd.DataFrame(globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean()
#                   q12 = pd.DataFrame(globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.25)
#                   q32 = pd.DataFrame(globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.75)
#                   q1q32=np.squeeze(np.array([[q12],[q32]]))
#                   globals()['line2_'+str(field_idx)] = ax.plot(time_var,li2,'--',color=colors[field_idx],linewidth=1.5)
#                   #globals()['point2_'+str(field_idx)] = ax.errorbar(time_var,li2,yerr=q1q32,color=colors[field_idx],linewidth=1.5)
#                   #globals()['line2_'+str(field_idx)] = ax.plot(time_var,li2,'--',color=colors[field_idx],linewidth=1.5)
#                else:
#                   print ('Rm the 12 hours persistence..')
#           
#            ylabel("RMSD(-)/BIAS(--) ["+udm[var_idx]+']',fontsize=16)
#            plt.axhline(linewidth=2, color='black')
#            ax.grid('on')
#            plt.title(var+' RMSD and bias of '+str(rolling_mean_days)+' days avg at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=16)
#            ax.xaxis.set_major_locator(mdates.YearLocator())
#            ax.xaxis.set_minor_locator(mdates.MonthLocator((1,4,7,10)))
#            ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y"))
#            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
#            ax.margins(x=0)
#            plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
#            ax.spines['right'].set_color('gray')  
#
#            # Legend
#            handles, labels = ax.get_legend_handles_labels()
#            box = ax.get_position()
#            ax.set_position([box.x0, box.y0 + box.height * 0.1,box.width, box.height * 0.9])
#            leg = plt.legend(reversed(handles),reversed(labels),loc='upper center',bbox_to_anchor=(0.5, -0.1), ncol=2,  shadow=True, fancybox=True, fontsize=12) 
#            leg.get_frame().set_alpha(0.3)
#    
#            plt.tight_layout()
#            plt.savefig(fig_name,format='png',dpi=1200)
#            plt.clf()
#      
#            # CORR
#            fig = plt.figure(0,figsize=(11,5))
#            fig_name = workdir+var+'_CORR_'+str(depth)+'_'+str(start_yy)+'-'+str(end_yy)+'_'+str(area_code)+'.png'
#            print ('Plot: ',fig_name)
#      
#            # Obs on the right axes 
#            ax2 = fig.add_subplot(111)
#            globals()['line_obs2_'+str(field_idx)] = ax2.fill_between(time_var,lo,0,color="gray", label='Obs num',alpha=0.4)
#            #(time_var,pd.DataFrame(globals()['obs_'+str(field)+'_'+str(depth)+'_'+var]).rolling(rolling_mean_days).mean(),color="gray", label='Obs num',alpha=0.4)
#            ax2.yaxis.tick_right()
#            ax2.yaxis.set_label_position("right")
#            ylabel("N. OBS",fontsize=16,color="gray")
#            ax2.yaxis.label.set_color('gray')
#            ax2.spines['right'].set_color('gray')
#            #leg = plt.legend(loc='upper right', ncol=2,  shadow=True, fancybox=True, fontsize=12)
#            #leg.get_frame().set_alpha(0.3)
#      
#            # CORR on the left axes
#            ax = fig.add_subplot(111, sharex=ax2, frameon=False)
#      
#            # Loop on fields to be plotted
#            colors = pl.cm.jet_r(np.linspace(0,len(fields)))
#            for field_idx,field in reversed(list(enumerate(fields))):
#                print ('IDX',field_idx,colors[field_idx])
#                if field != -12 :
#                   li3 = pd.DataFrame(globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean()
#                   q13 = pd.DataFrame(globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.25)
#                   q33 = pd.DataFrame(globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.75)
#                   q1q33=np.squeeze(np.array([[q13],[q33]]))
#                   globals()['line3_'+str(field_idx)] = ax.plot(time_var,li3,color=colors[field_idx],label=fields_defn[field_idx],linewidth=1.5)
#                   #globals()['point3_'+str(field_idx)] = ax.errorbar(time_var,li3,yerr=q1q33,color=colors[field_idx],linewidth=1.5)
#                   #globals()['line3_'+str(field_idx)] = ax.plot(time_var,li3,color=colors[field_idx],label=fields_defn[field_idx],linewidth=1.5)
#                else:
#                   print ('Rm the 12 hours persistence..')
#      
#            ylabel("Correlation",fontsize=16)
#            plt.ylim(top=1.0)
#            ax.grid('on')
#            #plt.axhline(linewidth=2, color='black')
#            #plt.title(str(start_yy)+'-'+str(end_yy)+' '+str(rolling_mean_days)+' days average of '+var+' correlation at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=16)
#            plt.title(var+' correlation of '+str(rolling_mean_days)+' days avg at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=16)
#            ax.xaxis.set_major_locator(mdates.YearLocator())
#            ax.xaxis.set_minor_locator(mdates.MonthLocator((1,4,7,10)))
#            ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y"))
#            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
#            ax.margins(x=0)
#            plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
#            ax.spines['right'].set_color('gray')
#
#            # Legend
#            handles, labels = ax.get_legend_handles_labels()
#            box = ax.get_position()
#            ax.set_position([box.x0, box.y0 + box.height * 0.1,box.width, box.height * 0.9])
#            #leg = plt.legend(loc='upper left', ncol=2,  shadow=True, fancybox=True, fontsize=12)
#            leg = plt.legend(reversed(handles),reversed(labels),loc='upper center',bbox_to_anchor=(0.5, -0.1), ncol=2,  shadow=True, fancybox=True, fontsize=12)
#            leg.get_frame().set_alpha(0.3)
#
#            plt.tight_layout()
#            plt.savefig(fig_name,format='png',dpi=1200)
#            plt.clf()
#   
#         #######################
