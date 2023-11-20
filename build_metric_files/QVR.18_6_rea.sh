#!/bin/sh -l
set -x

#InDir=$1
WorkDir=/work/oda/ag15419/tmp/Ana_Fcst/testVALFOR_18_6_rea/work/ #Da modificare
#LogDir=$3
OutDir=/work/oda/ag15419/tmp/Ana_Fcst/testVALFOR_18_6_rea/out/ #Da modificare

ds=$1
de=$2

BinDir=`dirname $0`/`basename $0 | cut -d . -f -1`.dir

count_line() {

if [ -f ${day}.${1}.dat ] ; then
    counter=`wc -l "${day}.${1}.dat" | awk '{print $1'}`
    echo $counter > nlines${1}.txt
    cat nlines${1}.txt ${day}.${1}.dat > ${1}.dat
    rm ${day}.${1}.dat nlines${1}.txt 
else
    echo " There are no ${1} data"
fi
}

cut_file(){

ncks -v nav_lat,nav_lon,time_counter,sossheig $1 SSH.nc

for i in 0 1 2 3 4 7 10 15 19 23 30 35 39 43 49 57 65 72 ; do
    ncks -d deptht,${i},${i} -v votemper,vosaline,deptht $1 TEMP_${i}.nc
    ncpdq -O -h -a deptht,time_counter TEMP_${i}.nc TEMP_${i}.nc
done
ncrcat TEMP_?.nc TEMP_??.nc TEMP.nc
ncpdq -O -a time_counter,deptht TEMP.nc TEMP.nc
ncks -A SSH.nc TEMP.nc
rm SSH.nc TEMP_?.nc TEMP_??.nc
mv TEMP.nc $1
}

#cd $InDir

#ProcDay=`basename procday.* | cut -d . -f 2`
ProcDay=20220101 # Eventualmente da modificare
year=`echo $ProcDay | cut -c 1-4`

echo "I am working on year: $year"

#ln -s ${NRT_STDATA}/eval-MVR/${ProcDay}/*.nc .

#DirData=$MYE_MFSINDATA
#NRT_SYSNAME=`echo $MYENVDEV_ALIAS | tr '[:upper:]' '[:lower:]'`
MYENVDEV_ALIAS=MED_REA #da modificre
ModName=`echo $MYENVDEV_ALIAS | cut -c 5-8`
MYE_MFSINDATA=/data/opa/mfs/MFS_INDATA_EAS7/
NRT_SYSNAME=med_rea # Da modificare
NRT_SYSNAME_CL=mfs_eas6v8
if [ $NRT_SYSNAME == "mfs_eas5" ] ; then
    diran=be_data
    dirfc=fc
elif [ $NRT_SYSNAME == "med_rea" ] ; then
    diran=day
    dirfc=day
else
    diran=analysis_daily_mean # Da modificare 
    dirfc=bulletin  # Da modificare
fi

VAL_WORKDIR=/data/opa/ag22216/for_val_EAS6/ #Directory file sy=tatici
MYE_DELIVERY2=/data/inputs/metocean/historical/model/ocean/CMCC/CMEMS/reanalysis/native/ #Directory dove sono archiviati i file da utilizzare

cd $WorkDir
echo "I am in $pwd"

for i in `seq $ds $de` ; do
    cd $WorkDir/
    day=`python ${BinDir}/jday.py $ProcDay ${i}`
    dayb=`python ${BinDir}/jday.py $day +1`
    echo " I am working on day: $day"
    yyyy=`echo $day | cut -c 1-4`
    mm=`echo $day | cut -c 5-6`    
    if [ ! -d ${day} ] ; then
      mkdir $WorkDir/${day}
    fi
    if [ ! -d ${day}/tmp ] ; then
      mkdir -p $WorkDir/${day}/tmp
    fi
