#!/bin/sh -l

Today=`date +%b%d%Y`
YYYYMM=`echo $1 | cut -c 1-6`
bm=`echo $Today | cut -c 1-3`
dm=`echo $Today | cut -c 4-5`
ym=`echo $Today | cut -c 6-9`

cd ${MYE_ALLOUTDIR}/output-QVR
ncrcat -h ./????????/${YYYYMM}??.TEMP.nc TEMP.nc

ncks -h -d forecasts,0,1 TEMP.nc TEMP_ca.nc 
ncks -h -d forecasts,11,11 TEMP.nc TEMP_p.nc
ncks -h -d forecasts,13,13 TEMP.nc TEMP_ff.nc 
ncks -h -d forecasts,15,15 TEMP.nc TEMP_t.nc 
ncks -h -d forecasts,17,17 TEMP.nc TEMP_f.nc
ncks -h -d forecasts,21,21 TEMP.nc TEMP_n.nc
ncpdq -O -h -a forecasts,time TEMP_ca.nc TEMP_ca.nc 
ncpdq -O -h -a forecasts,time TEMP_p.nc TEMP_p.nc
ncpdq -O -h -a forecasts,time TEMP_ff.nc TEMP_ff.nc 
ncpdq -O -h -a forecasts,time TEMP_t.nc TEMP_t.nc
ncpdq -O -h -a forecasts,time TEMP_f.nc TEMP_f.nc
ncpdq -O -h -a forecasts,time TEMP_n.nc TEMP_n.nc 
ncrcat -h TEMP_ca.nc TEMP_p.nc TEMP_ff.nc TEMP_t.nc TEMP_f.nc TEMP_n.nc TEMP_final.nc
ncpdq -O -h -a time,forecasts TEMP_final.nc TEMP_final.nc
rm TEMP_ca.nc TEMP_p.nc TEMP_ff.nc TEMP_t.nc TEMP_f.nc TEMP_n.nc 
ncatted -O -h -a units,time,m,c,"days since 1950-01-01 00:00:00" TEMP_final.nc TEMP_final.nc
ncatted -O -h -a start_date,global,c,c,"$1" TEMP_final.nc
ncatted -O -h -a end_date,global,c,c,"$2" TEMP_final.nc
ncatted -O -h -a creation_date,global,c,c,"$bm $dm $ym" TEMP_final.nc
mv TEMP_final.nc product_quality_stats_MEDSEA-ANALYSISFORECAST-PHY-006-013_${1}_${2}.nc
