# THis program is suited to produce EAN statistcs from MED experiments, in the form of Human readable csv files
# the program accepts as inputs the intermediate csv files of the type
# YYYYMMDD.<exp>.<instr>.csv
# where first tag YYYYMMDD gives the time frame (year, month and day) of data included within the file 
# the <exp> tag is related to the experiment whose wariable are used
# the <instr> tag refers to the observations source, as INSITU (INSITU=ARGO,XBT,GLIDER), SST, SLA
# to execute the script, some parameters are needed to give the structure of statistics, as the following example
# EAN_calc.py <inputfile> <outputfile> <nregs> <nlevs> <varid> <initime> <endtime>
# the <inputfile> parameter is a sample file, e.g, 20120120.exp1.INSITU.csv The time tag of the <inputfile> is not used
# the <outputfile> parameter is a string (no extension needed) that identifies the outputs , which filenames will all begin as <outputfile>_*
# the <nregs> parameter gives the number of regions in which the domain has been split. It can be any number, but at present insert 13 or 17 for this parameter
# the <nlevs> parameter gives the number of selected levels. please insert 6 or 9 for 3-D variables, 1 for 2-D variables
# the <initime> and <endtime> parameters must be in YYYYMMDD format, with <initime> date preceding the <endtime> one
# no check except the right number of parameters given is currently performed, so be careful when inserting the parameters

# the output are also csv files, dedicated to the selected experiment, selected source, and selected variable, which appears as tags in the output namefile
# inside the csv files, data lines are organized in the following order
# <region number> <RMSE> <BIAS> <NOBS>
# <region number> is a number that identifies the region, with 00 being the whole MED
# <RMSE> is the sequence of rmse in the region at each level defined (float number) 
# <BIAS> is the sequence of bias in the region at each level defined (float number) (obs-mod)
# <NOBS> is the sequence of observations in the region at each level defined (integer number)

# *STAT* files contains variances, means and covariances evaluated from the model and observations timeseries, as follow
# <region number> <VARMOD> <MEANMOD> <VAROBS> <MEANOBS> <COV>
# <region number> is a number that identifies the region, with 00 being the whole MED
# <VARMOD> is the sequence of model variance in the region at each level defined (float number)
# <MEANMOD> is the sequence of model mean in the region at each level defined (float number)
# <OBSMOD> is the sequence of observations variance in the region at each level defined (float number)
# <MEANOBS> is the sequence of observations mean in the region at each level defined (float number)
# <COV> is the sequence of <model,obs> covariance in the region at each level defined (float number)

#Satellites statistic output is given on multilple files: one including the general satallite statistics, and other dedicated each to a specific satellite (CRIOSAT,JASON1,JASON2,ALTIKA)
#Insitu statistic output is given on multilple files: one including the general insitu statistics, and other dedicated each to a specific instrumentation (ARGO,XBT,GLIDER)

import numpy as np
import sys
import getopt 
import os.path
from datetime import timedelta, date
from scipy import stats


savefile = 'default_tab'

print 'EAN_calc.py <inputfile> <outputfile> <nregs> <nlevs> <varid> <initime> <endtime> <sourcepath> <biasedge>'
print 'Argument entered:', str(sys.argv)
if (len(sys.argv)-1 != 9):
    print 'number of arguments:', len(sys.argv)-1, 'arguments, needed 8 arguments'
    print 'please enter the right <parameters> in the right order'
    print 'EAN_calc.py <inputfile> <outputfile> <nregs> <nlevs> <varid> <initime> <endtime> <sourcepath>'
    print 'example: phyton EAN_calc.py 20120101.exp1.INSITU.csv pippo 13 9 2 20120101 20120229 /home/myuser/mydaya/'
    print 'to execute source file(s) similar to  20120101.exp1.INSITU.csv, putting the output to pippo*,'
    print 'domain splitted in 13 regions, 9 levels, process SALT variable, from 20120101 to 20120229, stored in /home/myuser/mydaya/'
    print 'variable ids : 1=TEMP 2=SALT 3=SST 4=SLA '
    sys.exit()

argv=sys.argv
inputfile  = argv[1]
savefile   = argv[2]
nregs      = argv[3]
levs       = argv[4]
myvar      = argv[5]
initime    = argv[6]
endtime    = argv[7]
pat        = argv[8]
edge       = argv[9]

