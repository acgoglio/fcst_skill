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
workdir = '/work/oda/ag15419/tmp/Ana_Fcst_2023_2datasets/'

# -- Period --
start_date = 20230101
end_date   = 20231231

# -- Analysis type --
flag_ts = 0
flag_mean = 1

# -- Area code --
area_names = ["Mediterranean Sea","Alboran Sea","South West Med western part","North West Med","South West Med eastern part","Tyrrhenian Sea southern part","Tyrrhenian Sea northern part","Ionian Sea western part","Ionian Sea south-eastern part","Ionian Sea north-eastern part","Adriatic Sea southern part","Adriatic Sea northern part","Levantine Sea western part","Aegean Sea","Levantine Sea central-northern part","Levantine Sea central-southern part","Levantine Sea eastern part"]

# ---  Input archive ---
input_dir          ='/data/opa/mfs/MFS_EAS7v1/allout/output-QVR/'
input_dir_2        ='/data/opa/mfs/MFS_EAS6v82/allout/output-QVR/'
input_vars = ['salinity','sla','sstl3s','sst','temperature'] # Do not change the order..
input_field_in_filename =['PSAL','SSH','SSTL3S','SSTL4','TEMP']
udm        = ['PSU','cm','$^{\circ}$C','$^{\circ}$C','$^{\circ}$C']