# DECOMMENTARE
#    bestest=`find -L $MYE_DELIVERY2/$diran -name {NRT_SYSNAME}*-${day}-a-T.nc`
    dayfc1=`python ${BinDir}/jday.py ${day} 0`
    dayfc2=`python ${BinDir}/jday.py ${day} 0`
    dayfc3=`python ${BinDir}/jday.py ${day} 0`
    dayfc4=`python ${BinDir}/jday.py ${day} 0`
    dayfc5=`python ${BinDir}/jday.py ${day} 0`
    dayfc6=`python ${BinDir}/jday.py ${day} 0`
    dayfc7=`python ${BinDir}/jday.py ${day} 0`
    dayfc8=`python ${BinDir}/jday.py ${day} 0`
    dayfc9=`python ${BinDir}/jday.py ${day} 0`
    dayfc10=`python ${BinDir}/jday.py ${day} 0`
    # Da decidere la climatologia
    cl=`find -L ${VAL_WORKDIR}/QVR_DATA0/ -name ${NRT_SYSNAME_CL}-20210301-2019${mm}01-a-T.nc`
    # Da modificare 95-116 in base a nome file utilizzati rea_202201_202207_1d_20220113_grid_T.nc
    bestest=`find -L $MYE_DELIVERY2/$diran -name rea_*-${day}_grid_T.nc`
    bestest=`find -L $MYE_DELIVERY2/$diran -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}*-${day}-a-T.nc`
    sm=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` # ${NRT_SYSNAME}-${dayb}-${day}-s-T.nc`
    fc1=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` # ${NRT_SYSNAME}-${dayfc1}-${day}-f-T.nc`
    ps1=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc1}-${day}-f-T.nc`
    fc2=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc2}-${day}-f-T.nc`
    ps2=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc2}-${dayfc2}-f-T.nc`
    fc3=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc3}-${day}-f-T.nc`
    ps3=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc3}-${dayfc3}-f-T.nc`
    fc4=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc4}-${day}-f-T.nc`
    ps4=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc4}-${dayfc4}-f-T.nc`
    fc5=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc5}-${day}-f-T.nc`
    ps5=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc5}-${dayfc5}-f-T.nc`
    fc6=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc6}-${day}-f-T.nc`
    ps6=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc6}-${dayfc6}-f-T.nc`
    fc7=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc7}-${day}-f-T.nc`
    ps7=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc7}-${dayfc7}-f-T.nc`
    fc8=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc8}-${day}-f-T.nc`
    ps8=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` # ${NRT_SYSNAME}-${dayfc8}-${dayfc8}-f-T.nc`
    fc9=`find -L $MYE_DELIVERY2/$dirfc -name  rea_*-${day}_grid_T.nc` # ${NRT_SYSNAME}-${dayfc9}-${day}-f-T.nc`
    ps9=`find -L $MYE_DELIVERY2/$dirfc -name  rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc9}-${dayfc9}-f-T.nc`
    fc10=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` #${NRT_SYSNAME}-${dayfc10}-${day}-f-T.nc`
    ps10=`find -L $MYE_DELIVERY2/$dirfc -name rea_*-${day}_grid_T.nc` # ${NRT_SYSNAME}-${dayfc10}-${dayfc10}-f-T.nc`
    lcl=mfs_easO-20210301-2019${mm}01-a-T.nc
    # esempio di file finale mfs_easO-20220529-20220601-f-T.nc
    bbestest=med_reaO-${ProcDay}-${day}-a-T.nc
    bsm=mfs_reaO-${dayb}-${day}-s-T.nc
    bfc1=mfs_reaO-$(echo `basename $fc1` | cut -d '-' -f2-)
    bfc2=mfs_reaO-$(echo `basename $fc2` | cut -d '-' -f2-)
    bfc3=mfs_reaO-$(echo `basename $fc3` | cut -d '-' -f2-)
    bfc4=mfs_reaO-$(echo `basename $fc4` | cut -d '-' -f2-)
    bfc5=mfs_reaO-$(echo `basename $fc5` | cut -d '-' -f2-)
    bfc6=mfs_reaO-$(echo `basename $fc6` | cut -d '-' -f2-)
    bfc7=mfs_reaO-$(echo `basename $fc7` | cut -d '-' -f2-)
    bfc8=mfs_reaO-$(echo `basename $fc8` | cut -d '-' -f2-)
    bfc9=mfs_reaO-$(echo `basename $fc9` | cut -d '-' -f2-)
    bfc10=mfs_reaO-$(echo `basename $fc10` | cut -d '-' -f2-)
    bps1=mfs_reaO-$(echo `basename $ps1` | cut -d '-' -f2-)
    bps2=mfs_reaO-$(echo `basename $ps2` | cut -d '-' -f2-)
    bps3=mfs_reaO-$(echo `basename $ps3` | cut -d '-' -f2-)
    bps4=mfs_reaO-$(echo `basename $ps4` | cut -d '-' -f2-)
    bps5=mfs_reaO-$(echo `basename $ps5` | cut -d '-' -f2-)
    bps6=mfs_reaO-$(echo `basename $ps6` | cut -d '-' -f2-)
    bps7=mfs_reaO-$(echo `basename $ps7` | cut -d '-' -f2-)
    bps8=mfs_reaO-$(echo `basename $ps8` | cut -d '-' -f2-)
    bps9=mfs_reaO-$(echo `basename $ps9` | cut -d '-' -f2-)
    bps10=mfs_reaO-$(echo `basename $ps10` | cut -d '-' -f2-)
    Cmd="ln -s $cl ./${day}/${lcl}"
    echo $Cmd
    eval $Cmd
    cp $bestest ./${day}/$bbestest
    cp $sm ./${day}/$bsm
    cp $fc1 ./${day}/$bfc1
    cp $fc2 ./${day}/$bfc2
    cp $fc3 ./${day}/$bfc3
    cp $fc4 ./${day}/$bfc4
    cp $fc5 ./${day}/$bfc5
    cp $fc6 ./${day}/$bfc6
    cp $fc7 ./${day}/$bfc7
    cp $fc8 ./${day}/$bfc8
    cp $fc9 ./${day}/$bfc9
    cp $fc10 ./${day}/$bfc10
    cp $ps1 ./${day}/$bps1
    cp $ps2 ./${day}/$bps2
    cp $ps3 ./${day}/$bps3
    cp $ps4 ./${day}/$bps4
    cp $ps5 ./${day}/$bps5
    cp $ps6 ./${day}/$bps6
    cp $ps7 ./${day}/$bps7
    cp $ps8 ./${day}/$bps8
    cp $ps9 ./${day}/$bps9
    cp $ps10 ./${day}/$bps10
 
    bcl=`basename $lcl`