entries=inputfile.split(".")
exper=entries[1]
instr=entries[2]

if int(myvar)==1:
    strvar='TEMP'
elif int(myvar)==2:
    strvar='SALT'
elif int(myvar)==3:
    strvar='SST'
elif int(myvar)==4:
    strvar='SLA'

print 'Input experiment is "',exper
print 'Input instrument is "',instr
print 'Output file is "', savefile
print 'domain has ',nregs,' regions, and ',levs,'levels'
print 'variable chosen is 1=T 2=S 3=SST 4=SLA: ',strvar
print 'time range: from ',initime,' to ',endtime    
print 'source path: ', pat
print 'removing abs(bias) larger than: ', edge

edge=int(edge)
dep=np.array([0.0,10.0,30.0,60.0,100.0,150.0,300.0,600.0,1000.0,2000.0])

lev=int(levs)
regs=int(nregs)
# 1=temperature, 2=salinity, 3=sst, 4=sla
selvar=int(myvar)

if lev == 1:
    dep1=dep[[0]]
    dep2=dep[[1]]
if lev == 6:
    dep1=dep[[0,1,2,5,6,7]]
    dep2=dep[[1,2,5,6,7,8]]
if lev ==9:
    dep1=dep[0:9]
    dep2=dep[1:10]

# storing statistics for aggregated source (INSITU, SLA)
# or for SST data (single source)
ndept=np.shape(dep1)[0]
dsq=np.zeros((regs,ndept))
bias=np.zeros((regs,ndept))
dsq_c=np.zeros((regs,ndept))
aggr_mod=np.zeros((regs,ndept))
aggr_obs=np.zeros((regs,ndept))
reslt=np.zeros((regs,ndept))
mean_mod=np.zeros((regs,ndept))
mean_obs=np.zeros((regs,ndept))

if (instr == "INSITU" ):
    dsq_argo=np.zeros((regs,ndept))
    bias_argo=np.zeros((regs,ndept))
    dsq_c_argo=np.zeros((regs,ndept))
    dsq_xbt=np.zeros((regs,ndept))
    bias_xbt=np.zeros((regs,ndept))
    dsq_c_xbt=np.zeros((regs,ndept))
    dsq_glider=np.zeros((regs,ndept))
    bias_glider=np.zeros((regs,ndept))
    dsq_c_glider=np.zeros((regs,ndept))

# Introducing variables to store statistics for individual satellites
# 2=Criosat 4=Jason1 5=Jason2 6=Altika
#if (int(myvar) == 4):
if (instr == "SLA"):
    dsq_criosat=np.zeros((regs,ndept))
    bias_criosat=np.zeros((regs,ndept))
    dsq_c_criosat=np.zeros((regs,ndept))
    dsq_jas1=np.zeros((regs,ndept))
    bias_jas1=np.zeros((regs,ndept))
    dsq_c_jas1=np.zeros((regs,ndept))
    dsq_jas2=np.zeros((regs,ndept))
    bias_jas2=np.zeros((regs,ndept))
    dsq_c_jas2=np.zeros((regs,ndept))
    dsq_altika=np.zeros((regs,ndept))
    bias_altika=np.zeros((regs,ndept))
    dsq_c_altika=np.zeros((regs,ndept))

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+1):
        yield start_date + timedelta(n)

#print int(initime[0:4]),int(initime[4:6]) , int(initime[6:8])
start_date = date(int(initime[0:4]),int(initime[4:6]) , int(initime[6:8]))
end_date = date(int(endtime[0:4]),int(endtime[4:6]) , int(endtime[6:8]))