# --- Set the num of days to be included in the rolling mean ---
rolling_mean_days = 30

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
          depths      = [10, 30, 60, 100, 150, 300, 600, 1000, 2000]
          depths_defn = ['0-10', '10-30', '30-60', '60-100', '100-150', '150-300', '300-600', '600-1000', '1000-2000']
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
           if field == -12 or field == 12 or field == 36 or field == 60 or field == 84 or field == 108 or field == 132 or field == 156 :
             print ('I am going to extract ',fields_defn[field_idx])
             # Root Mean Squared Diff
             globals()['rmsd_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             ## Bias computed as mean of product - mean of reference
             #globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Anomaly Correlation
             globals()['acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             ## Obs num
             #globals()['obs_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
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
                     file_to_open=input_dir+str(yy)+str(mm)+str(dd_dir)+'/'+str(yy)+str(mm)+str(dd)+'.'+input_field_in_filename[var_idx]+'.nc'
                     file_to_open_2=input_dir_2+str(yy)+str(mm)+str(dd_dir)+'/'+str(yy)+str(mm)+str(dd)+'.'+input_field_in_filename[var_idx]+'.nc'
                     # check the existence of the file and open it
                     if glob.glob(file_to_open): 
                        print ('Found date ',yy,mm,dd)
                        #print ('I am opening file: ',file_to_open)
                        fh = ncdf.Dataset(file_to_open,mode='r')
                        time_r = fh.variables['time'][:]
                        # var(time, forecasts, depths, metrics, areas) ;
                        var_msd  = fh.variables['stats_'+var][:,field_idx,depth_idx,3,area_code]
                        #var_bias = fh.variables['stats_'+var][:,field_idx,depth_idx,1,area_code] - fh.variables['stats_'+var][:,field_idx,depth_idx,2,area_code]
                        #var_bias[var_bias > 1000] = np.nan
                        var_acc = fh.variables['stats_'+var][:,field_idx,depth_idx,7,area_code]
                        var_acc[var_acc > 1000] = np.nan
                        #var_obs  = fh.variables['stats_'+var][:,field_idx,depth_idx,0,area_code]
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
                        #var_obs   = np.nan #np.empty(days_num)

                     # check the existence of the file and open it
                     if glob.glob(file_to_open_2):
                        print ('Found date ',yy,mm,dd)
                        print ('I am opening file: ',file_to_open_2)
                        fh = ncdf.Dataset(file_to_open_2,mode='r')
                        time_r_2 = fh.variables['time'][:]
                        # var(time, forecasts, depths, metrics, areas) ;
                        var_msd_2  = fh.variables['stats_'+var][:,field_idx,depth_idx,3,area_code]
                        #var_bias = fh.variables['stats_'+var][:,field_idx,depth_idx,1,area_code] - fh.variables['stats_'+var][:,field_idx,depth_idx,2,area_code]
                        #var_bias[var_bias > 1000] = np.nan
                        var_acc_2 = fh.variables['stats_'+var][:,field_idx,depth_idx,7,area_code]
                        var_acc_2[var_acc_2 > 1000] = np.nan
                        #var_obs_2  = fh.variables['stats_'+var][:,field_idx,depth_idx,0,area_code]
                        fh.close()
                        # Check the num of days
                        days_num_infile_2 = len(np.array(time_r_2))
                        print ('days_num ',days_num_infile_2)
                        if days_num!= days_num_infile_2:
                           print ('WARNING: Issues with days num in the input file!')
                           print ('A single day is expected for each input file..')
                     else:
                        #print ('WARNING: input file NOT found for date ',yy,mm,dd)
                        var_msd_2   = np.nan #np.empty(days_num)
                        #var_bias  = np.nan np.empty(days_num)
                        var_acc_2  = np.nan #np.empty(days_num)
                        #var_obs_2   = np.nan #np.empty(days_num)
                     # Compute the RMSD (time, forecasts, depths, metrics, areas) ad sqrt(msd)
                     try:
                        globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(sqrt(var_msd_2)) #extend(np.sqrt(var_msd[:])) 
                     except:
                        globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_msd_2) #extend(np.array(var_msd)) #[:]))
                     # Read the bias
                     #globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_bias) #extend(np.array(var_bias[:]))
                     # Read the anomaly correlation
                     globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_acc_2) #extend(var_acc) #(np.array(var_acc)) #[:]))
                     ## Read the num of obs in first loop iteration
                     #globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].append(var_obs_2) #extend(var_obs) #(np.array(var_obs)) #[:]))
             # compute the mean values on the whole period
             # Mean of the RMSD
             globals()['mean_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             # Mean of the ACC
             globals()['mean_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
             ## Mean of the OBS
             #globals()['mean_obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=np.nanmean(globals()['obs_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
         print ('..Done!')  
   
         # Compute the date array
         time_var=pd.date_range(datetime.date(start_yy, start_mm, start_dd),datetime.date(end_yy, end_mm, end_dd))

         #####################
         if flag_mean == 1 :

            # MEAN PLOT
            fig = plt.figure(figsize=(12,15))
            plt.rc('font', size=18)
            fig_name = workdir+'mean_'+var+'_RMSD_ACC_'+str(depth)+'_'+str(start_yy)+'-'+str(end_yy)+'_'+str(area_code)+'.png'
            print ('Plot: ',fig_name)

            # PLOT 1
            plt.subplot(2,1,1)
            # Plot each field
            fields_2_include=[-12, 12, 36, 60, 84, 108, 132, 156]
            fields_defn = ['pers 1d','fcst 1d','fcst 2d','fcst 3d','fcst 4d','fcst 5d','fcst 6d','fcst 7d']
            fields_defn =  np.array(fields_defn)

            for field_idx,field in enumerate(fields_2_include):
                  l_rmsd = float(globals()['mean_rmsd_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                  l_rmsd_2 = float(globals()['mean_rmsd_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                  #
                  if field == -12:
                     plt.plot(fields_defn[field_idx],l_rmsd,'o',color="red",label='Mean RMSD 1')
                     plt.plot(fields_defn[field_idx],l_rmsd_2,'o',color="blue",label='Mean RMSD 2')
                  else:
                     plt.plot(fields_defn[field_idx],l_rmsd,'o-',color="red",label='Mean RMSD 1')
                     plt.plot(fields_defn[field_idx],l_rmsd_2,'o-',color="blue",label='Mean RMSD 2')
                  plt.text(fields_defn[field_idx],l_rmsd,str(round(l_rmsd,3)),fontsize=15,color="red")
                  plt.text(fields_defn[field_idx],l_rmsd_2,str(round(l_rmsd,3)),fontsize=15,color="blue")
            ylabel("Mean RMSD ["+udm[var_idx]+']',fontsize=16)

            plt.grid('on')
            plt.title(str(start_yy)+'-'+str(end_yy)+' Mean RMSD of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=18)

            #PLOT 2
            plt.subplot(2,1,2)
            # Plot each field
            for field_idx,field in enumerate(fields_2_include):
                  l_acc = float(globals()['mean_acc_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                  l_acc_2 = float(globals()['mean_acc_2_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)])
                  #
                  if field == -12:
                     plt.plot(fields_defn[field_idx],l_acc,'o',color="red",label='Mean ACC')
                     plt.plot(fields_defn[field_idx],l_acc_2,'o',color="blue",label='Mean ACC')
                  else:
                     plt.plot(fields_defn[field_idx],l_acc,'o-',color="red",label='Mean ACC')
                     plt.plot(fields_defn[field_idx],l_acc_2,'o-',color="blue",label='Mean ACC')
                  # Add values on the plot
                  plt.text(fields_defn[field_idx],l_acc,str(round(l_acc,3)),fontsize=15,color="blue")
            ylabel("Mean ACC ["+udm[var_idx]+']',fontsize=16)

            plt.grid('on')
            plt.title(str(start_yy)+'-'+str(end_yy)+' Mean ACC of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=18)

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
