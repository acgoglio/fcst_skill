#! /usr/bin/env python

from netCDF4 import Dataset 
import sys
import seawater as sw
from copy import copy, deepcopy

indir=sys.argv[1]
outdir=sys.argv[2]
filein=sys.argv[3]
date=sys.argv[4]

def create_line(p,i,x,y,d,t,v,e):
    LON='{:{width}.{prec}f}'.format(x, width=10, prec=5)
    LAT='{:{width}.{prec}f}'.format(y, width=10, prec=5)
    DEP='{:{width}.{prec}f}'.format(d, width=10, prec=5)
    TIM='{:{width}.{prec}f}'.format(t, width=10, prec=5)
    TEM='{:{width}.{prec}f}'.format(v, width=10, prec=5)
    ERR='{:{width}.{prec}f}'.format(e, width=10, prec=5)
    lin=p+i+LON+LAT+DEP+TIM+TEM+ERR
    return lin

obs=filein[13:15]
if obs=='PF':
    inst=int(filein[16:23])
    outfile='.ARGO.dat'
elif obs=='GL':
    outfile='.GLIDER.dat'
else:
    outfile='.XBT.dat'

fh = Dataset(indir+'/'+filein, mode='r')
lon = fh.variables['LONGITUDE'][:]
lat = fh.variables['LATITUDE'][:]
dep = fh.variables['DEPH'][:]
depqc = fh.variables['DEPH_QC'][:]
tem = fh.variables['TEMP'][:]
temqc = fh.variables['TEMP_QC'][:]
if obs=='PF' or obs=='GL':
    sal = fh.variables['PSAL'][:]
    salqc = fh.variables['PSAL_QC'][:]
fh.close()

nprof=dep.shape[0]
indT=1
indS=2
tim=0
err=0

ptem=deepcopy(tem)

f = open(outdir+'/'+date+outfile, 'a')

if obs=='PF':
    for i in range(dep.shape[0]):
        for j in range(dep.shape[1]):
            if temqc[i,j]==1:
                ptem[i,j]=sw.ptmp(sal[i,j],tem[i,j],sw.pres(dep[i,j],lat[i]))
                BUOY=' '+'{:7d}'.format(inst)
                P='{:5d}'.format(i+1)
                I='{:4d}'.format(indT)
                lin=create_line(P,I,lon[i],lat[i],dep[i,j],tim,ptem[i,j],err)
                lin=lin+BUOY+'\n'
                f.write(lin)
        for j in range(dep.shape[1]):
            if salqc[i,j]==1:
                BUOY=' '+'{:7d}'.format(inst)
                P='{:5d}'.format(i+1)
                I='{:4d}'.format(indS)
                lin=create_line(P,I,lon[i],lat[i],dep[i,j],tim,sal[i,j],err)
                lin=lin+BUOY+'\n'
                f.write(lin)
elif obs=='GL':
    for i in range(dep.shape[0]):
        for j in range(dep.shape[1]):
            if temqc[i,j]==1:
                ptem[i,j]=sw.ptmp(sal[i,j],tem[i,j],sw.pres(dep[i,j],lat[i]))
                P='{:8d}'.format(i+1)
                I='{:8d}'.format(indT)
                lin=create_line(P,I,lon[i],lat[i],dep[i,j],tim,ptem[i,j],err)
                lin=lin+'\n'
                f.write(lin)
        for j in range(dep.shape[1]):
            if salqc[i,j]==1:
                P='{:8d}'.format(i+1)
                I='{:8d}'.format(indS)
                lin=create_line(P,I,lon[i],lat[i],dep[i,j],tim,sal[i,j],err)
                lin=lin+'\n'
                f.write(lin)
else:
    for i in range(dep.shape[0]):
        for j in range(dep.shape[1]):
            if temqc[i,j]==1:
                P='{:8d}'.format(i+1)
                I='{:8d}'.format(indT)
                lin=create_line(P,I,lon[i],lat[i],dep[i,j],tim,ptem[i,j],err)
                lin=lin+'\n'
                f.write(lin)
f.close() 