print "evaluating squared difference and plain differences in all locations"
for single_date in daterange(start_date, end_date):
    #print single_date.strftime("%Y-%m-%d")
    timetag=single_date.strftime("%Y%m%d")

    # reading the selected cvs file
    infile=timetag+'.'+entries[1]+'.'+entries[2]+'.csv'
    if os.path.isfile(pat+infile) and os.stat(pat+infile).st_size > 62:
        print "reading: ", infile, " size: ", os.stat(pat+infile).st_size
        csv = np.genfromtxt (pat+infile, delimiter=",")
        #fieldnames=['region','var_id','lon_obs','lat_obs','depth_obs','mod','obs']
        #depths6=[0-10[ , [10-30[ , [30-150[ , [150-300[ , [300-600[ , [600-1000]

        nlines=np.shape(csv)[0]
        for irow in range(nlines):
            for idep in range(ndept):
                if (csv[irow,1] == selvar):
                    if (csv[irow,1] in [ 1, 2, 3] and csv[irow,0] > 0 and csv[irow,4] >= dep1[idep] and csv[irow,4] < dep2[idep] ):
                    #if np.isfinite(csv[irow,5]-csv[irow,6]):
                    # check over observations >0 is necessary because we now compare interpolated 1/24 -> 1/16 model fields
                    # that have been processed with sea over land, so the preprocessing check finds legit values on land and
                    # stores them in the input files here used. At the same time, the observed values on land are set to zero
                    # so we avoid to collect these values checking the obs [irow,5]=modelllo, [irow,6]=dato osservato
                        if (instr == "SST" and csv[irow,6]>0):
                            bias[int(csv[irow,0])-1,idep]=bias[int(csv[irow,0])-1,idep]+(csv[irow,6]-csv[irow,5]) 
                            dsq[int(csv[irow,0])-1,idep]=dsq[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-csv[irow,6]) 
                            dsq_c[int(csv[irow,0])-1,idep]=dsq_c[int(csv[irow,0])-1,idep] + 1

                            aggr_mod[int(csv[irow,0])-1,idep]=aggr_mod[int(csv[irow,0])-1,idep]+csv[irow,5]
                            aggr_obs[int(csv[irow,0])-1,idep]=aggr_obs[int(csv[irow,0])-1,idep]+csv[irow,6]
                        if (instr=="INSITU"):
                         #check for spurious data or high bias
                         if (csv[irow,5]<40 and csv[irow,5]>0) and (abs(csv[irow,6]-csv[irow,5]) <= edge):
                            bias[int(csv[irow,0])-1,idep]=bias[int(csv[irow,0])-1,idep]+(csv[irow,6]-csv[irow,5]) 
                            dsq[int(csv[irow,0])-1,idep]=dsq[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-csv[irow,6]) 
                            dsq_c[int(csv[irow,0])-1,idep]=dsq_c[int(csv[irow,0])-1,idep] + 1

                            aggr_mod[int(csv[irow,0])-1,idep]=aggr_mod[int(csv[irow,0])-1,idep]+csv[irow,5]
                            aggr_obs[int(csv[irow,0])-1,idep]=aggr_obs[int(csv[irow,0])-1,idep]+csv[irow,6]
