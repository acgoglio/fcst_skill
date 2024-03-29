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
workdir = '/work/oda/ag15419/tmp/Ana_Fcst_2022/'

# -- Period --
start_yy = 2023
end_yy   = 2023

# -- Analysis type --
flag_ts = 1
flag_mean = 1

# -- Area code --
area_names = ["Mediterranean Sea","Alboran Sea","South West Med western part","North West Med","South West Med eastern part","Tyrrhenian Sea southern part","Tyrrhenian Sea northern part","Ionian Sea western part","Ionian Sea south-eastern part","Ionian Sea north-eastern part","Adriatic Sea southern part","Adriatic Sea northern part","Levantine Sea western part","Aegean Sea","Levantine Sea central-northern part","Levantine Sea central-southern part","Levantine Sea eastern part"]

# ---  Input archive ---
input_dir          ='/data/opa/ag22216/BACKUP_work_ATHENA/QVR/HOMOGENIZED/'
input_prefile_name ='product_quality_stats_MEDSEA-ANALYSISFORECAST-PHY-006-013_'
#
timestep_ini_2017  = ['0101','0401','0701','1001']
timestep_end_2017  = ['0331','0630','0930','1231']
timestep_ini_2018  = timestep_ini_2017
timestep_end_2018  = timestep_end_2017
timestep_ini_2019  = ['0101','0401','0501','0601','0701','0801','0901','1001','1101','1201']
timestep_end_2019  = ['0331','0430','0531','0630','0731','0831','0930','1031','1130','1231']
timestep_ini_2020  = ['0101','0201','0301','0401','0501','0601','0701','0801','0901','1001','1101','1201']
timestep_end_2020  = ['0131','0229','0331','0430','0531','0630','0731','0831','0930','1031','1130','1231']
timestep_ini_2021  = ['0101','0201','0501','0601','0701','0801','0901','1001','1101','1201']
timestep_end_2021  = ['0131','0430','0531','0630','0731','0831','0930','1031','1130','1231']
timestep_ini_2022  = ['0101','0201','0301','0401','0501','0601','0701','0801','0901','1001','1101','1201']
timestep_end_2022  = ['0131','0228','0331','0430','0531','0630','0731','0831','0930','1031','1130','1231']
#
input_vars = ['salinity','sla','sstl3s','sst','temperature'] # Do not change the order..
udm        = ['PSU','cm','$^{\circ}$C','$^{\circ}$C','$^{\circ}$C']

# --- Set the num of days to be included in the rolling mean ---
rolling_mean_days = 30

#############################
# Input checks
if start_yy > end_yy :
   print ('ERROR: start_yy > end_yy!!')
   quit()