#
#---- Copy file INSITU ----
    for tfl in PF BA ; do
        for ccFile in `find -L ${MYE_MFSINDATA}/INSITU_MED_NRT_OBSERVATIONS_013_035-med_multiparameter_nrt/${day} -name *_PR_${tfl}_*_${day}*`; do
            fileName=`basename $ccFile`
            pref=`echo $fileName | cut -c 1-3`
            suf=`echo $fileName | cut -c 3-`
            fileNew=${pref}LATEST${suf}
            Cmd="python ${BinDir}/Converter.py $ccFile ./${day}/$fileNew"
            echo $Cmd
            eval $Cmd
        done
    done
    
#---- Copy file SST L4----
    DirSat=${MYE_MFSINDATA}/SST_L4
    filesstl4=`find -L ${DirSat}/ -name ${day}000000-GOS-L4_GHRSST-SSTfnd-OISST_HR_NRT-MED-v02.0-fv02.0.nc`
    cp $filesstl4 ./${day}/.
#---- Copy file SST L3S----
    DirSatb=${MYE_MFSINDATA}/SST_L3S
    filesstl3s=`find -L ${DirSatb}/ -name ${day}000000-GOS-L3S_GHRSST-SSTsubskin-night_SST_HR_NRT-MED-v02.0-fv01.0.nc`
    cp $filesstl3s ./${day}/.