#                            if (abs(csv[irow,6]-csv[irow,5]) > 5):
#                                print "high bias ",abs(csv[irow,6]-csv[irow,5]),csv[irow,2:7],infile
                            if (csv[irow,7] == 1):
                                bias_argo[int(csv[irow,0])-1,idep]=bias_argo[int(csv[irow,0])-1,idep]+(csv[irow,6]-csv[irow,5])
                                dsq_argo[int(csv[irow,0])-1,idep]=dsq_argo[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-csv[irow,6])
                                dsq_c_argo[int(csv[irow,0])-1,idep]=dsq_c_argo[int(csv[irow,0])-1,idep] + 1
                            if (csv[irow,7] == 2):
                                bias_xbt[int(csv[irow,0])-1,idep]=bias_xbt[int(csv[irow,0])-1,idep]+(csv[irow,6]-csv[irow,5])
                                dsq_xbt[int(csv[irow,0])-1,idep]=dsq_xbt[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-csv[irow,6])
                                dsq_c_xbt[int(csv[irow,0])-1,idep]=dsq_c_xbt[int(csv[irow,0])-1,idep] + 1
                            if (csv[irow,7] == 3):
                                bias_glider[int(csv[irow,0])-1,idep]=bias_glider[int(csv[irow,0])-1,idep]+(csv[irow,6]-csv[irow,5])
                                dsq_glider[int(csv[irow,0])-1,idep]=dsq_glider[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-csv[irow,6])
                                dsq_c_glider[int(csv[irow,0])-1,idep]=dsq_c_glider[int(csv[irow,0])-1,idep] + 1
                         else:
                            print "high bias or found garbage:", csv[irow,5:7],timetag,irow
                         if (csv[irow,6]>40 or csv[irow,6]<0):
                            print" something is WRONG in data:", csv[irow,6],irow,timetag 
                    if (instr == "SLA"):
                        if (csv[irow,4] >= edge):
                            bias[int(csv[irow,0])-1,idep]=bias[int(csv[irow,0])-1,idep]+(csv[irow,6]-csv[irow,5]) 
                            dsq[int(csv[irow,0])-1,idep]=dsq[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-csv[irow,6]) 
                            dsq_c[int(csv[irow,0])-1,idep]=dsq_c[int(csv[irow,0])-1,idep] + 1

                            aggr_mod[int(csv[irow,0])-1,idep]=aggr_mod[int(csv[irow,0])-1,idep]+csv[irow,5]
                            aggr_obs[int(csv[irow,0])-1,idep]=aggr_obs[int(csv[irow,0])-1,idep]+csv[irow,6]
                            if (csv[irow,7] == 2):
                                bias_criosat[int(csv[irow,0])-1,idep]=bias_criosat[int(csv[irow,0])-1,idep]+(csv[irow,6]-csv[irow,5]) 
                                dsq_criosat[int(csv[irow,0])-1,idep]=dsq_criosat[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-csv[irow,6]) 
                                dsq_c_criosat[int(csv[irow,0])-1,idep]=dsq_c_criosat[int(csv[irow,0])-1,idep] + 1
                            if (csv[irow,7] == 4):
                                bias_jas1[int(csv[irow,0])-1,idep]=bias_jas1[inr(csv[irow,0])-1,idep]+(csv[irow,6]-csv[irow,5]) 
                                dsq_jas1[int(csv[irow,0])-1,idep]=dsq_jas1[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-csv[irow,6]) 
                                dsq_c_jas1[int(csv[irow,0])-1,idep]=dsq_c_jas1[int(csv[irow,0])-1,idep] + 1
                            if (csv[irow,7] == 5):
                                bias_jas2[int(csv[irow,0])-1,idep]=bias_jas2[int(csv[irow,0])-1,idep]+(csv[irow,6]-csv[irow,5]) 
                                dsq_jas2[int(csv[irow,0])-1,idep]=dsq_jas2[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-csv[irow,6]) 
                                dsq_c_jas2[int(csv[irow,0])-1,idep]=dsq_c_jas2[int(csv[irow,0])-1,idep] + 1
                            if (csv[irow,7] == 6):
                                bias_altika[int(csv[irow,0])-1,idep]=bias_altika[int(csv[irow,0])-1,idep]+(csv[irow,6]-csv[irow,5]) 
                                dsq_altika[int(csv[irow,0])-1,idep]=dsq_altika[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-csv[irow,6]) 
                                dsq_c_altika[int(csv[irow,0])-1,idep]=dsq_c_altika[int(csv[irow,0])-1,idep] + 1
                        else:
                            print "sla over seafloor less than:" , edge, "m :",  csv[irow,4]
                        
                        
    else:
        print "file empty or not found: ", infile

#dsq_c[dsq_c==0]=np.nan
reslt1=np.sqrt(dsq/dsq_c)
reslt2=bias/dsq_c
mean_mod=aggr_mod/dsq_c
mean_obs=aggr_obs/dsq_c

print "reslt1: ", reslt1
print "reslt2: ", reslt2
print "dsq_c : ", dsq_c
print "mean_mod: ",mean_mod
print "mean_obs: ",mean_obs

var_mod=np.zeros((regs,ndept))
var_obs=np.zeros((regs,ndept))
cov_m_o=np.zeros((regs,ndept))

