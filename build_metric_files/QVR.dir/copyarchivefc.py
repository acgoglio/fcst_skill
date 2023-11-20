#! /usr/bin/env python
import datetime
import sys
import time
import calendar
import commands
import os.path

t0=sys.argv[1]
dirout=sys.argv[2]
tstart=sys.argv[3]
tend=sys.argv[4]
dir=sys.argv[5]
syst=sys.argv[6]
ver=sys.argv[7]
# tstart=0 tend=1 simulazione
# tstart=10 tend=11 10 giorno di forecast
ts=int(tstart)
te=int(tend)
t3=time.strptime(t0,"%Y%m%d")
d1=time.strftime("%Y%m%d",t3)
tf=time.strptime(d1,"%Y%m%d")
sf=calendar.timegm(tf)
for count in range(ts,te):
    s2f=sf-count*24*60*60
    d2f=s2f+10*24*60*60
    t2f=time.gmtime(s2f)
    t3f=time.gmtime(d2f)
    outf=time.strftime("%Y%m%d",t2f)
    YYYY=str(outf)[0:4]
    oute=time.strftime("%Y%m%d",t3f)
    filef=dir+YYYY+"/"+outf+"_"+oute+"_d-INGV---"+syst+"-MEDATL-b"+outf+"_arch_fc-"+ver 
    strcomf="cp "+filef+" "+dirout+"/."
#    strcomf="cp "+filef+" "+dirout
    print strcomf
    fname=dirout+"/"+outf+"_"+oute+"_d-INGV---"+syst+"-MEDATL-b"+outf+"_arch_fc-"+ver
    print fname
    a=os.path.isfile(fname)
    print a
    if a:
        print "File is present"
    else:
        ll=commands.getstatusoutput(strcomf)
        print ll[0]
        while ll[0]!=0:
            ll=commands.getstatusoutput(strcomf)