#---- Copy SLA ----
    DirSla=${MYE_MFSINDATA}/SLA_EUR202003_
    for sat in AL C2 J3 J2G S3A S3B C2N J3N S6A H2A H2B ; do
        SatName=`echo $sat | tr '[:upper:]' '[:lower:]'`
        if [ $SatName != 's6a' ] ; then
            file=`find -L ${DirSla}${sat}/ -name nrt_europe_${SatName}_phy_l3_${day}_*.nc | sort | tail -1`
            cp $file ./${day}/.
        else
            file=`find -L ${DirSla}${sat}/ -name nrt_europe_${SatName}_hr_phy_l3_${day}_*.nc | sort | tail -1`
            filen=`basename $file`
            file1=`echo $filen | cut -d '_' -f1-3`
            file2=`echo $filen | cut -d '_' -f5-`
            cp $file ./${day}/${file1}_${file2}
        fi
    done
#---- Pre-proc insitu data ----
    cd ${WorkDir}/${day}
    for argofile in `find *_LATEST_PR_PF_*` ; do 
        echo $argofile
        ${BinDir}/prep_ARGO_3dvar_C3_V3.exe ./ ./tmp/ $argofile $day 
    done
#    for gliderfile in `find *_LATEST_PR_GL_*` ; do
#        echo $gliderfile
#        buoy=`echo $gliderfile | cut -f 5 -d _`
#        ${BinDir}/prep_GLIDER_3dvar_C3_V3.exe ./ ./tmp/ $gliderfile $day $buoy
#    done
    for xbtfile in `find *_LATEST_PR_BA_*` ; do
        echo $xbtfile
        buoy=`echo $xtfile | cut -f 5 -d _`
        ${BinDir}/prep_XBT_3dvar_C3_V3.exe ./ ./tmp/ $xbtfile $day $buoy
    done
    rm *_LATEST_PR_*
    mv ./tmp/*_LATEST_PR_* .
    rm -rf ${WorkDir}/tmp
#----- Conversion from NetCDF to ASCII -----
    for filea in `find *_LATEST_PR_*` ; do
        echo $filea
        Cmd="python ${BinDir}/convert_INSITU.py ./ ./ $filea $day"
        echo $Cmd
        eval $Cmd
    done
    for inst in ARGO XBT ; do
        count_line $inst
    done
    rm *_LATEST_PR_*
    Cmd="ln -s ${VAL_WORKDIR}/QVR_DATA0/MFS_24_20y_mdt_final_full.nc MFS_24_y_mdt_final_full.nc"
    echo $Cmd
    eval $Cmd
    Cmd="ln -s ${VAL_WORKDIR}/QVR_DATA0/MFS_QVR_17r_16_20.nc MFS_QVR_17r_16_20.nc"
    echo $Cmd
    eval $Cmd
    Cmd="ln -s ${VAL_WORKDIR}/QVR_DATA0/sample_sst.nc sample_sst.nc"
    echo $Cmd
    eval $Cmd
    Cmd="ln -s ${VAL_WORKDIR}/QVR_DATA0/mygrid_16deg mygrid_16deg"
    echo $Cmd
    eval $Cmd
    Cmd="ln -s ${VAL_WORKDIR}/QVR_DATA0/mygrid_24deg mygrid_24deg"
    echo $Cmd
    eval $Cmd
    count=0
    # Da commentere il ciclo for che fa il sottocampionamento dei livelli. Utilizzare solo per MFS
    for filetocut in $bcl $bbestest $bps10 $bps9 $bps8 $bps7 $bps6 $bps5 $bps4 $bps3 $bps2 $bsm $bfc1 $bfc2 $bfc3 $bfc4 $bfc5 $bfc6 $bfc7 $bfc8 $bfc9 $bfc10 ; do
       cut_file $filetocut
    done
    for filemod in $bcl $bbestest $bps10 $bps9 $bps8 $bps7 $bps6 $bps5 $bps4 $bps3 $bps2 $bps1 $bsm $bfc1 $bfc2 $bfc3 $bfc4 $bfc5 $bfc6 $bfc7 $bfc8 $bfc9 $bfc10 ; do
        # ARGO
        if [ -f ARGO.dat ] ; then 
            Cmd="${BinDir}/argoean_18.exe $filemod"
            echo $Cmd
            eval $Cmd
        fi
        # XBT
        if [ -f XBT.dat ] ; then
            Cmd="${BinDir}/xbtean_18.exe $filemod"
            echo $Cmd
            eval $Cmd
        fi
        # GLIDER
#        if [ -f GLIDER.dat ] ; then
#            Cmd="${BinDir}/gliderean.exe $filemod"
#            echo $Cmd
#            eval $Cmd
#        fi
        Cmd="mv INSITU.csv ${day}.${count}.INSITU.csv"
        echo $Cmd
        eval $Cmd
        # SST
        Cmd="python ${BinDir}/interp_sst_cdo.py $filemod"
        echo $Cmd
        eval $Cmd
        filemod_sst=int_$filemod
        Cmd="cdo remapbil,mygrid_16deg -setgrid,mygrid_24deg test_$filemod $filemod_sst"
        echo $Cmd
        eval $Cmd
        ncks -x -O -h -v nav_lon_2,nav_lat_2 $filemod_sst $filemod_sst
        ncrename -O -h -d x,lon -d y,lat $filemod_sst $filemod_sst
        rm test_$filemod
        Cmd="ncks -O -d lon,50,870 $filemod_sst $filemod_sst"
        echo $Cmd
        eval $Cmd
        Cmd="cp ${day}000000-GOS-L4_GHRSST-SSTfnd-OISST_HR_NRT-MED-v02.0-fv02.0.nc sst.nc"
        echo $Cmd
        eval $Cmd
        Cmd="ncks -O -d lon,50,870 sst.nc sst.nc"
        echo $Cmd
        eval $Cmd
        Cmd="${BinDir}/sstean.exe $filemod_sst"
        echo $Cmd
        eval $Cmd
        Cmd="rm sst.nc"
        echo $Cmd
        eval $Cmd
        Cmd="mv SST.csv ${day}.${count}.SSTL4.csv"
        echo $Cmd
        eval $Cmd
        Cmd="cp ${day}000000-GOS-L3S_GHRSST-SSTsubskin-night_SST_HR_NRT-MED-v02.0-fv01.0.nc sst.nc"
        echo $Cmd
        eval $Cmd
        Cmd="ncks -O -d lon,50,870 sst.nc sst.nc"
        echo $Cmd
        eval $Cmd
        Cmd="${BinDir}/sstcloudean.exe $filemod_sst"
        echo $Cmd
        eval $Cmd
        Cmd="rm sst.nc"
        echo $Cmd
        eval $Cmd
        Cmd="mv SST.csv ${day}.${count}.SSTL3S.csv"
        echo $Cmd
        eval $Cmd
        # SLA
        # AGGIUNGERCI S3A
        for dirsat in AL C2 J3 J2G S3A S3B C2N J3N S6A H2A H2B ; do
            SlaName=`echo $dirsat | tr '[:upper:]' '[:lower:]'`
            filestr=`echo $SlaName | cut -c 1-3`
            for slafile in `ls nrt_europe_${SlaName}_phy_l3_*` ; do
                echo $slafile
                Cmd="${BinDir}/slaeaneur.exe $filemod $slafile $day $filestr $ModName"
                echo $Cmd
                eval $Cmd
            done
        done
        Cmd="mv SLA.csv ${day}.${count}.SLA.csv"
        echo $Cmd
        eval $Cmd
        Cmd="python ${BinDir}/EAN_calc_v3.6.2_n.py ${day}.${count}.INSITU.csv res 17 9 1 $day $day ./ 4"
        echo $Cmd
        eval $Cmd
        Cmd="python ${BinDir}/EAN_calc_v3.6.2_n.py ${day}.${count}.INSITU.csv res 17 9 2 $day $day ./ 2"
        echo $Cmd
        eval $Cmd
        Cmd="cp ${day}.0.SSTL4.csv ${day}.0.SST.csv"
        echo $Cmd
        eval $Cmd
        Cmd="cp ${day}.${count}.SSTL4.csv ${day}.${count}.SST.csv"
        echo $Cmd
        eval $Cmd
        Cmd="python ${BinDir}/EAN_calc_v3.6.2_n.py ${day}.${count}.SST.csv res 17 1 3 $day $day ./ 0"
        echo $Cmd
        eval $Cmd
        Cmd="rm ${day}.${count}.SST.csv ${day}.0.SST.csv"
        echo $Cmd
        eval $Cmd
        Cmd="python ${BinDir}/createNC_SST.py res_${count}_SST_SST_${day}_${day}_EAN_STATS2.csv res_${count}_SST_SST_${day}_${day}_EAN2.csv $day $count"
        echo $Cmd
        eval $Cmd
        mv SST.nc ${day}.${count}.SSTL4.nc
        Cmd="mv res_${count}_SST_SST_${day}_${day}_EAN2.csv res_${count}_SSTL4_SSTL4_${day}_${day}_EAN2.csv"
        echo $Cmd
        eval $Cmd
        Cmd="mv res_${count}_SST_SST_${day}_${day}_EAN_STATS2.csv res_${count}_SSTL4_SSTL4_${day}_${day}_EAN_STATS2.csv"
        echo $Cmd
        eval $Cmd
        Cmd="cp ${day}.0.SSTL3S.csv ${day}.0.SST.csv"
        echo $Cmd
        eval $Cmd
        Cmd="cp ${day}.${count}.SSTL3S.csv ${day}.${count}.SST.csv"
        echo $Cmd
        eval $Cmd
        Cmd="python ${BinDir}/EAN_calc_v3.6.2_n.py ${day}.${count}.SST.csv res 17 1 3 $day $day ./ 0"
        echo $Cmd
        eval $Cmd
        Cmd="rm ${day}.${count}.SST.csv ${day}.0.SST.csv"
        echo $Cmd
        eval $Cmd
        Cmd="python ${BinDir}/createNC_SST.py res_${count}_SST_SST_${day}_${day}_EAN_STATS2.csv res_${count}_SST_SST_${day}_${day}_EAN2.csv $day $count"
        echo $Cmd
        eval $Cmd
        mv SST.nc ${day}.${count}.SSTL3S.nc
        Cmd="mv res_${count}_SST_SST_${day}_${day}_EAN2.csv res_${count}_SSTL3S_SSTL3S_${day}_${day}_EAN2.csv"
        echo $Cmd
        eval $Cmd
        Cmd="mv res_${count}_SST_SST_${day}_${day}_EAN_STATS2.csv res_${count}_SSTL3S_SSTL3S_${day}_${day}_EAN_STATS2.csv"
        echo $Cmd
        eval $Cmd
        Cmd="python ${BinDir}/EAN_calc_v3.6.2_n.py ${day}.${count}.SLA.csv res 17 1 4 $day $day ./ 0"
        echo $Cmd
        eval $Cmd
        Cmd="python ${BinDir}/createNC_TEMP_n.py res_${count}_INSITU_TEMP_${day}_${day}_EAN_STATS2.csv res_${count}_INSITU_TEMP_${day}_${day}_EAN2.csv $day $count" 
        echo $Cmd
        eval $Cmd
        Cmd="python ${BinDir}/createNC_PSAL_n.py res_${count}_INSITU_SALT_${day}_${day}_EAN_STATS2.csv res_${count}_INSITU_SALT_${day}_${day}_EAN2.csv $day $count"
        echo $Cmd
        eval $Cmd
        Cmd="python ${BinDir}/createNC_SSH.py res_${count}_SLA_SLA_${day}_${day}_EAN_STATS2.csv res_${count}_SLA_SLA_${day}_${day}_EAN2.csv $day $count"
        echo $Cmd
        eval $Cmd
        mv TEMP.nc ${day}.${count}.TEMP.nc
        mv PSAL.nc ${day}.${count}.PSAL.nc
        mv SSH.nc ${day}.${count}.SSH.nc
        ncpdq -O -h -a forecasts,time ${day}.${count}.TEMP.nc ${day}.${count}.TEMP.nc
        ncpdq -O -h -a forecasts,time ${day}.${count}.PSAL.nc ${day}.${count}.PSAL.nc
        ncpdq -O -h -a forecasts,time ${day}.${count}.SSH.nc ${day}.${count}.SSH.nc
        ncpdq -O -h -a forecasts,time ${day}.${count}.SSTL4.nc ${day}.${count}.SSTL4.nc
        ncpdq -O -h -a forecasts,time ${day}.${count}.SSTL3S.nc ${day}.${count}.SSTL3S.nc
        count=`expr ${count} + 1`
    done
    ncrcat -h ${day}.0.TEMP.nc ${day}.1.TEMP.nc ${day}.2.TEMP.nc ${day}.3.TEMP.nc ${day}.4.TEMP.nc ${day}.5.TEMP.nc ${day}.6.TEMP.nc ${day}.7.TEMP.nc ${day}.8.TEMP.nc ${day}.9.TEMP.nc ${day}.10.TEMP.nc ${day}.11.TEMP.nc ${day}.12.TEMP.nc ${day}.13.TEMP.nc ${day}.14.TEMP.nc ${day}.15.TEMP.nc ${day}.16.TEMP.nc ${day}.17.TEMP.nc ${day}.18.TEMP.nc ${day}.19.TEMP.nc ${day}.20.TEMP.nc ${day}.21.TEMP.nc ${day}.22.TEMP.nc TEMP.nc
    mv TEMP.nc ${OutDir}/${day}.TEMP.nc
    ncpdq -O -h -a time,forecasts ${OutDir}/${day}.TEMP.nc ${OutDir}/${day}.TEMP.nc
    ncrcat -h ${day}.0.PSAL.nc ${day}.1.PSAL.nc ${day}.2.PSAL.nc ${day}.3.PSAL.nc ${day}.4.PSAL.nc ${day}.5.PSAL.nc ${day}.6.PSAL.nc ${day}.7.PSAL.nc ${day}.8.PSAL.nc ${day}.9.PSAL.nc ${day}.10.PSAL.nc ${day}.11.PSAL.nc ${day}.12.PSAL.nc ${day}.13.PSAL.nc ${day}.14.PSAL.nc ${day}.15.PSAL.nc ${day}.16.PSAL.nc ${day}.17.PSAL.nc ${day}.18.PSAL.nc ${day}.19.PSAL.nc ${day}.20.PSAL.nc ${day}.21.PSAL.nc ${day}.22.PSAL.nc PSAL.nc
    mv PSAL.nc ${OutDir}/${day}.PSAL.nc
    ncpdq -O -h -a time,forecasts ${OutDir}/${day}.PSAL.nc ${OutDir}/${day}.PSAL.nc
    ncrcat -h ${day}.0.SSH.nc ${day}.1.SSH.nc ${day}.2.SSH.nc ${day}.3.SSH.nc ${day}.4.SSH.nc ${day}.5.SSH.nc ${day}.6.SSH.nc ${day}.7.SSH.nc ${day}.8.SSH.nc ${day}.9.SSH.nc ${day}.10.SSH.nc ${day}.11.SSH.nc ${day}.12.SSH.nc ${day}.13.SSH.nc ${day}.14.SSH.nc ${day}.15.SSH.nc ${day}.16.SSH.nc ${day}.17.SSH.nc ${day}.18.SSH.nc ${day}.19.SSH.nc ${day}.20.SSH.nc ${day}.21.SSH.nc ${day}.22.SSH.nc SSH.nc
    mv SSH.nc ${OutDir}/${day}.SSH.nc
    ncpdq -O -h -a time,forecasts ${OutDir}/${day}.SSH.nc ${OutDir}/${day}.SSH.nc
    ncrcat -h ${day}.0.SSTL4.nc ${day}.1.SSTL4.nc ${day}.2.SSTL4.nc ${day}.3.SSTL4.nc ${day}.4.SSTL4.nc ${day}.5.SSTL4.nc ${day}.6.SSTL4.nc ${day}.7.SSTL4.nc ${day}.8.SSTL4.nc ${day}.9.SSTL4.nc ${day}.10.SSTL4.nc ${day}.11.SSTL4.nc ${day}.12.SSTL4.nc ${day}.13.SSTL4.nc ${day}.14.SSTL4.nc ${day}.15.SSTL4.nc ${day}.16.SSTL4.nc ${day}.17.SSTL4.nc ${day}.18.SSTL4.nc ${day}.19.SSTL4.nc ${day}.20.SSTL4.nc ${day}.21.SSTL4.nc ${day}.22.SSTL4.nc SSTL4.nc
    mv SSTL4.nc ${OutDir}/${day}.SSTL4.nc
    ncpdq -O -h -a time,forecasts ${OutDir}/${day}.SSTL4.nc ${OutDir}/${day}.SSTL4.nc
    ncrcat -h ${day}.0.SSTL3S.nc ${day}.1.SSTL3S.nc ${day}.2.SSTL3S.nc ${day}.3.SSTL3S.nc ${day}.4.SSTL3S.nc ${day}.5.SSTL3S.nc ${day}.6.SSTL3S.nc ${day}.7.SSTL3S.nc ${day}.8.SSTL3S.nc ${day}.9.SSTL3S.nc ${day}.10.SSTL3S.nc ${day}.11.SSTL3S.nc ${day}.12.SSTL3S.nc ${day}.13.SSTL3S.nc ${day}.14.SSTL3S.nc ${day}.15.SSTL3S.nc ${day}.16.SSTL3S.nc ${day}.17.SSTL3S.nc ${day}.18.SSTL3S.nc ${day}.19.SSTL3S.nc ${day}.20.SSTL3S.nc ${day}.21.SSTL3S.nc ${day}.22.SSTL3S.nc SSTL3S.nc
    mv SSTL3S.nc ${OutDir}/${day}.SSTL3S.nc
    ncpdq -O -h -a time,forecasts ${OutDir}/${day}.SSTL3S.nc ${OutDir}/${day}.SSTL3S.nc
    ncrename -O -h -v stats_sst,stats_sstl3s ${OutDir}/${day}.SSTL3S.nc ${OutDir}/${day}.SSTL3S.nc
    ncatted -O -h -a reference,stats_sstl3s,o,c,"SST L3S from OSI TAC" ${OutDir}/${day}.SSTL3S.nc
    ncks -h -A ${OutDir}/${day}.PSAL.nc ${OutDir}/${day}.TEMP.nc
    ncks -h -A ${OutDir}/${day}.SSH.nc ${OutDir}/${day}.TEMP.nc
    ncks -h -A ${OutDir}/${day}.SSTL4.nc ${OutDir}/${day}.TEMP.nc
    ncks -h -A ${OutDir}/${day}.SSTL3S.nc ${OutDir}/${day}.TEMP.nc
    ncks -h -d depths,0,5 ${OutDir}/${day}.TEMP.nc ${OutDir}/${day}.TEMP.nc
    mv ${WorkDir}/${day}/${day}.1.SSTL4.csv ${OutDir}/${day}.exp001.SST.csv
    mv ${WorkDir}/${day}/${day}.1.SSTL3S.csv ${OutDir}/${day}.exp001.SSTL3S.csv
    rm -rf $WorkDir/${day}
done

if ls "${WorkDir}"/*.nc &> /dev/null; then
    rm "${WorkDir}"/*.nc
fi