print "reading again the selected cvs file to evaluate second order statistics"
for single_date in daterange(start_date, end_date):
    timetag=single_date.strftime("%Y%m%d")

    infile=timetag+'.'+entries[1]+'.'+entries[2]+'.csv'
    if os.path.isfile(pat+infile) and os.stat(pat+infile).st_size > 62:
        print "reading: ", infile, " size: ", os.stat(pat+infile).st_size
        csv = np.genfromtxt (pat+infile, delimiter=",")
        #fieldnames=['region','var_id','lon_obs','lat_obs','depth_obs','mod','obs']
        nlines=np.shape(csv)[0]
        #evaluating variance of model and obs, and covariance between them
        for irow in range(nlines):
            for idep in range(ndept):
                if (csv[irow,1] == selvar ):
                    if (csv[irow,1] in [ 1, 2, 3] and csv[irow,0] > 0 and csv[irow,4] >= dep1[idep] and csv[irow,4] < dep2[idep]):
                    #if np.isfinite(csv[irow,5]-csv[irow,6]):
                        if (instr == "SST" and csv[irow,6]>0):
                            var_mod[int(csv[irow,0])-1,idep]=var_mod[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-mean_mod[int(csv[irow,0])-1,idep])
                            var_obs[int(csv[irow,0])-1,idep]=var_obs[int(csv[irow,0])-1,idep]+np.square(csv[irow,6]-mean_obs[int(csv[irow,0])-1,idep])
                            cov_m_o[int(csv[irow,0])-1,idep]=cov_m_o[int(csv[irow,0])-1,idep]+((csv[irow,5]-mean_mod[int(csv[irow,0])-1,idep]) * \
                             (csv[irow,6]-mean_obs[int(csv[irow,0])-1,idep]))
                        if (instr=="INSITU"):
                         #check for spurious data or high bias
                            if (csv[irow,5]<40 and csv[irow,5]>0) and (abs(csv[irow,6]-csv[irow,5]) <= edge):
                                #print "first",timetag,irow,idep,csv[irow,5],mean_mod[int(csv[irow,0])-1,idep],csv[irow,6],mean_obs[int(csv[irow,0])-1,idep],var_mod[int(csv[irow,0])-1,idep],var_obs[int(csv[irow,0])-1,idep],cov_m_o[int(csv[irow,0])-1,idep]
                                var_mod[int(csv[irow,0])-1,idep]=var_mod[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-mean_mod[int(csv[irow,0])-1,idep])
                                var_obs[int(csv[irow,0])-1,idep]=var_obs[int(csv[irow,0])-1,idep]+np.square(csv[irow,6]-mean_obs[int(csv[irow,0])-1,idep])
                                cov_m_o[int(csv[irow,0])-1,idep]=cov_m_o[int(csv[irow,0])-1,idep]+((csv[irow,5]-mean_mod[int(csv[irow,0])-1,idep]) * \
                                 (csv[irow,6]-mean_obs[int(csv[irow,0])-1,idep]))
                                #print "after",timetag,irow,idep,csv[irow,5],mean_mod[int(csv[irow,0])-1,idep],csv[irow,6],mean_obs[int(csv[irow,0])-1,idep],var_mod[int(csv[irow,0])-1,idep],var_obs[int(csv[irow,0])-1,idep],cov_m_o[int(csv[irow,0])-1,idep]
                            else:
                                print "high bias or found garbage:", csv[irow,5:7],timetag,irow
                    if (instr == "SLA"):
                        var_mod[int(csv[irow,0])-1,idep]=var_mod[int(csv[irow,0])-1,idep]+np.square(csv[irow,5]-mean_mod[int(csv[irow,0])-1,idep])
                        var_obs[int(csv[irow,0])-1,idep]=var_obs[int(csv[irow,0])-1,idep]+np.square(csv[irow,6]-mean_obs[int(csv[irow,0])-1,idep])
                        cov_m_o[int(csv[irow,0])-1,idep]=cov_m_o[int(csv[irow,0])-1,idep]+((csv[irow,5]-mean_mod[int(csv[irow,0])-1,idep]) * \
                        (csv[irow,6]-mean_obs[int(csv[irow,0])-1,idep]))
    else:
        print "file empty or not found: ", infile

# evalutaing the second order statistics
var_mod_rslt=var_mod/dsq_c
var_obs_rslt=var_obs/dsq_c
cov_m_o_rslt=cov_m_o/dsq_c

