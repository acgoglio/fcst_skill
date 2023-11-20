#!/bin/sh -l

cd
if [ $1 == "R" ] ; then
     source activate /users_home/opa/ag22216/.conda/envs/myenv4 
#    source activate .conda/envs/myenv4
#    source activate /users_home/oda/aa32919/.conda/envs/myenv4
fi
if [ $1 == "N" ] ; then
    source activate /users_home/opa/ag22216/.conda/envs/myenv4 
    #source activate .conda/envs/myenv4
    module purge
    module load intel19.5/19.5.281 intel19.5/netcdf-threadsafe/C_4.7.2-F_4.5.2_CXX_4.3.1
    module load intel19.5/nco/4.8.1
    module load impi19.5/19.5.281 impi19.5/netcdf/C_4.7.2-F_4.5.2_CXX_4.3.1
    module load intel19.5/ncview/2.1.8
    # For SST
    module load intel19.5/cdo/1.9.8
    module load intel19.5/magics/3.3.1
    module load intel19.5/eccodes/2.12.5
#    module load intel20.1/eccodes/2.17.0
fi
if [ $1 == "E1" ] ; then
# For ECMWF wgrib1
    source activate .conda/envs/myenv4 
    module purge
    module load wgrib/1.8.1.0b
    module load impi19.5/19.5.281
    module load intel19.5/19.5.281
    module load intel19.5/eccodes/2.12.5
    module load impi19.5/netcdf/C_4.7.2-F_4.5.2_CXX_4.3.1
    module load impi19.5/hdf5/1.10.5
    module load intel19.5/szip/2.1.1
    module load intel19.5/udunits/2.2.26
    module load intel19.5/magics/3.3.1
    module load intel19.5/cdo/1.9.8
    module load intel19.5/nco/4.8.1
#    module load anaconda/3.7
fi

if [ $1 == "E2" ] ; then
# For ECMWF wgrib2
    module purge
    module load intel19.5/wgrib2/0.2.0.8
    module load impi19.5/19.5.281
    module load intel19.5/19.5.281
    module load intel19.5/eccodes/2.12.5
    module load impi19.5/netcdf/C_4.7.2-F_4.5.2_CXX_4.3.1
    module load impi19.5/hdf5/1.10.5
    module load intel19.5/szip/2.1.1
    module load intel19.5/udunits/2.2.26
    module load intel19.5/magics/3.3.1
    module load intel19.5/cdo/1.9.8
    module load intel19.5/nco/4.8.1
    module load anaconda/3.7
fi

if [ $1 == "S" ] ; then
# For test pre-proc SST
    module purge
    module load intel19.5/19.5.281 
    module load impi19.5/19.5.281 
    module load impi19.5/netcdf/C_4.7.2-F_4.5.2_CXX_4.3.1 
    module load impi19.5/hdf5/1.10.5
    module load intel19.5/nco/4.8.1

    export SST_NEMO_INTERP_PATH=/work/opa/md04916/eas6/dev_eas6_v3_hdepth/pack/NEMO_V3.6_rep/NEMOGCM/TOOLS/WEIGHTS/BLD/bin/scripinterp.exe
    export SST_DATA0=/data/opa/md04916/Med_static/MFS_REA24V2_STATIC/SST_DATA0_v3
fi 
