#!/bin/sh
## Shift SST di input su griglia modello NEMO MFS16 
## Giacomo Girardi, 12.02.2013

InDir=$1

#BinDir=`dirname $0`/MFS_QVR.dir
BinDir=`dirname $0`

Cmd="cd $InDir"
echo $Cmd
eval $Cmd

#source /etc/profile.d/modules.sh

for InFile in `ls -1 *-GOS-L3S_GHRSST-SSTsubskin-night_SST_HR_NRT-MED-*` ; do
  if [ -f $InFile ] ; then

	Cmd="rm -f 1.nc 2.nc shift.nc south.nc lat2 boundary rest"
	echo $Cmd
	eval $Cmd

	AnalysedDay=`basename $InFile | cut -c 1-8`
	yyyy=`echo $AnalysedDay | cut -c"1-4"`
        mm=`echo $AnalysedDay | cut -b"5 6"`
	dd=`echo $AnalysedDay | cut -b"7 8"`

	Cmd="ncks -O -d lat,0,251 -v sea_surface_temperature $InFile 1.nc "
	echo $Cmd
	eval $Cmd

	Cmd="ncatted -h -a ,lat,d,, -a ,lon,d,, -a ,global,d,, -a ,sea_surface_temperature,d,, 1.nc  "
	echo $Cmd
	eval $Cmd

	Cmd="ncatted -a scale_factor,sea_surface_temperature,c,f,0.01 -a units,sea_surface_temperature,c,c,'Celsius'  -a _FillValue,sea_surface_temperature,c,s,-99 1.nc "
	echo $Cmd
	eval $Cmd
#	Cmd="ncatted -a scale_factor,analysis_error,c,f,0.01 -a units,analysis_error,c,c,'Celsius'  -a _FillValue,analysis_error,c,s,-99 1.nc "
#	echo $Cmd
#	eval $Cmd  

	Cmd="cdo setmissval,0 1.nc 2.nc"
	echo $Cmd
	eval $Cmd 

	Cmd="ncks -O -d lat,1 -v sea_surface_temperature  2.nc lat2"
	echo $Cmd
	eval $Cmd

	Cmd="ncks -O -d lat,0 -v sea_surface_temperature  2.nc boundary"
	echo $Cmd
	eval $Cmd

	Cmd="ncks -O -d lat,1,251 -v sea_surface_temperature  2.nc rest"
	echo $Cmd
	eval $Cmd


	Cmd="ncap -O -s 'lat=30.25'   lat2 lat2"
	echo $Cmd
	eval $Cmd
	Cmd="ncecat -O -h lat2 lat2"
	echo $Cmd
	eval $Cmd
	Cmd="ncpdq -O -h -a lat,record lat2 lat2"
	echo $Cmd
	eval $Cmd

	Cmd="ncap -O -s 'lat=30.1875'   boundary boundary"
	echo $Cmd
	eval $Cmd
	Cmd="ncecat -O -h boundary boundary"
	echo $Cmd
	eval $Cmd
	Cmd="ncpdq -O -h -a lat,record boundary boundary"
	echo $Cmd
	eval $Cmd

	Cmd="ncecat -O -h rest shift.nc "
	echo $Cmd
	eval $Cmd
	Cmd="ncpdq -O -h -a lat,record shift.nc  shift.nc "
	echo $Cmd
	eval $Cmd
	Cmd="ncrcat -O  boundary lat2 south.nc "
	echo $Cmd
	eval $Cmd


	Cmd="ncrcat -O  south.nc shift.nc new.nc "
	echo $Cmd
	eval $Cmd
	Cmd="ncwa -O -a record new.nc new.nc"
	echo $Cmd
	eval $Cmd
	Cmd="ncpdq -O -h -a time,lat new.nc new.nc"
	echo $Cmd
	eval $Cmd

	Cmd="ncrename -h -d lon,x -d lat,y new.nc"
	echo $Cmd
	eval $Cmd

	Cmd="ncatted  -a units,sea_surface_temperature,c,c,'Celsius' new.nc"
	echo $Cmd
	eval $Cmd

	Cmd="ncks -O -v sea_surface_temperature new.nc new.nc"
	echo $Cmd
	eval $Cmd

	Cmd="ncbo -O -y mlt new.nc $BinDir/T3Smask.nc new.nc"
	echo $Cmd
	eval $Cmd

	OutName=`echo sst_3S_data_y${yyyy}m${mm}d${dd}.nc`
	Cmd="mv new.nc ${OutName}"   
	echo $Cmd
	eval $Cmd

 fi
done
