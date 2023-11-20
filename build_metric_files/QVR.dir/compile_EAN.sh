#module load intel
module load NETCDF/netcdf-4.3

#module purge intel

EXTINC="-I/users/home/opt/netcdf/netcdf-4.3/include/"
EXTLIB="-L/users/home/opt/netcdf/netcdf-4.3/lib -lnetcdff -lnetcdf -lhdf5_hl -lhdf5 -lcurl"
rm argoean.exe
Cmd="mpiifort -g set_knd_oceanvar.f90 obs_str_oceanvar.f90 argoean.f90 -o argoean.exe $EXTINC $EXTLIB"
echo $Cmd
eval $Cmd
rm gliderean.exe
Cmd="mpiifort -g set_knd_oceanvar.f90 obs_str_oceanvar.f90 gliderean.f90 -o gliderean.exe $EXTINC $EXTLIB"
echo $Cmd
eval $Cmd
rm xbtean.exe
Cmd="mpiifort -g set_knd_oceanvar.f90 obs_str_oceanvar.f90 xbtean.f90 -o xbtean.exe $EXTINC $EXTLIB"
echo $Cmd
eval $Cmd
rm sstean.exe
Cmd="mpiifort sstean.f90 -o sstean.exe $EXTINC $EXTLIB"
echo $Cmd
eval $Cmd
rm sstcloudean.exe
Cmd="mpiifort sstcloudean.f90 -o sstcloudean.exe $EXTINC $EXTLIB"
echo $Cmd
eval $Cmd
rm slaean.exe
Cmd="mpiifort slaean.f90 -o slaean.exe $EXTINC $EXTLIB" 
echo $Cmd
eval $Cmd
