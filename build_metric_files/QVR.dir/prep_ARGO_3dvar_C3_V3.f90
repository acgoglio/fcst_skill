      include './netcdf.inc'

!INPUT:
! 1-file name 2-Date

      character*256 :: indir, outdir, infile, listfile, errfile
      character*28 :: oufile
      integer ::  ist, ncid,  prof, lev, N, cln, start(2), count(2)
      integer :: yyyy, mm, dd, hh, mn, longitude, latitude, posit
      integer :: rejobsqo, rejobsso, rejobsto, rejobsbo
      integer :: rejobsho, rejobsmo, rejobspo
      integer :: rejproho, rejpromo, rejpropo, rejproqo
      integer :: rejobsq, rejobss, rejobst, rejobsb
      integer :: rejobsh, rejobsm, rejobsp
      integer :: rejproh, rejprom, rejprop, rejproq
      integer :: dimen(2), diment(1), dimenst(1), dimenstb(1)
      integer :: dimenla(1), dimenlo(1), dimenp(1)
      integer :: depoid, posoid, lonoid, latoid, timoid, toid, iddcr
      integer :: tmoid, tmqoid, lonvoid, latvoid, posqoid, wmooid
      integer :: poid, pqoid, soid, sqoid, tqoid, pnoid, stroid,strboid
      double precision,dimension(:), allocatable :: jul, lat, lon
      double precision :: julo
      double precision,dimension(:), allocatable :: jul_qc,pos_qc
      character*32 ::  pln
      character(len=32),allocatable :: dcr(:)
      integer::  iihour, iimin, A, B, M, P, Q
      double precision,dimension(:), allocatable:: tem_qc, sal_qc,pre_qc
      real,dimension(:), allocatable :: pres, tem, sal, dpt, s
      real :: presmis, temmis, salmis
      real,dimension(:), allocatable :: bfrq, xx, r, errs, errt 
      real,dimension(:,:), allocatable :: X, PRO, PROH
      integer,dimension(:), allocatable :: temo_qc, psalo_qc, depo_qc
      real :: DATA(5000,3), DAT(5000,3),  limit, mean, real
      character*2 :: cmon, cday,chr,cmin
      character*4 cyear
      integer dateb
      character*8 date
      character*7 wpc
      character(len=10)::odate
      character(len=5)::  otime
!!!!! DICHIARAZIONE VARIABILE 2 PROGRAMMA
      parameter(nlns=1000*1000,nprofs=10000)
      parameter(km=46,kmt=72,km2=2*km,kms=10000)
      real,dimension(:), allocatable ::  deps, targ, sarg
      double precision :: presqmis, temqmis, salqmis
      integer platn, rr
      integer noqc, nosp, nofq, nohl, nolm
      integer nopr, noml, nodp, nolo, nogo
      integer nprof, oo, nods
      integer indx, ntobs, np
      character*1 CHAR1
      character*4 CHAR4
      character*10 CDATE
      character*5 CHOUR
      character*3 datatype, wmo
      character*2 cinm, cind, chrs, cdys, cdya
      character*4 ciny , cwin
      character*1 indxx
      character*43 strwr
      logical :: file_exists
      logical :: filep_exists

      call getarg(1,indir)
      call getarg(2,outdir)
      call getarg(3,infile)
      call getarg(4,date)

      if(iargc().ne.4)stop 'Stop wrong number of arguments'
      print*,trim(infile)
      wpc=infile(17:23)
      print*,wpc
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Open file with numbers of rejected data for every profile 
! Formatting of the file:
! nodp,nolo,nods,noqc,nolm,nohl,ndue,nprof,nvals
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      open(33,file=trim(outdir)//'/'//date//'.ARGO_PPREJC.dat', &
           form='formatted',position='append')
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Open file with list of rejected data for every profile
! Formatting of the file:
! date,lon,lat,pres,tem,sal,buoy,flag
! Flag list:
!  1   Bad quality flags on time and position
!  2   Profile out of the Med
!  3   Descending profile (only for Glider)
!  4   Quality flag of Pres, T or S not=1             
!  5   Value of T or S out of range (0<T<35 0<S<45)                               
!  6   Lack in the thermocline 
!  (pres(j+1)-pres(j)>40m in the first 300m)   
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      open(34,file=trim(outdir)//'/'//date//'.ARGO_LISTRJ.dat', &
           form='formatted',position='append')
