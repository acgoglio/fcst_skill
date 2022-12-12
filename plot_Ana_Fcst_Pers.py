# AC Goglio Sep 2022
# Script for Forecast skill score
# Load condaE virtual env!

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
import matplotlib.pylab as pl 
warnings.filterwarnings("ignore")

#####################################

# -- Workdir path -- 
workdir = '/work/oda/ag15419/tmp/Ana_Fcst_Pers/'

# -- Period --
start_yy = 2017
end_yy   = 2021

# -- Area code --
area_code = 0

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
input_vars = ['salinity','sla','sst','sstl3s','temperature'] 
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
      fields_defn = ['climatology','analysis','12 hours persistence','12 hours forecast','60 hours forecast','108 hours forecast','204 hours forecast']
      # Loop on fields
      for field_idx,field in enumerate(fields): 
          print ('I am going to extract ',fields_defn[field_idx])
          # Mean squared error
          globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var]=[]
          # Obs num
          globals()['obs_'+str(field)+'_'+str(depth)+'_'+var]=[]
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
                     var_mse  = np.empty(days_num)
                     var_obs  = np.empty(days_num)
                 
                  # compute the RMSD (time, forecasts, depths, metrics, areas)
                  try:
                     globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var].extend(np.sqrt(var_mse[:])) 
                  except:
                     globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var].extend(np.array(var_mse[:]))

                  # Read the num of obs in first loop iteration
                  globals()['obs_'+str(field)+'_'+str(depth)+'_'+var].extend(np.array(var_obs[:]))
      print ('..Done!')  

      # Compute the date array
      time_var=pd.date_range(datetime.date(start_yy, 1, 1),datetime.date(end_yy, 12, 31))
   
      #####################
      # TS PLOT
      fig = plt.figure(0,figsize=(11,5))
      fig_name = workdir+var+'_RMSD_'+str(depth)+'_'+str(start_yy)+'-'+str(end_yy)+'.png'
      print ('Plot: ',fig_name)

      # Obs on the right axes 
      ax1 = fig.add_subplot(111)
      globals()['line_obs_'+str(field_idx)] = ax1.plot(time_var,pd.DataFrame(globals()['obs_'+str(field)+'_'+str(depth)+'_'+var]).rolling(rolling_mean_days).mean(),color="gray", label='Obs num',alpha=0.4)
      ax1.yaxis.tick_right()
      ax1.yaxis.set_label_position("right")
      ylabel("N. OBS",fontsize=16,color="gray")
      ax1.yaxis.label.set_color('gray')
      ax1.spines['right'].set_color('gray')

      # RMSDs on the left axes
      ax = fig.add_subplot(111, sharex=ax1, frameon=False)

      # Loop on fields to be plotted
      colors = pl.cm.jet_r(np.linspace(0,len(fields)))
      for field_idx,field in reversed(list(enumerate(fields))):
          print ('IDX',field_idx,colors[field_idx])
          if field != -12 :
             globals()['line_'+str(field_idx)] = ax.plot(time_var,pd.DataFrame(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var]).rolling(rolling_mean_days).mean(),color=colors[field_idx],label=fields_defn[field_idx],linewidth=1.5)
          else:
             print ('Rm the 12 hours persistence..')
     
      ylabel("RMSD ["+udm[var_idx]+']',fontsize=16)
      leg = plt.legend(loc='upper right', ncol=2,  shadow=True, fancybox=True, fontsize=12)
      leg.get_frame().set_alpha(0.3)
      ax.grid('on')
      plt.title(var+' '+str(start_yy)+'-'+str(end_yy)+' '+str(rolling_mean_days)+' days average of RMSD @ '+str(depths_defn[depth_idx])+' m ' ,fontsize=16)
      ax.xaxis.set_major_locator(mdates.YearLocator())
      ax.xaxis.set_minor_locator(mdates.MonthLocator((1,4,7,10)))
      ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%Y"))
      ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
      ax.margins(x=0)
      plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
      plt.tight_layout()
      plt.savefig(fig_name,format='png',dpi=1200)
      plt.clf()

      #######################
      # MEAN PLOT
      fig = plt.figure(0,figsize=(11,5))
      fig_name = workdir+'mean_'+var+'_RMSD_'+str(depth)+'_'+str(start_yy)+'-'+str(end_yy)+'.png'
      print ('Plot: ',fig_name)

      # RMSDs on the left axes
      ax = fig.add_subplot(111)

      # Loop on fields to be plotted
      globals()['mean_rmse_'+str(depth)+'_'+var]=[]
      for field_idx,field in enumerate(fields):
          print (fields_defn[field_idx],'Val: ',np.nanmean(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var]))
          if field != -12 :
             globals()['mean_rmse_'+str(depth)+'_'+var].append(np.nanmean(globals()['rmse_'+str(field)+'_'+str(depth)+'_'+var]))
          else:
             print ('Rm the 12 hours persistence..')
      fields_defn_nopers = ['climatology','analysis','12 hours forecast','60 hours forecast','108 hours forecast','204 hours forecast'] 
      globals()['point_'+str(field_idx)] = ax.plot(fields_defn_nopers,globals()['mean_rmse_'+str(depth)+'_'+var],'x',color="red")
      
      # Add the numbers in the plot
      for val_num_idx,val_num in enumerate(globals()['mean_rmse_'+str(depth)+'_'+var]):
          str_val = str(round(val_num,3))
          plt.text(fields_defn_nopers[val_num_idx],val_num+0.001,str_val,fontsize=10,color="red")

      ylabel("mean RMSD ["+udm[var_idx]+']',fontsize=16)
      ax.grid('on')
      plt.title(var+' '+str(start_yy)+'-'+str(end_yy)+' mean RMSD @ '+str(depths_defn[depth_idx])+' m ' ,fontsize=16)

      plt.tight_layout()
      plt.savefig(fig_name,format='png',dpi=1200)
      plt.clf()

