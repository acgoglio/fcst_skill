#module load intel
module load NETCDF/netcdf-4.3

#module purge intel

EXTINC="-I/users/home/opt/netcdf/netcdf-4.3/include/"
EXTLIB="-L/users/home/opt/netcdf/netcdf-4.3/lib -lnetcdff -lnetcdf -lhdf5_hl -lhdf5 -lcurl"
rm slaean2.exe
Cmd="mpiifort slaean2.f90 -o slaean2.exe $EXTINC $EXTLIB" 
echo $Cmd
eval $Cmd