else: 
   print ('PERIOD: ',start_yy,end_yy)

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
         fields = [1, 0, -12, 12, 60, 108, 204]
         #fields_defn = ['climatology','analysis','12h hours persistence','12h forecast','60h forecast','108h forecast','204h forecast']
         fields_defn = ['climatology','analysis','12h hours persistence','fcst 1d','fcst 3d','fcst 5d','fcst 9d']
         # Loop on fields
         for field_idx,field in enumerate(fields): 
             print ('I am going to extract ',fields_defn[field_idx])
             # Mean squared error
             globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Bias computed as mean of product - mean of reference
             globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Correlation
             globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Obs num
             globals()['obs_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
             # Time var   
             time_var=[]
            
             # Loop on input files
             for yy in range(start_yy,end_yy+1):
                 print ('Working on year',yy)
                 # Define the type of timestep
                 try:
                    timestep_ini = globals()['timestep_ini_'+str(yy)]
                    timestep_end = globals()['timestep_end_'+str(yy)]
                 except:
                    if yy < 2017 :
                       timestep_ini = timestep_ini_2017
                       timestep_end = timestep_end_2017
                    elif yy > 2022 :
                       timestep_ini = timestep_ini_2022
                       timestep_end = timestep_end_2022
                 print ('File div ',timestep_ini,timestep_end)
   
                 for timestep_idx in range (0,len(timestep_ini)):
                     file_to_open=input_dir+input_prefile_name+str(yy)+timestep_ini[timestep_idx]+'_'+str(yy)+timestep_end[timestep_idx]+".nc"
                     print ('I am opening file: ',file_to_open)
                     # check the existence of the file and open it
                     if glob.glob(file_to_open):
                        fh = ncdf.Dataset(file_to_open,mode='r')
                        time_r = fh.variables['time'][:]
                        # var(time, forecasts, surface, metrics, areas)
                        var_mse  = fh.variables['stats_'+var][:,field_idx,depth_idx,3,area_code]
                        var_bias = fh.variables['stats_'+var][:,field_idx,depth_idx,1,area_code] - fh.variables['stats_'+var][:,field_idx,depth_idx,2,area_code]
                        var_bias[var_bias > 1000] = np.nan
                        var_corr = fh.variables['stats_'+var][:,field_idx,depth_idx,6,area_code]/np.sqrt(fh.variables['stats_'+var][:,field_idx,depth_idx,4,area_code]*fh.variables['stats_'+var][:,field_idx,depth_idx,5,area_code])
                        var_corr[var_corr > 1000] = np.nan
                        #var_corr = fh.variables['stats_'+var][:,field_idx,depth_idx,7,area_code]
                        var_obs  = fh.variables['stats_'+var][:,field_idx,depth_idx,0,area_code]
                        fh.close()
                        # Check the num of days
                        days_num_infile = len(np.array(time_r))
                        print ('days_num ',days_num_infile)
                        mm_ini = timestep_ini[timestep_idx][0:2]
                        dd_ini = timestep_ini[timestep_idx][2:4]
                        mm_end = timestep_end[timestep_idx][0:2]
                        dd_end = timestep_end[timestep_idx][2:4]
                        data_ini = datetime.date(yy,int(mm_ini),int(dd_ini))
                        data_end = datetime.date(yy,int(mm_end),int(dd_end))
                        data_all = pd.date_range(start=data_ini,end=data_end)
                        days_num = len(np.array(data_all))
                        print ('days_num ',days_num_infile)
                        if days_num_infile != days_num:
                           print ('WARNING: Issues with days num!')
                     else:
                        print ('WARNING: input file NOT found!')
                        mm_ini = timestep_ini[timestep_idx][0:2]
                        dd_ini = timestep_ini[timestep_idx][2:4]
                        mm_end = timestep_end[timestep_idx][0:2]
                        dd_end = timestep_end[timestep_idx][2:4]
                        data_ini = datetime.date(yy,int(mm_ini),int(dd_ini))
                        data_end = datetime.date(yy,int(mm_end),int(dd_end))
                        data_all = pd.date_range(start=data_ini,end=data_end)
                        days_num = len(np.array(data_all))
                        print ('days_num ',days_num)
                        var_mse   = np.empty(days_num)
                        var_bias  = np.empty(days_num)
                        var_corr  = np.empty(days_num)
                        var_obs   = np.empty(days_num)
                    
                     # Compute the RMSD (time, forecasts, depths, metrics, areas)
                     try:
                        globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].extend(np.sqrt(var_mse[:])) 
                     except:
                        globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].extend(np.array(var_mse[:]))
                     # Read the bias
                     globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].extend(np.array(var_bias[:]))
                     # Read the correlation
                     globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].extend(np.array(var_corr[:]))
                     # Read the num of obs in first loop iteration
                     globals()['obs_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)].extend(np.array(var_obs[:]))
         print ('..Done!')  
   
         # Compute the date array
         time_var=pd.date_range(datetime.date(start_yy, 1, 1),datetime.date(end_yy, 12, 31))
      
         #####################
         if flag_ts == 1 :
            # TS PLOT
            fig = plt.figure(0,figsize=(11,5))
            fig_name = workdir+var+'_RMSD_BIAS_'+str(depth)+'_'+str(start_yy)+'-'+str(end_yy)+'_'+str(area_code)+'.png'
            print ('Plot: ',fig_name)
      
            # Obs on the right axes 
            ax1 = fig.add_subplot(111)
            if var != 'sst':
               lo = np.squeeze(pd.DataFrame(globals()['obs_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean())
            else:
               print('WARNING: sstl3 obs for sst..')

            globals()['line_obs_'+str(field_idx)] = ax1.fill_between(time_var,lo,0,color="gray", label='Obs num',alpha=0.4)
            ax1.yaxis.tick_right()
            ax1.yaxis.set_label_position("right")
            ylabel("N. OBS",fontsize=16,color="gray")
            ax1.yaxis.label.set_color('gray')
            ax1.spines['right'].set_color('gray')
      
            # First plot
            ###plt.subplot(2,1,1)
            # RMSDs and BIAS on the left axes
            ax = fig.add_subplot(111, sharex=ax1, frameon=False)
      
            # Loop on fields to be plotted
            colors = pl.cm.jet_r(np.linspace(0,len(fields)))
            for field_idx,field in reversed(list(enumerate(fields))):
                print ('IDX',field_idx,colors[field_idx])
                if field != -12 :
                   li = pd.DataFrame(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean()
                   q11 = pd.DataFrame(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.25)
                   q31 = pd.DataFrame(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.75)
                   globals()['line_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx],label=fields_defn[field_idx],linewidth=1.5)
                   q1q3=np.squeeze(np.array([[q11],[q31]]))
                   #globals()['point_'+str(field_idx)] = ax.errorbar(time_var,li,yerr=q1q3,color=colors[field_idx],linewidth=1.5)
                   #globals()['line_'+str(field_idx)] = ax.plot(time_var,li,color=colors[field_idx],label=fields_defn[field_idx],linewidth=1.5)
                   #if field != 1 :
                   li2 = pd.DataFrame(globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean()
                   q12 = pd.DataFrame(globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.25)
                   q32 = pd.DataFrame(globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.75)
                   q1q32=np.squeeze(np.array([[q12],[q32]]))
                   globals()['line2_'+str(field_idx)] = ax.plot(time_var,li2,'--',color=colors[field_idx],linewidth=1.5)
                   #globals()['point2_'+str(field_idx)] = ax.errorbar(time_var,li2,yerr=q1q32,color=colors[field_idx],linewidth=1.5)
                   #globals()['line2_'+str(field_idx)] = ax.plot(time_var,li2,'--',color=colors[field_idx],linewidth=1.5)
                else:
                   print ('Rm the 12 hours persistence..')
           
            ylabel("RMSD(-)/BIAS(--) ["+udm[var_idx]+']',fontsize=16)
            plt.axhline(linewidth=2, color='black')
            ax.grid('on')
            plt.title(var+' RMSD and bias of '+str(rolling_mean_days)+' days avg at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=16)
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_minor_locator(mdates.MonthLocator((1,4,7,10)))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y"))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
            ax.margins(x=0)
            plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
            ax.spines['right'].set_color('gray')  

            # Legend
            handles, labels = ax.get_legend_handles_labels()
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,box.width, box.height * 0.9])
            leg = plt.legend(reversed(handles),reversed(labels),loc='upper center',bbox_to_anchor=(0.5, -0.1), ncol=2,  shadow=True, fancybox=True, fontsize=12) 
            leg.get_frame().set_alpha(0.3)
    
            plt.tight_layout()
            plt.savefig(fig_name,format='png',dpi=1200)
            plt.clf()
      
            # CORR
            fig = plt.figure(0,figsize=(11,5))
            fig_name = workdir+var+'_CORR_'+str(depth)+'_'+str(start_yy)+'-'+str(end_yy)+'_'+str(area_code)+'.png'
            print ('Plot: ',fig_name)
      
            # Obs on the right axes 
            ax2 = fig.add_subplot(111)
            globals()['line_obs2_'+str(field_idx)] = ax2.fill_between(time_var,lo,0,color="gray", label='Obs num',alpha=0.4)
            #(time_var,pd.DataFrame(globals()['obs_'+str(field)+'_'+str(depth)+'_'+var]).rolling(rolling_mean_days).mean(),color="gray", label='Obs num',alpha=0.4)
            ax2.yaxis.tick_right()
            ax2.yaxis.set_label_position("right")
            ylabel("N. OBS",fontsize=16,color="gray")
            ax2.yaxis.label.set_color('gray')
            ax2.spines['right'].set_color('gray')
            #leg = plt.legend(loc='upper right', ncol=2,  shadow=True, fancybox=True, fontsize=12)
            #leg.get_frame().set_alpha(0.3)
      
            # CORR on the left axes
            ax = fig.add_subplot(111, sharex=ax2, frameon=False)
      
            # Loop on fields to be plotted
            colors = pl.cm.jet_r(np.linspace(0,len(fields)))
            for field_idx,field in reversed(list(enumerate(fields))):
                print ('IDX',field_idx,colors[field_idx])
                if field != -12 :
                   li3 = pd.DataFrame(globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).mean()
                   q13 = pd.DataFrame(globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.25)
                   q33 = pd.DataFrame(globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]).rolling(rolling_mean_days).quantile(0.75)
                   q1q33=np.squeeze(np.array([[q13],[q33]]))
                   globals()['line3_'+str(field_idx)] = ax.plot(time_var,li3,color=colors[field_idx],label=fields_defn[field_idx],linewidth=1.5)
                   #globals()['point3_'+str(field_idx)] = ax.errorbar(time_var,li3,yerr=q1q33,color=colors[field_idx],linewidth=1.5)
                   #globals()['line3_'+str(field_idx)] = ax.plot(time_var,li3,color=colors[field_idx],label=fields_defn[field_idx],linewidth=1.5)
                else:
                   print ('Rm the 12 hours persistence..')
      
            ylabel("Correlation",fontsize=16)
            plt.ylim(top=1.0)
            ax.grid('on')
            #plt.axhline(linewidth=2, color='black')
            #plt.title(str(start_yy)+'-'+str(end_yy)+' '+str(rolling_mean_days)+' days average of '+var+' correlation at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=16)
            plt.title(var+' correlation of '+str(rolling_mean_days)+' days avg at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=16)
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_minor_locator(mdates.MonthLocator((1,4,7,10)))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y"))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
            ax.margins(x=0)
            plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
            ax.spines['right'].set_color('gray')

            # Legend
            handles, labels = ax.get_legend_handles_labels()
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,box.width, box.height * 0.9])
            #leg = plt.legend(loc='upper left', ncol=2,  shadow=True, fancybox=True, fontsize=12)
            leg = plt.legend(reversed(handles),reversed(labels),loc='upper center',bbox_to_anchor=(0.5, -0.1), ncol=2,  shadow=True, fancybox=True, fontsize=12)
            leg.get_frame().set_alpha(0.3)

            plt.tight_layout()
            plt.savefig(fig_name,format='png',dpi=1200)
            plt.clf()
   
         #######################
         if flag_mean == 1 :
   
            # MEAN PLOT
            fig = plt.figure(figsize=(12,15)) #(0,figsize=(11,5))
            plt.rc('font', size=18)
            fig_name = workdir+'mean_'+var+'_RMSD_BIAS_CORR_'+str(depth)+'_'+str(start_yy)+'-'+str(end_yy)+'_'+str(area_code)+'.png'
            print ('Plot: ',fig_name)
      
            #Loop on fields to be plotted
            globals()['mean_rmse_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
            globals()['mean_bias_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
            globals()['mean_corr_'+str(depth)+'_'+var+'_'+str(area_code)]=[]

            globals()['q1_rmse_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
            globals()['q1_bias_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
            globals()['q1_corr_'+str(depth)+'_'+var+'_'+str(area_code)]=[]

            globals()['q3_rmse_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
            globals()['q3_bias_'+str(depth)+'_'+var+'_'+str(area_code)]=[]
            globals()['q3_corr_'+str(depth)+'_'+var+'_'+str(area_code)]=[]

            for field_idx,field in enumerate(fields):
                if field != -12 :
                   globals()['mean_rmse_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nanmean(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                   globals()['mean_bias_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nanmean(globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))
                   globals()['mean_corr_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nanmean(globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)]))

                   globals()['q1_rmse_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nanquantile(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],0.25))
                   globals()['q1_bias_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nanquantile(globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],0.25))
                   globals()['q1_corr_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nanquantile(globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],0.25))

                   globals()['q3_rmse_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nanquantile(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],0.75))
                   globals()['q3_bias_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nanquantile(globals()['bias_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],0.75))
                   globals()['q3_corr_'+str(depth)+'_'+var+'_'+str(area_code)].append(np.nanquantile(globals()['corr_'+str(field)+'_'+str(depth)+'_'+var+'_'+str(area_code)],0.75))

                else:
                   print ('Rm the 12 hours persistence..')
            #fields_defn_nopers = ['climatology','analysis','12h forecast','60h forecast','108h forecast','204h forecast']
            fields_defn_nopers = ['climatology','analysis','fcst 1d','fcst 3d','fcst 5d','fcst 9d']
            fields_defn_nopers = np.array(fields_defn_nopers)
            fields_defn_nopers_cl = np.hstack([fields_defn_nopers[1:], fields_defn_nopers[:1]])
   
            # PLOT 1
            plt.subplot(3,1,1)
            l_rmsd = globals()['mean_rmse_'+str(depth)+'_'+var+'_'+str(area_code)]
            l_rmsd_cl = np.hstack([l_rmsd[1:], l_rmsd[:1]])
            l_rmsd_nocl = l_rmsd_cl[:-1]

            q1_rmsd = globals()['q1_rmse_'+str(depth)+'_'+var+'_'+str(area_code)]
            q1_rmsd_cl = np.hstack([q1_rmsd[1:], q1_rmsd[:1]])
            q1_rmsd_nocl = q1_rmsd_cl[:-1]

            q3_rmsd = globals()['q3_rmse_'+str(depth)+'_'+var+'_'+str(area_code)]
            q3_rmsd_cl = np.hstack([q3_rmsd[1:], q3_rmsd[:1]])
            q3_rmsd_nocl = q3_rmsd_cl[:-1]

            globals()['point1_'+str(field_idx)] = plt.plot(fields_defn_nopers_cl[:-1],l_rmsd_nocl,'o-',color="red",label='Mean RMSD')
            globals()['point1cl_'+str(field_idx)] = plt.plot(fields_defn_nopers_cl[-1],l_rmsd_cl[-1],'o',color="red")

            #globals()['err1_'+str(field_idx)] = plt.errorbar(fields_defn_nopers_cl,l_rmsd_cl,yerr=np.squeeze(np.array([[q1_rmsd_cl],[q3_rmsd_cl]])),color="red",label='Mean RMSD')

            for val_num_idx,val_num in enumerate(l_rmsd_cl):
                str_val = str(round(val_num,3))
                plt.text(fields_defn_nopers_cl[val_num_idx],val_num+0.001,str_val,fontsize=15,color="red")
            ylabel("Mean RMSD ["+udm[var_idx]+']',fontsize=16)
      
            plt.grid('on')
            plt.title(str(start_yy)+'-'+str(end_yy)+' Mean RMSD of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=18)
      
            #PLOT 2
            plt.subplot(3,1,2)
            l_bias = globals()['mean_bias_'+str(depth)+'_'+var+'_'+str(area_code)]
            l_bias_cl = np.hstack([l_bias[1:], l_bias[:1]])
            l_bias_nocl = l_bias_cl[:-1] 

            q1_bias = globals()['q1_bias_'+str(depth)+'_'+var+'_'+str(area_code)]
            q1_bias_cl = np.hstack([q1_bias[1:], q1_bias[:1]])
            q1_bias_nocl = q1_bias_cl[:-1]

            q3_bias = globals()['q3_bias_'+str(depth)+'_'+var+'_'+str(area_code)]
            q3_bias_cl = np.hstack([q3_bias[1:], q3_bias[:1]])
            q3_bias_nocl = q3_bias_cl[:-1]

            globals()['point2_'+str(field_idx)] = plt.plot(fields_defn_nopers_cl[:-1],l_bias_nocl,'o-',color="blue",label='Mean Bias (MOD-OBS)')
            globals()['point2cl_'+str(field_idx)] = plt.plot(fields_defn_nopers_cl[-1],l_bias_cl[-1],'o',color="blue")

            #globals()['err2_'+str(field_idx)] = plt.errorbar(fields_defn_nopers_cl,l_bias_cl,yerr=np.squeeze(np.array([[q1_bias_cl],[q3_bias_cl]])),color="blue",label='Mean Bias (MOD-OBS)')

            for val_num_idx,val_num in enumerate(l_bias_cl):
                str_val = str(round(val_num,3))
                plt.text(fields_defn_nopers_cl[val_num_idx],val_num+0.002,str_val,fontsize=15,color="blue")
            ylabel("Mean BIAS ["+udm[var_idx]+']',fontsize=16)
      
            plt.axhline(linewidth=2, color='black')
            plt.grid('on')
            plt.title(str(start_yy)+'-'+str(end_yy)+' Mean Bias of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=18)
      
            #PLOT 3
            plt.subplot(3,1,3)
            plt.title(str(start_yy)+'-'+str(end_yy)+' Mean Correlation of '+var+' at '+str(depths_defn[depth_idx])+' m - '+area_names[area_code] ,fontsize=18)
            l_corr = globals()['mean_corr_'+str(depth)+'_'+var+'_'+str(area_code)]
            l_corr_cl = np.hstack([l_corr[1:], l_corr[:1]])
            l_corr_nocl = l_corr_cl[:-1]

            q1_corr = globals()['q1_corr_'+str(depth)+'_'+var+'_'+str(area_code)]
            q1_corr_cl = np.hstack([q1_corr[1:], q1_corr[:1]])
            q1_corr_nocl = q1_corr_cl[:-1]

            q3_corr = globals()['q3_corr_'+str(depth)+'_'+var+'_'+str(area_code)]
            q3_corr_cl = np.hstack([q3_corr[1:], q3_corr[:1]])
            q3_corr_nocl = q3_corr_cl[:-1]

            globals()['point3_'+str(field_idx)] = plt.plot(fields_defn_nopers_cl[:-1],l_corr_nocl,'o-',color="green",label='Mean Correlation')
            globals()['point3cl_'+str(field_idx)] = plt.plot(fields_defn_nopers_cl[-1],l_corr_cl[-1],'o',color="green")

            #globals()['err3_'+str(field_idx)] = plt.errorbar(fields_defn_nopers_cl,l_corr_cl,yerr=np.squeeze(np.array([[q1_corr_cl],[q3_corr_cl]])),color="green",label='Mean Correlation')

            plt.ylabel("Mean Corr",fontsize=16)
            plt.ylim(top=1.0)
            for val_num_idx,val_num in enumerate(l_corr_cl):
                str_val = str(round(val_num,3))
                plt.text(fields_defn_nopers_cl[val_num_idx],val_num+0.002,str_val,fontsize=15,color="green")
            
            #leg = plt.legend(loc='lower left', ncol=2,  shadow=True, fancybox=True, fontsize=14)
            #leg.get_frame().set_alpha(0.3)
            plt.grid('on')
            
            plt.tight_layout()
            plt.savefig(fig_name,format='png',dpi=1200)
            plt.clf()