#if (int(myvar)==4):
if (instr == "INSITU"):
    reslt1_argo=np.sqrt(dsq_argo/dsq_c_argo)
    reslt2_argo=bias_argo/dsq_c_argo
    reslt1_argo_aggr=np.nanmean(reslt1_argo[0:regs-1,:],axis=0)
    reslt2_argo_aggr=np.nanmean(reslt2_argo[0:regs-1,:],axis=0)
    dsq_c_argo_levs=np.sum(dsq_c_argo[0:regs-1,:],axis=0)

    reslt1_xbt=np.sqrt(dsq_xbt/dsq_c_xbt)
    reslt2_xbt=bias_xbt/dsq_c_xbt
    reslt1_xbt_aggr=np.nanmean(reslt1_xbt[0:regs-1,:],axis=0)
    reslt2_xbt_aggr=np.nanmean(reslt2_xbt[0:regs-1,:],axis=0)
    dsq_c_xbt_levs=np.sum(dsq_c_xbt[0:regs-1,:],axis=0)

    reslt1_glider=np.sqrt(dsq_glider/dsq_c_glider)
    reslt2_glider=bias_glider/dsq_c_glider
    reslt1_glider_aggr=np.nanmean(reslt1_glider[0:regs-1,:],axis=0)
    reslt2_glider_aggr=np.nanmean(reslt2_glider[0:regs-1,:],axis=0)
    dsq_c_glider_levs=np.sum(dsq_c_glider[0:regs-1,:],axis=0)

if (instr == "SLA"):
    reslt1_criosat=np.sqrt(dsq_criosat/dsq_c_criosat)
    reslt2_criosat=bias_criosat/dsq_c_criosat
    reslt1_criosat_aggr=np.nanmean(reslt1_criosat[0:regs-1,:],axis=0)
    reslt2_criosat_aggr=np.nanmean(reslt2_criosat[0:regs-1,:],axis=0)
    dsq_c_criosat_levs=np.sum(dsq_c_criosat[0:regs-1,:],axis=0)

    reslt1_jas1=np.sqrt(dsq_jas1/dsq_c_jas1)
    reslt2_jas1=bias_jas1/dsq_c_jas1
    reslt1_jas1_aggr=np.nanmean(reslt1_jas1[0:regs-1,:],axis=0)
    reslt2_jas1_aggr=np.nanmean(reslt2_jas1[0:regs-1,:],axis=0)
    dsq_c_jas1_levs=np.sum(dsq_c_jas1[0:regs-1,:],axis=0)

    reslt1_jas2=np.sqrt(dsq_jas2/dsq_c_jas2)
    reslt2_jas2=bias_jas2/dsq_c_jas2
    reslt1_jas2_aggr=np.nanmean(reslt1_jas2[0:regs-1,:],axis=0)
    reslt2_jas2_aggr=np.nanmean(reslt2_jas2[0:regs-1,:],axis=0)
    dsq_c_jas2_levs=np.sum(dsq_c_jas2[0:regs-1,:],axis=0)

    reslt1_altika=np.sqrt(dsq_altika/dsq_c_altika)
    reslt2_altika=bias_altika/dsq_c_altika
    reslt1_altika_aggr=np.nanmean(reslt1_altika[0:regs-1,:],axis=0)
    reslt2_altika_aggr=np.nanmean(reslt2_altika[0:regs-1,:],axis=0)
    dsq_c_altika_levs=np.sum(dsq_c_altika[0:regs-1,:],axis=0)

reslt1_aggr_lvl=np.nanmean(reslt1[0:regs-1,:],axis=0)
reslt2_aggr_lvl=np.nanmean(reslt2[0:regs-1,:],axis=0)
dsq_c_regs=np.sum(dsq_c,axis=1)
dsq_c_levs=np.sum(dsq_c[0:regs-1,:],axis=0)

mean_mod_lvl=np.nanmean(mean_mod[0:regs-1,:],axis=0)
mean_obs_lvl=np.nanmean(mean_obs[0:regs-1,:],axis=0)
var_mod_lvl=np.nanmean(var_mod_rslt[0:regs-1,:],axis=0)
var_obs_lvl=np.nanmean(var_obs_rslt[0:regs-1,:],axis=0)
cov_m_o_lvl=np.nanmean(cov_m_o_rslt[0:regs-1,:],axis=0)