! Numbers of data rejected by:
      ! (for one layer one of the qf is not 1)
      noqc = 0
      ! (Discending profile, for Argo =0)
      nods = 0  
      ! (hole in the thermocline)
      nohl = 0 
      ! (value not in 0<T<35, 0<S<45)
      nolm = 0 
      ! (bad qf for position or time)
      nodp = 0 
      ! (Out of the Med basin)
      nolo = 0 
      ! (data in the layer between 0 and 2 m)
      ndue = 0 
      ! (number of profiles rejected)
      nprof = 0 
      ! (number of good data)
      nvals = 0 
! open input nc file
!      ist = nf_open(trim(indir)//'/'//infile,nf_read, ncid)
      ist = nf_open(trim(indir)//'/'//infile,'0', ncid)
      call handle_err(ist)
! open error asci file
      open(99,file=trim(outdir)//'/error_ascii.txt', &
           form='formatted',position='append')
      write(99,'(a30)') '#########################################'
      write(99,'(a35)') infile

      ! get id variable
      
      !!!! PLATFORM NUMBER !!!!
!      ist = nf_get_att_text (ncid,n_global,"id",pln)
!      call handle_err(ist)
      
      !!!! TIME !!!!
      ist = nf_inq_varid (ncid,'TIME',idjul)
      call handle_err(ist)
!      print*,'TIME'
      !!!! TIME_QC !!!!
      ist = nf_inq_varid (ncid,'TIME_QC',idjul_qc)
      call handle_err(ist)
!      print*,'TIME_QC'
      !!!! LATITUDE !!!!
      ist = nf_inq_varid (ncid,'LATITUDE',idlat)
      call handle_err(ist)
!      print*,'LAT'
      !!!! LONGITUDE !!!!
      ist = nf_inq_varid (ncid,'LONGITUDE',idlon)
      call handle_err(ist)
!      print*,'LON'
      !!!! POSITION_QC !!!!
      ist = nf_inq_varid (ncid,'POSITION_QC',idpos)
      call handle_err(ist)
!      print*,'POS_QC'
      !!!! PRES !!!!
      ist = nf_inq_varid (ncid,'PRES',idpre)
      if (ist .NE. NF_NOERR) then
         PRINT *,"PRES doesn't exist"
         strwr=trim(infile)//' no PRES'
         write(34,11)strwr
         close(34)
         stop 
      endif
!      print*,'PRES'
      !!!! PRES_QC !!!!
      ist = nf_inq_varid (ncid,'PRES_QC',idpre_qc)
      call handle_err(ist)
      print*,'PRES_QC'
      !!!! TEMP !!!!
      ist = nf_inq_varid (ncid,'TEMP',idtem)
      if (ist .NE. NF_NOERR) then
         PRINT *,"TEMP doesn't exist"
         strwr=trim(infile)//' no TEMP'
         write(34,11)strwr
         close(34)
         stop
      endif 
      print*,'TEMP'
      !!!! TEMP_QC !!!!
      ist = nf_inq_varid (ncid,'TEMP_QC',idtem_qc)
      call handle_err(ist)
      print*,'TEMP_QC'
      !!!! PSAL !!!!
      ist = nf_inq_varid (ncid,'PSAL',idsal)
      if (ist .NE. NF_NOERR) then
         PRINT *,"PSAL doesn't exist"
         strwr=trim(infile)//' no PSAL'
         write(34,11)strwr
         close(34)
         stop
      endif 
      print*,'PSAL'
      !!!! PSAL_QC !!!!
      ist = nf_inq_varid (ncid,'PSAL_QC',idsal_qc)
      call handle_err(ist)
      print*,'PSAL_QC'
!get dimension and length of variable PRES

      ist = nf_inq_dimid(ncid,'TIME',dimidp)
      call handle_err(ist)
      ist = nf_inq_dimlen(ncid,dimidp,prof)
      call handle_err(ist)
      ist = nf_inq_dimid(ncid,'DEPTH',dimidl)
      call handle_err(ist)
      ist = nf_inq_dimlen(ncid,dimidl,lev)
      call handle_err(ist)

!get value of variable

      !!!! TIME !!!!
      allocate ( jul(prof) )
      ist = nf_get_var_double(ncid,idjul,jul)
      call handle_err(ist)
      
      julo=jul(1)
       
      call conv_jul_date(dd,mm,yyyy,hh,mn,julo)
      
      dateb=(yyyy*10000)+(mm*100)+dd
      
      !!!! DC_REFERENCE !!!!
      ist = nf_inq_varid (ncid,'DC_REFERENCE',iddcr)
      if (ist .NE. NF_NOERR) then
         PRINT *,"DC_REFERENCE doesn't exist"
         allocate(character(32) :: dcr(1))
         dcr='00000000                        '
      else
         allocate(character(32) :: dcr(prof))
         ist = nf_get_var_text(ncid,iddcr,dcr)
         call handle_err(ist)
      endif
      
      !!!! TIME_QC !!!!
      allocate ( jul_qc(prof) )
      ist = nf_get_var_double(ncid,idjul_qc,jul_qc)
      call handle_err(ist)

      !!!! LATITUDE !!!!
      allocate ( lat(prof) )
      ist = nf_get_var_double(ncid,idlat,lat)
      call handle_err(ist)

      !!!! LONGITUDE !!!!
      allocate ( lon(prof) )
      ist = nf_get_var_double(ncid,idlon,lon)
      call handle_err(ist)

      !!!! POSITION_QC !!!!
      allocate ( pos_qc(prof) )
      ist = nf_get_var_double(ncid,idpos,pos_qc)
      call handle_err(ist)

      !! INDEXES OF ARRAY
      start(1)=1
      start(2)=1
      count(1)=lev
      count(2)=1

      !!!! PRES !!!!
      allocate ( pres(lev) )
      ist = nf_get_vara_real(ncid,idpre,start,count,pres)
      call handle_err(ist)
      ist = nf_get_att_real(ncid,idpre,'_FillValue',presmis)
      call handle_err(ist)

      !!!! PRES_QC !!!!
      allocate ( pre_qc(lev) )
      ist = nf_get_vara_double(ncid,idpre_qc,start,count,pre_qc)
      call handle_err(ist)
      ist = nf_get_att_double(ncid,idpre_qc,'_FillValue',presqmis)
      call handle_err(ist)
      
      !!!! TEM !!!!
      allocate ( tem(lev) )
      ist = nf_get_vara_real(ncid,idtem,start,count,tem)
      call handle_err(ist)
      ist = nf_get_att_real(ncid,idtem,'_FillValue',temmis)
      call handle_err(ist)

      !!!! TEM_QC !!!!
      allocate ( tem_qc(lev) )
      ist = nf_get_vara_double(ncid,idtem_qc,start,count,tem_qc)
      call handle_err(ist)
      ist = nf_get_att_double(ncid,idtem_qc,'_FillValue',temqmis)
      call handle_err(ist)

      !!!! PSAL !!!!
      allocate ( sal(lev) )
      ist = nf_get_vara_real(ncid,idsal,start,count,sal)
      call handle_err(ist)
      ist = nf_get_att_real(ncid,idsal,'_FillValue',salmis)
      call handle_err(ist)

      !!!! PSAL_QC !!!!
      allocate ( sal_qc(lev) )
      ist = nf_get_vara_double(ncid,idsal_qc,start,count,sal_qc)
      call handle_err(ist)
      ist = nf_get_att_double(ncid,idsal_qc,'_FillValue',salqmis)
      call handle_err(ist)

          !!!!!!!!! Code Meaning !!!!!!!!!
          !!                            !!
          !! 0 No QC was performed      !!
          !! 1 Good data                !!
          !! 2 Probably good data       !!
          !! 3 Bad data that are        !!
          !!   potentially correctable  !!
          !! 4 Bad data                 !!
          !! 5 Value changed            !!
          !! 6 Not used                 !!
          !! 7 Not used                 !!
          !! 8 Interpolated value       !!
          !! 9 Missing value            !!
          !!                            !!
          !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

      print*,"Variables read"

!!!! CHECK of QUALITY CONTROL on JULD and POSITION
!      read(pln(17:23),'(i8)') platn
      np=1
         if ((jul_qc(np) .eq. 1 ) .and. ( pos_qc(np) .eq. 1 )) then

!!!! CONVERSION PRESSION TO DEPTH

            allocate( dpt(lev) )
            do n = 1, lev
               dpt(n) = depth(pres(n),lat(np))
            enddo
!!!! CONTROL ON POSITION 
            if ((lon(np).ge.-6).and.(lon(np).le.36.25).and. &
               (lat(np).ge.30.1875).and.(lat(np).le.45.9375)) then
               j = 0
!!!! CHECK of QUALITY CONTROL for P, T and S

               do n = 1, lev
                  if (( pre_qc(n) .eq. 1 ) .and. (tem_qc(n) .eq. 1 ) .and. ( sal_qc(n) .eq. 1 )) then
                     if((tem(n).le.35. .and. tem(n).ge.0.0) .and. &
                        (sal(n).le.45. .and. sal(n).ge.0.0)) then
                        j = j + 1
                        DAT(j,1) = dpt(n)
                        DAT(j,2) = tem(n)
                        DAT(j,3) = sal(n)
                     else
                        print*,'Profile rejected'
!                        nolm=lev
                        nprof=1
                        do oo=1,lev
                           if ( pres(oo) .eq. presmis ) then 
                                 pres(oo) = -999.
                           endif
                           if ( tem(oo) .eq. temmis ) then 
                                tem(oo) = -999.
                           endif
                           if ( sal(oo) .eq. salmis ) then 
                                 sal(oo) = -999.
                           endif
                           if (( pre_qc(oo) .ne. presqmis ) .and. &
                               ( tem_qc(oo) .ne. temqmis ) .and. &
                               ( sal_qc(oo) .ne. salqmis )) then
                               nolm=nolm+1
                           write(34,10)dateb,',',lon(np),',',lat(np),',', &
                             pres(oo),',',tem(oo),',', &
                             sal(oo),',',wpc,',',5
                           endif
                        enddo
!                        stop
                        go to 1220
                     end if 
                  else
                     write(99,1) n
!                     noqc=noqc+1
                     if ( pres(n) .eq. presmis ) then 
                         pres(n) = -999.
                     endif
                     if ( tem(n) .eq. temmis ) then
                         tem(n) = -999.
                     endif
                     if ( sal(n) .eq. salmis ) then
                         sal(n) = -999.
                     endif
                     if (( pre_qc(n) .ne. presqmis ) .and. &
                         ( tem_qc(n) .ne. temqmis ) .and. &
                         ( sal_qc(n) .ne. salqmis )) then
                         noqc=noqc+1
                     write(34,10)dateb,',',lon(np),',',lat(np),',', &
                          pres(n),',',tem(n),',',sal(n),',',wpc,',',4
                     endif
                  end if
               enddo
!               print*,DAT(:,2)
               if (( j .eq. 0 )) then
                  write(99,'(a20)') 'no good data in the profile'
                  nprof=1
                  go to 1220
               else if ( j .eq. 1 ) then
                  write(99,'(a24)') 'there is only one datum '
                  nprof=1
                  go to 1220
               else
                  M=j
                  
                  allocate( X(M,3) )

                  do n = 1, M
                     X(n,1) = DAT(n,1)
                     X(n,2) = DAT(n,2)
                     X(n,3) = DAT(n,3)
                  enddo
! Check if there is a lack of 40 m in the first 300 m of the profile
                  P=0
                  if ( M .ne. 0 .and. M .ne. 1 ) then
                     do i=1, M
                        if (X(i,1).le.300 ) then
                           P=P+1
                        end if
                     enddo
                  end if

                  allocate ( PRO(P,3) )

                  p=0
                  if ( M .ne. 0 .and. M .ne. 1 ) then
                     do i=1, M
                        if ( X(i,1).le.300 ) then
                           p=p+1
                           PRO(p,:)=X(i,:)
                        end if
                     enddo
                  end if

                  Q=0
                  if ( M .ne. 0 .and. M .ne. 1 ) then
                     do i=1, P-1
                        if ( PRO(i+1,1)-PRO(i,1) .ge. 40 ) then
                           Q=Q+1
                        end if
                     enddo
                  end if

                  allocate( PROH(Q,3) )

                  q=0
                  if ( M .ne. 0 .and. M .ne. 1 ) then
                     do i=1, P-1
                        if ( PRO(i+1,1)-PRO(i,1) .ge. 40 ) then
                           holes=1
                           q=q+1
                           PROH(q,:)=X(i,:)
                        end if
                     enddo
                  end if

                  if ((holes .eq. 1).or.(X(1,1).gt.35.)) then

                     write(99,'(a28)') 'data lack in the thermocline'
!                     nohl=lev
                     nprof=1
                     do oo=1,lev
                        if ( pres(oo) .eq. presmis ) then 
                            pres(oo) = -999.
                        endif
                        if ( tem(oo) .eq. temmis ) then
                            tem(oo) = -999.
                        endif
                        if ( sal(oo) .eq. salmis ) then
                            sal(oo) = -999.
                        endif
                        if (( pre_qc(oo) .ne. presqmis ) .and. &
                            ( tem_qc(oo) .ne. temqmis ) .and. &
                            ( sal_qc(oo) .ne. salqmis )) then
                            nohl=nohl+1
                        write(34,10)dateb,',',lon(np),',',lat(np),',', &
                          pres(oo),',',tem(oo),',', &
                          sal(oo),',',wpc,',',6
                        endif
                     enddo
!                     stop
                     go to 1220
                  else
                     kmss=M
                  end if !(continuare da prima di questo endif)
               end if  !(End check on thermocline)
            else
               write(99,'(a11)') 'No good LON' 
!               nolo=lev
               nprof=1
               do oo=1,lev
                  if ( pres(oo) .eq. presmis ) then 
                      pres(oo) = -999.
                  endif
                  if ( tem(oo) .eq. temmis ) then 
                      tem(oo) = -999.
                  endif
                  if ( sal(oo) .eq. salmis ) then
                      sal(oo) = -999.
                  endif
                  if (( pre_qc(oo) .ne. presqmis ) .and. &
                      ( tem_qc(oo) .ne. temqmis ) .and. &
                      ( sal_qc(oo) .ne. salqmis )) then
                  nolo=nolo+1
                  write(34,10)dateb,',',lon(np),',',lat(np),',', &
                     pres(oo),',',tem(oo),',',sal(oo), &
                     ',',wpc,',',2
                  endif
               enddo
!               stop
               go to 1220
            end if !(End check on LON )
         else
            write(99,'(a25)') 'No QC on date or position'
!            nodp=lev
            nprof=1
            do oo=1,lev
               if ( pres(oo) .eq. presmis ) then 
                   pres(oo) = -999.
               endif
               if ( tem(oo) .eq. temmis ) then
                   tem(oo) = -999.
               endif
               if ( sal(oo) .eq. salmis ) then
                   sal(oo) = -999.
               endif
               if (( pre_qc(oo) .ne. presqmis ) .and. &
                   ( tem_qc(oo) .ne. temqmis ) .and. &
                   ( sal_qc(oo) .ne. salqmis )) then
                   nodp=nodp+1
               write(34,10)dateb,',',lon(np),',',lat(np),',', &
                 pres(oo),',',tem(oo),',',sal(oo), &
                 ',',wpc,',',1
               endif
            enddo
!            stop
            go to 1220
         end if !(End check sul JUL e POS QC)
      print*,"QC done"
      if (kmss .gt. 1)then

      allocate ( temo_qc(kmss), psalo_qc(kmss) )
      allocate ( depo_qc(kmss) )
     
      temo_qc=1
      psalo_qc=1
      depo_qc=1
      do i=1,kmss
         if (X(i,1).lt.2.) then
            ndue=ndue+1
            nvals=nvals+0
            temo_qc(i)=4
            psalo_qc(i)=4
            depo_qc(i)=4
!            X(i,1)=9.96921e+36
!            X(i,2)=9.96921e+36
!            X(i,3)=9.96921e+36
         else
            nvals=nvals+1
         endif
      enddo

!------- WRITE OUTPUT FILE
      print*,"Create NetCDF file"
      ist = nf_create(trim(outdir)//'/'//infile, nf_NoClobber, ncio)
      call handle_err(ist)
      !!------- ADD DIMENSIONS -------
      ist=nf_def_dim(ncio, 'DEPTH', kmss , depoid)
      call handle_err(ist)
      ist=nf_def_dim(ncio, 'POSITION', 1 , posoid)
      call handle_err(ist)
      ist=nf_def_dim(ncio, 'LONGITUDE', 1 , lonoid)
      call handle_err(ist)
      ist=nf_def_dim(ncio, 'LATITUDE', 1 , latoid)
      call handle_err(ist)
      ist=nf_def_dim(ncio, 'TIME', 1, timoid)
      call handle_err(ist)
      ist=nf_def_dim(ncio, 'STRING32', 32, stroid)
      call handle_err(ist)
!      ist=nf_def_dim(ncio, 'STRING2', 3, strboid)
!      call handle_err(ist)
      print*,"Dimensions added"
     
      dimen(2)=timoid
      dimen(1)=depoid 
      
      diment(1)=timoid
      dimenla(1)=latoid
      dimenlo(1)=lonoid
      dimenp(1)=posoid
      dimenst(1)=stroid
!      dimenstb(1)=strboid

      !!------- ADD VARIABLE ---------
!      ist=nf_copy_att(ncid, idtem, 'units', ncio, toid)
!      call handle_err(ist)
      
      ist=nf_def_var(ncio, 'TIME', nf_double, 1,diment, tmoid)
      call handle_err(ist)
      ist=nf_def_var(ncio, 'TIME_QC', nf_byte, 1,diment, tmqoid)
      call handle_err(ist)
      ist=nf_def_var(ncio, 'LONGITUDE', nf_float, 1,dimenlo, lonvoid)
      call handle_err(ist)
      ist=nf_def_var(ncio, 'LATITUDE', nf_float, 1,dimenla, latvoid)
      call handle_err(ist)
      ist=nf_def_var(ncio, 'POSITION_QC', nf_byte, 1,dimenp, posqoid)
      call handle_err(ist)
      ist=nf_def_var(ncio, 'DEPH', nf_float, 2,dimen, poid)
      call handle_err(ist)
!      ist=nf_copy_att(ncid, idpre, '_FillValue', ncio, poid)
!      call handle_err(ist)
      ist=nf_put_att_real(ncio, poid, '_FillValue', nf_float, &
          1, 9.96921e+36 )
      ist=nf_def_var(ncio, 'DEPH_QC', nf_byte, 2,dimen, pqoid)
      call handle_err(ist)
      ist=nf_def_var(ncio, 'PSAL', nf_float, 2,dimen, soid) 
      call handle_err(ist)
!      ist=nf_copy_att(ncid, idsal, '_FillValue', ncio, soid)
!      call handle_err(ist)
      ist=nf_put_att_real(ncio, soid, '_FillValue', nf_float, &
          1, 9.96921e+36 )
      ist=nf_def_var(ncio, 'PSAL_QC', nf_byte, 2,dimen, sqoid) 
      call handle_err(ist)
      ist=nf_def_var(ncio, 'TEMP', nf_float, 2,dimen, toid) 
      call handle_err(ist)
      ist=nf_put_att_real(ncio, toid, '_FillValue', nf_float, &
          1, 9.96921e+36 )
!      ist=nf_copy_att(ncid, idtem, '_FillValue', ncio, toid)
!      call handle_err(ist)
      ist=nf_def_var(ncio, 'TEMP_QC', nf_byte, 2,dimen, tqoid) 
      call handle_err(ist)
      !!!! WMO_INST_TYPE !!!!
!      ist = nf_get_att_text (ncid,n_global,"wmo_inst_type",wmo)
!      if (ist .NE. NF_NOERR) then
!         PRINT *,"wmo_inst_type doesn't exist"
         wmo='850'
         ist = nf_put_att_text (ncio,nf_global,'wmo_inst_type',3,wmo)
         call handle_err(ist)
!      else
!         ist=nf_copy_att(ncid, nf_global, 'wmo_inst_type', ncio, nf_global)
!         call handle_err(ist)
!      endif 
!      ist=nf_copy_att(ncid, nf_global, 'wmo_platform_code', ncio, nf_global)
!      ist = nf_get_att_text (ncid,n_global,"wmo_platform_code",wpc)
!      if (ist .NE. NF_NOERR) then
!         print*,"wmo_platform_code doesn't exist"
!         wpc='0000000'
         ist = nf_put_att_text (ncio,nf_global,'wmo_platform_code',7,wpc)
!      else
!         ist=nf_copy_att(ncid, nf_global, 'wmo_platform_code', ncio, nf_global)
         call handle_err(ist)
!      endif
!      call handle_err(ist)
      ist=nf_def_var(ncio, 'DC_REFERENCE', nf_char, 1,dimenst, pnoid) 
      call handle_err(ist)
!      ist=nf_def_var(ncio, 'WMO_INST_TYPE', nf_char, 1,dimenstb, wmooid) 
!      call handle_err(ist)
 
      ist = nf_enddef(ncio)
      call handle_err(ist)
      print*,"Variables declared"

      ist=nf_put_var_double(ncio, tmoid, jul(1))
      call handle_err(ist)
      ist=nf_put_var_double(ncio, tmqoid, jul_qc(1)) 
      call handle_err(ist)
      ist=nf_put_var_double(ncio, lonvoid, lon(1))
      call handle_err(ist)
      ist=nf_put_var_double(ncio, latvoid, lat(1))
      call handle_err(ist)
      ist=nf_put_var_double(ncio, posqoid, pos_qc(1))
      call handle_err(ist)
      ist=nf_put_var_real(ncio, poid, X(:,1))
      call handle_err(ist)
      ist=nf_put_var_int(ncio, pqoid, depo_qc)
      call handle_err(ist)
      ist=nf_put_var_real(ncio, toid, X(:,2))
      call handle_err(ist)
      ist=nf_put_var_int(ncio, tqoid, temo_qc)
      call handle_err(ist)
      ist=nf_put_var_real(ncio, soid, X(:,3))
      call handle_err(ist)
      ist=nf_put_var_int(ncio, sqoid, psalo_qc)
      call handle_err(ist)
      ist=nf_put_var_text(ncio, pnoid, dcr(1))
      call handle_err(ist)
!      ist=nf_put_var_text(ncio, wmooid, wmo)
!      call handle_err(ist)
      ist = nf_close (ncio)
      ist = nf_close (ncid)
      
      print*,"NetCDF file written" 
      deallocate (temo_qc, psalo_qc, depo_qc)

      endif 
1220      write(33,20)  &
             nodp*2,',',nolo*2,',',nods*2,',', &
             noqc*2,',',nolm*2,',',nohl*2,',', &
             ndue*2,',',nprof,',',nvals*2
      close(33)
      close(34)
      close(12)
      close(10)
      close(99)
1 format('bad P, T or S quality flag at level' i3)
2 format(a10,1x,a5,1x,f8.4,1x,f8.4,1x,a7,1x,i3)
3 format(f6.2,1x,f12.8,1x,f12.8)
4 format('Stability check: tollerance ',f14.7)
5 format('density instability at level ' i3)
6 format(f7.2,1x,f12.8,1x,f12.8)
7 format('quality control done on file ',a73)
8 format('error at depth ',f7.2)
9 format(i8)
!10 format(i8,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,i8,a1,i1)
10 format(i8,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,a7,a1,i1)
11 format(a43)
20 format(i6,a1,i6,a1,i6,a1,i6,a1,i6,a1,i6,a1, &
      i6,a1,i6,a1,i6)
      stop
      end
!*************************************************
      SUBROUTINE HANDLE_ERR(stat)
      include './netcdf.inc'
      INTEGER stat
      IF (stat .NE. NF_NOERR) THEN
         PRINT *, NF_STRERROR(stat)
         STOP 'Stopped'
      ENDIF
      END SUBROUTINE HANDLE_ERR
!*************************************************
!----------------------------------------------------------------------
      subroutine conv_date_jul(iiday,iimon,iiyear,iijul)

      dimension idmn(12)
      data idmn/ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31/

      njear = iiyear-1990

      iijul = 0

      if(iiyear.gt.1990)then
         do k=1998,iiyear-1
            iijul = iijul + 365
            if(mod(k,4).eq.0)  iijul = iijul + 1
         enddo
       endif

       if(iimon.gt.1)then
          do k=1,iimon-1
             iijul = iijul + idmn(k)
             if(k.eq.2 .and. mod(iiyear,4).eq.0)  iijul = iijul + 1
          enddo
       endif

       iijul = iijul + iiday
       
       return
       end
!----------------------------------------------------------------------
       subroutine conv_jul_date(iiday,iimon,iiyear,hour,minutes,iijul)

       dimension idmn(12)
       data idmn/ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31/
       double precision  iijul,iijuld
       real  restday, resthour
       integer hour, minutes

       iiyear = 1950
       if(iijul.gt.365)then
          do while(iijul.gt.365.or.iijul.eq.365)
             iijul=iijul-365
             if(mod(iiyear,4).eq.0) iijul=iijul-1
             iiyear=iiyear+1
         enddo
      endif


      if(iijul.lt.0) then
         iiyear=iiyear-1
         iijul=iijul+366
      endif
         iijuld = iijul
         iijul=ceiling(iijul)
         iimon = 1
      if((iijul).gt.idmn(iimon))then
         mond = idmn(iimon)
         do while((iijul).gt.mond)
            iijul = iijul - mond
            iijuld = iijuld - mond
            iimon=iimon+1
            mond = idmn(iimon)
            if(iimon.eq.2 .and. mod(iiyear,4).eq.0) mond = 29
         enddo
      endif

      iiday = int(iijul)
      restday = iijuld-int(iijuld)
      hour = int(restday * 24)
      resthour = (restday * 24) - hour
      minutes = int(resthour * 60)


!!      return

      end
!----------------------------------------------------------------------
      real function depth(p,l)
       !! This is to calculate depth in metres from pressure in dbars.
       !! The input data are
       !!       p = Pressure [db]
       !!       l = Latitude in decimal degrees north [-90..+90]
       !! The output is
       !!       depth = depth [metres]

       !! REFERENCES :
       !! Unesco 1983. Algorithms for computation of fundamental properties of
       !! seawater, 1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.

       real :: pi
       real :: DEG2RAD
       real,parameter:: c1 = +9.72659
       real,parameter:: c2 = -2.2512E-5
       real,parameter:: c3 = +2.279E-10
       real,parameter:: c4 = -1.82E-15
       real,parameter:: gam_dash = 2.184e-6
       real:: X, bot_line, top_line
       real:: p
       double precision:: l, LAT
       pi =  3.1416
       DEG2RAD = pi/180
       LAT = abs(l)
       X = sin(LAT*DEG2RAD) !! convert to radians
       X = X*X
       bot_line = 9.780318*(1.0+(5.2788E-3+2.36E-5*X)*X) + gam_dash*0.5*p
       top_line = (((c4*p+c3)*p+c2)*p+c1)*p
       depth = top_line/bot_line

      return
      end function depth

      real function pressure(d,l)
      !! This is to calculate pressure in dbars in metres.
      !! The input data are
      !!       d = depth [metres]
      !!       l = Latitude in decimal degrees north [-90..+90]
      !! The output is
      !!       pressure = Pressure [db]

      !! REFERENCES :
      !! Saunders, P.M. 1981
      !! "Practical conversion of Pressure to Depth"
      !! Journal of Physical Oceanography, 11, 573-574

      real :: pi
      real :: DEG2RAD
      real :: X,C1
      double precision::l
!!       real :: pressure


      pi =  3.1416
      DEG2RAD = pi/180
      X       = sin(abs(l)*DEG2RAD)  ! convert to radians
      C1      = 5.92E-3+(X**2)*5.25E-3
      pressure = ((1-C1)-sqrt(((1-C1)**2)-(8.84E-6*d)))/4.42E-6

      return
      end function pressure
