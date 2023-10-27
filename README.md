# fcst_skill
  for DAYN in 0 1 2 3 4 5 6 ; do DAY_1=$(( $DAYN + 1 )) ; ncks -d time,${DAYN},${DAYN} -o /work/oda/ag15419/tmp/Ana_Fcst_2023/2022010${DAY_1}.TEMP.nc /work/opa/ag22216/testVALFOR/TEMP_141.nc  ; done
  for DAYN in 0 1 2 3 4 5 6 ; do DAY_1=$(( $DAYN + 1 )) ; ncks -d time,${DAYN},${DAYN} -o /work/oda/ag15419/tmp/Ana_Fcst_testVALFOR_18/2022010${DAY_1}.TEMP.nc /work/opa/ag22216/testVALFOR_18/TEMP_18.nc  ; done