# fare la media delle medie locali non e' come fare una media generale: metodo 2
reslt1_aggr_lvlB=np.sqrt(np.nansum(dsq[0:regs-1,:],axis=0)/np.nansum(dsq_c[0:regs-1,:],axis=0))
print "reslt1_aggr_lvl",reslt1_aggr_lvl
print "reslt1_aggr_lvlB",reslt1_aggr_lvlB
reslt2_aggr_lvlB=np.nansum(bias[0:regs-1,:],axis=0)/np.nansum(dsq_c[0:regs-1,:],axis=0)
print "reslt2_aggr_lvl",reslt2_aggr_lvl
print "reslt2_aggr_lvlB",reslt2_aggr_lvlB

var_mod_aggr_lvl=np.nansum(var_mod[0:regs-1,:],axis=0)/np.nansum(dsq_c[0:regs-1,:],axis=0)
var_obs_aggr_lvl=np.nansum(var_obs[0:regs-1,:],axis=0)/np.nansum(dsq_c[0:regs-1,:],axis=0)
cov_m_o_aggr_lvl=np.nansum(cov_m_o[0:regs-1,:],axis=0)/np.nansum(dsq_c[0:regs-1,:],axis=0)
#reslt1=np.sqrt(dsq/dsq_c)
#reslt2=bias/dsq_c
#mean_mod=aggr_mod/dsq_c
#mean_obs=aggr_obs/dsq_c
#var_mod_rslt=var_mod/dsq_c
#var_obs_rslt=var_obs/dsq_c
#cov_m_o_rslt=cov_m_o/dsq_c

#create formatting
form_data='%8.4f,'*int(levs)*2+'%6d,'*int(levs)
form_data=form_data[0:len(form_data)-1]
form_data2='%8.4f,'*int(levs)*5
form_data2=form_data2[0:len(form_data2)-1]

f1 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_EAN.csv', "a")
for ii in range(int(nregs)+1):
    f1.write(str("%02d"%ii)+", ")
    if (ii==0):
        linea=np.concatenate((reslt1_aggr_lvl,reslt2_aggr_lvl,dsq_c_levs),axis=0)
    else:
        linea=np.concatenate((reslt1[ii-1,:],reslt2[ii-1,:],dsq_c[ii-1,:]),axis=0)
    np.savetxt(f1,linea.reshape(1,int(levs)*3),fmt=form_data)

f11 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_EAN2.csv', "a")
for ii in range(int(nregs)+1):
    f11.write(str("%02d"%ii)+", ")
    if (ii==0):
        linea=np.concatenate((reslt1_aggr_lvlB,reslt2_aggr_lvlB,dsq_c_levs),axis=0)
    else:
        linea=np.concatenate((reslt1[ii-1,:],reslt2[ii-1,:],dsq_c[ii-1,:]),axis=0)
    np.savetxt(f11,linea.reshape(1,int(levs)*3),fmt=form_data)

#print "examining1 ", np.shape(reslt1_aggr_lvl), np.shape(reslt2_aggr_lvl),np.shape(dsq_c_levs)
#print "examining: ", np.shape(var_mod_lvl), np.shape(var_obs_lvl),np.shape(cov_m_o_lvl)
f9 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_EAN_STATS.csv', "a")
for ii in range(int(nregs)+1):
    f9.write(str("%02d"%ii)+", ")
    if (ii==0):
        linea=np.concatenate((var_mod_lvl,mean_mod_lvl,var_obs_lvl,mean_obs_lvl,cov_m_o_lvl),axis=0)
    else:
        linea=np.concatenate((var_mod_rslt[ii-1,:],mean_mod[ii-1,:],var_obs_rslt[ii-1,:],mean_obs[ii-1,:],cov_m_o_rslt[ii-1,:]),axis=0)
    np.savetxt(f9,linea.reshape(1,int(levs)*5),fmt=form_data2)

f10 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_EAN_STATS2.csv', "a")
for ii in range(int(nregs)+1):
    f10.write(str("%02d"%ii)+", ")
    if (ii==0):
        linea=np.concatenate((var_mod_aggr_lvl,mean_mod_lvl,var_obs_aggr_lvl,mean_obs_lvl,cov_m_o_aggr_lvl),axis=0)
    else:
        linea=np.concatenate((var_mod_rslt[ii-1,:],mean_mod[ii-1,:],var_obs_rslt[ii-1,:],mean_obs[ii-1,:],cov_m_o_rslt[ii-1,:]),axis=0)
    np.savetxt(f10,linea.reshape(1,int(levs)*5),fmt=form_data2)


if instr == "INSITU":
    f2 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_ARGO_EAN.csv', "a")
    for ii in range(int(nregs)+1):
        f2.write(str("%02d"%ii)+", ")
        if (ii==0):
            linea=np.concatenate((reslt1_argo_aggr,reslt2_argo_aggr,dsq_c_argo_levs),axis=0)
        else:
            linea=np.concatenate((reslt1_argo[ii-1,:],reslt2_argo[ii-1,:],dsq_c_argo[ii-1,:]),axis=0)
        np.savetxt(f2,linea.reshape(1,int(levs)*3),fmt=form_data)

    f3 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_XBT_EAN.csv', "a")
    for ii in range(int(nregs)+1):
        f3.write(str("%02d"%ii)+", ")
        if (ii==0):
            linea=np.concatenate((reslt1_xbt_aggr,reslt2_xbt_aggr,dsq_c_xbt_levs),axis=0)
        else:
            linea=np.concatenate((reslt1_xbt[ii-1,:],reslt2_xbt[ii-1,:],dsq_c_xbt[ii-1,:]),axis=0)
        np.savetxt(f3,linea.reshape(1,int(levs)*3),fmt=form_data)

    f4 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_GLIDER_EAN.csv', "a")
    for ii in range(int(nregs)+1):
        f4.write(str("%02d"%ii)+", ")
        if (ii==0):
            linea=np.concatenate((reslt1_glider_aggr,reslt2_glider_aggr,dsq_c_glider_levs),axis=0)
        else:
            linea=np.concatenate((reslt1_glider[ii-1,:],reslt2_glider[ii-1,:],dsq_c_glider[ii-1,:]),axis=0)
        np.savetxt(f4,linea.reshape(1,int(levs)*3),fmt=form_data)

#if int(myvar)==4:
if instr == "SLA":
    f5 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_CRIOSAT_EAN.csv', "a")
    for ii in range(int(nregs)+1):
        f5.write(str("%02d"%ii)+", ")
        if (ii==0):
            linea=np.concatenate((reslt1_criosat_aggr,reslt2_criosat_aggr,dsq_c_criosat_levs),axis=0)
        else:
            linea=np.concatenate((reslt1_criosat[ii-1,:],reslt2_criosat[ii-1,:],dsq_c_criosat[ii-1,:]),axis=0)
        np.savetxt(f5,linea.reshape(1,int(levs)*3),fmt=form_data)

    f6 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_JASON1.csv', "a")
    for ii in range(int(nregs)+1):
        f6.write(str("%02d"%ii)+", ")
        if (ii==0):
            linea=np.concatenate((reslt1_jas1_aggr,reslt2_jas1_aggr,dsq_c_jas1_levs),axis=0)
        else:
            linea=np.concatenate((reslt1_jas1[ii-1,:],reslt2_jas1[ii-1,:],dsq_c_jas1[ii-1,:]),axis=0)
        np.savetxt(f6,linea.reshape(1,int(levs)*3),fmt=form_data)

    f7 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_JASON2_EAN.csv', "a")
    for ii in range(int(nregs)+1):
        f7.write(str("%02d"%ii)+", ")
        if (ii==0):
            linea=np.concatenate((reslt1_jas2_aggr,reslt2_jas2_aggr,dsq_c_jas2_levs),axis=0)
        else:
            linea=np.concatenate((reslt1_jas2[ii-1,:],reslt2_jas2[ii-1,:],dsq_c_jas2[ii-1,:]),axis=0)
        np.savetxt(f7,linea.reshape(1,int(levs)*3),fmt=form_data)

    f8 = open(savefile+'_'+exper+'_'+instr+'_'+strvar+'_'+initime+'_'+endtime+'_ALTIKA_EAN.csv', "a")
    for ii in range(int(nregs)+1):
        f8.write(str("%02d"%ii)+", ")
        if (ii==0):
            linea=np.concatenate((reslt1_altika_aggr,reslt2_altika_aggr,dsq_c_altika_levs),axis=0)
        else:
            linea=np.concatenate((reslt1_altika[ii-1,:],reslt2_altika[ii-1,:],dsq_c_altika[ii-1,:]),axis=0)
        np.savetxt(f8,linea.reshape(1,int(levs)*3),fmt=form_data)

    
