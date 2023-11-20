      include './netcdf.inc'

!INPUT:
! 1-file name 2-Date

      character*256 :: indir, outdir, infile, listfile, errfile
      character*28 :: oufile
      integer ::  ist, ncid,  prof, lev, N, cln, start(2), count(2)
      integer :: yyyy, mm, dd, longitude, latitude, posit, sist, wist
      double precision,dimension(:), allocatable :: jul, lat, lon
      double precision,dimension(:), allocatable :: jul_qc,pos_qc
      double precision,dimension(:), allocatable :: julo
      integer :: depoid, posoid, lonoid, latoid, timoid, toid, iddcr
      integer :: tmoid, tmqoid, lonvoid, latvoid, posqoid, wmooid
      integer :: poid, pqoid, soid, sqoid, tqoid, pnoid, stroid,strboid
      integer ,dimension(:), allocatable :: dateb
      character,dimension(:), allocatable :: dir
      integer,dimension(:,:), allocatable:: temf_qc, dptf_qc, salf_qc
      real,dimension(:,:), allocatable:: temf, dptf, salf
      integer :: dimen(2), diment(1), dimenst(2), dimenstb(1)
      integer :: dimenla(1), dimenlo(1), dimenp(1)
      real :: presmis, temmis, salmis
      double precision :: presqmis, temqmis, salqmis
      integer :: rejobsqo, rejobsso, rejobsto, rejobsbo
      integer :: rejobsho, rejobsmo, rejobspo, rejobsao
      integer :: rejproho, rejpromo, rejpropo, rejproqo
      integer :: rejproao
      integer :: rejobsq, rejobss, rejobst, rejobsb
      integer :: rejobsh, rejobsm, rejobsp, ntobs, rejobsa
      integer :: rejproh, rejprom, rejprop, rejproq, rejproa
      integer noqc, nosp, nofq, nohl, nolm
      integer nopr, noml, nodp, nolo
      integer nprof, nods, oo, nobs, ndue
      character*5 ::  pln
      character(len=32),allocatable :: dcr(:)
      integer::  iihour, iimin, A, B, M, P, Q, ag, rrr
      double precision,dimension(:,:), allocatable:: tem_qc, sal_qc
      double precision,dimension(:,:), allocatable:: pre_qc
      real,dimension(:,:), allocatable :: pres, tem, sal
      real,dimension(:,:), allocatable :: dpt
      real,dimension(:), allocatable :: bfrq, xx, r, errs, errt, se
      real,dimension(:,:), allocatable :: X, PRO, PROH
      real :: DATA(2500,3), DAT(2500,3),  limit, mean
      character*2 :: cmon, cday,chr,cmin
      character*4 cyear
      character*8 date
      character*7 wpc
      character(len=10)::odate
      character(len=5)::  otime
      parameter(nlns=1000*1000,nprofs=10000)
      parameter(km=46,kmt=72,km2=2*km,kms=10000)
      real,dimension(:), allocatable ::  deps, targ, sarg
! real,dimension(:) ::  deps, targ, sarg
      dimension lnprf(nprofs),lnpre(nprofs)
      integer inoa(nlns), para(nlns)
      integer platn, rr
      integer indx, counts
      real lona(nlns), lata(nlns), dpta(nlns), tima(nlns), vala(nlns)
      real erra(nlns)
      character*1 CHAR1
      character*4 CHAR4
      character*10 CDATE
      character*5 CHOUR
      character*3 datatype
      character*2 cinm, cind, chrs, cdys, cdya
      character*4 ciny , cwin
      character*1 indxx
      character*90 strwr
      character*90 plnall
      character*1 plnallu
      character*2 plnalld
      integer kline, inoaii, parai
      real lonai,latai, dptai,timai,valai,errai, tsp, tspa, tspb
      logical :: file_exists
      logical :: filep_exists
      logical :: fileo_exists
      real pot_tem
      call getarg(1,indir)
      call getarg(2,outdir)
      call getarg(3,infile)
      call getarg(4,date)
      call getarg(5,plnall)
      
      plnallu=' '
      plnalld='  '
 
      if(iargc().ne.5)stop 'Stop wrong number of arguments'
      print*,trim(infile)

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Open file with numbers of rejected data for every profile 
! Formatting of the file:
! nodp,nolo,nods,noqc,nolm,nohl,ndue,nprof,nvals
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      open(33,file=trim(outdir)//'/'//date//'.GLIDER_PPREJC.dat', &
           form='formatted',position='append')
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Open file with list of rejected data for every profile
! Formatting of the file:
! date,lon,lat,pres,tem,sal,buoy,flag
! Flag list:
!  1   Bad quality flags on time and position
!  2   Profile out of the Med
!  3   Descending profile (only for Glider)
!  4   Quality flag of Pres, T or S not=1             
!  5   Value of T or S out of range (0<T<35 0<S<45)                               
!  6   Lack in the thermocline (pres(j+1)-pres(j)>40m in the first 300m)   
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      open(34,file=trim(outdir)//'/'//date//'.GLIDER_LISTRJ.dat', &
           form='formatted',position='append')

      nvals = 0 ! (number of good data)
      noqc = 0 ! (for one layer one of the qf is not 1)
      nohl = 0 ! (hole in the thermocline)
      nolm = 0 ! (value not in 0<T<35, 0<S<45)
      nodp = 0 ! (bad qf for position or time)
      nolo = 0 ! (Out of the Med basin)
      nods = 0 ! (Discending profile, for Argo =0)
      nprof = 0 ! (number of profiles rejected)
!      nobs = 0 ! (number of good data)
      ndue = 0 ! (data in the layer between 0 and 2 m)

! open input nc file
      ist = nf_open(trim(indir)//'/'//infile,'0', ncid)
      call handle_err(ist)
! open error asci file
      open(99,file=trim(outdir)//'/error_ascii.txt', &
           form='formatted',position='append')
      write(99,'(a30)') '#########################################'
      write(99,'(a35)') infile
      
      ! get id variable
      
      !!!! PLATFORM NUMBER !!!!
!      ist = nf_get_att_text (ncid,n_global,"wmo_platform_code",pln)
!      call handle_err(ist)
      pln=infile(17:21)
      if ( pln .eq. 'EGO-P' ) then
          plnall='68450'
      end if 
      print*,trim(plnall)
!      read(pln,'(i5)') platn      
      !!!! TIME !!!!
      ist = nf_inq_varid (ncid,'TIME',idjul)
      call handle_err(ist)
     
      !!!! TIME_QC !!!!
      ist = nf_inq_varid (ncid,'TIME_QC',idjul_qc)
      call handle_err(ist)
    
      !!!! LATITUDE !!!!
      ist = nf_inq_varid (ncid,'LATITUDE',idlat)
      call handle_err(ist)
   
      !!!! LONGITUDE !!!!
      ist = nf_inq_varid (ncid,'LONGITUDE',idlon)
      call handle_err(ist)
  
      !!!! DIRECTION !!!!
      ist = nf_inq_varid (ncid,'DIRECTION',iddir)
      call handle_err(ist)

      !!!! POSITION_QC !!!!
      ist = nf_inq_varid (ncid,'POSITION_QC',idpos)
      call handle_err(ist)
 
      !!!! PRES !!!!
      ist = nf_inq_varid (ncid,'PRES',idpre)
      if (ist .NE. NF_NOERR) then
         PRINT *,"PRES doesn't exist"
         strwr=trim(infile)//' no PRES'
         write(34,21)strwr
         close(34)
         stop
      endif

      !!!! PRES_QC !!!!
      ist = nf_inq_varid (ncid,'PRES_QC',idpre_qc)
      call handle_err(ist)

      !!!! TEMP !!!!
      ist = nf_inq_varid (ncid,'TEMP',idtem)
      if (ist .NE. NF_NOERR) then
         PRINT *,"TEMP doesn't exist"
         strwr=trim(infile)//' no TEMP'
         write(34,21)strwr
         close(34)
         stop
      endif      

      !!!! TEMP_QC !!!!
      ist = nf_inq_varid (ncid,'TEMP_QC',idtem_qc)
      call handle_err(ist)

      !!!! PSAL !!!!
      ist = nf_inq_varid (ncid,'PSAL',idsal)
      if (ist .NE. NF_NOERR) then
         PRINT *,"PSAL doesn't exist"
         strwr=trim(infile)//' no PSAL'
         write(34,21)strwr
         close(34)
         stop
      endif

      !!!! PSAL_QC !!!!
      ist = nf_inq_varid (ncid,'PSAL_QC',idsal_qc)
      call handle_err(ist)

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
      allocate ( julo(prof) )
      allocate ( dateb(prof) )
      ist = nf_get_var_double(ncid,idjul,jul)
      call handle_err(ist)

      do s=1,prof
         julo(s)=jul(s)
      enddo

      allocate ( temf(lev,prof) )
      allocate ( dptf(lev,prof) )
      allocate ( salf(lev,prof) )
      allocate ( temf_qc(lev,prof) )
      allocate ( dptf_qc(lev,prof) )
      allocate ( salf_qc(lev,prof) )
      temf=9.96921e+36
      salf=9.96921e+36
      dptf=9.96921e+36
      temf_qc=4
      salf_qc=4
      dptf_qc=4

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

      !!!! DIRECTION !!!!
      allocate ( dir(prof) )
      ist = nf_get_var_text(ncid,iddir,dir)
      call handle_err(ist)

      !!!! POSITION_QC !!!!
      allocate ( pos_qc(prof) )
      ist = nf_get_var_double(ncid,idpos,pos_qc)
      call handle_err(ist)
      
      !!!! DC_REFERENCE !!!!
      ist = nf_inq_varid (ncid,'DC_REFERENCE',iddcr)
      if (ist .NE. NF_NOERR) then
         PRINT *,"DC_REFERENCE doesn't exist"
         allocate(character(32) :: dcr(prof))
         do h=1,prof
            dcr(h)='00000000                        '
         enddo
      else
         allocate(character(32) :: dcr(prof))
         ist = nf_get_var_text(ncid,iddcr,dcr)
         call handle_err(ist)
      endif

      !! INDEXES OF ARRAY
      start(1)=1
      start(2)=1
      count(1)=lev
      count(2)=prof

      !!!! PRES !!!!
      allocate ( pres(lev,prof) )
      ist = nf_get_vara_real(ncid,idpre,start,count,pres)
      call handle_err(ist)
      ist = nf_get_att_real(ncid,idpre,'_FillValue',presmis)
      call handle_err(ist)
    
      !!!! PRES_QC !!!!
      allocate ( pre_qc(lev,prof) )
      ist = nf_get_vara_double(ncid,idpre_qc,start,count,pre_qc)
      call handle_err(ist)
      ist = nf_get_att_double(ncid,idpre_qc,'_FillValue',presqmis)
      call handle_err(ist)

      !!!! TEM !!!!
      allocate ( tem(lev,prof) )
      ist = nf_get_vara_real(ncid,idtem,start,count,tem)
      call handle_err(ist)
      ist = nf_get_att_real(ncid,idtem,'_FillValue',temmis)
      call handle_err(ist)
 
      !!!! TEM_QC !!!!
      allocate ( tem_qc(lev,prof) )
      ist = nf_get_vara_double(ncid,idtem_qc,start,count,tem_qc)
      call handle_err(ist)
      ist = nf_get_att_double(ncid,idtem_qc,'_FillValue',temqmis)
      call handle_err(ist)

      !!!! PSAL !!!!
      Allocate ( sal(lev,prof) )
      ist = nf_get_vara_real(ncid,idsal,start,count,sal)
      call handle_err(ist)
      ist = nf_get_att_real(ncid,idsal,'_FillValue',salmis)
      call handle_err(ist)

      !!!! PSAL_QC !!!!
      allocate ( sal_qc(lev,prof) )
      ist = nf_get_vara_double(ncid,idsal_qc,start,count,sal_qc)
      call handle_err(ist)
      ist = nf_get_att_double(ncid,idsal_qc,'_FillValue',salqmis)
      call handle_err(ist)

! Quality flags of the profile
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

!!!! CONVERSION PRES TO DEPTH
     
      allocate( dpt(lev,prof) )
      do np=1,prof
         do n = 1, lev
            if ( pres(n,np) .ge. 0 ) then
               dpt(n,np) = depth(pres(n,np),lat(np))
            endif
         enddo
      enddo

      do np=1,prof
!!!! CHECK of QUALITY CONTROL on JULD and POSITION
         if ((jul_qc(np) .eq. 1 ) .and. ( pos_qc(np) .eq. 1 )) then
            call conv_jul_date(dd,mm,yyyy,hh,mn,julo(np))
            dateb(np)=(yyyy*10000)+(mm*100)+dd
!!!! CHECK if the profile is in the Med.
            print*,dir(np)
            if ((lon(np).ge.-6).and.(lon(np).le.36.25).and. &
               (lat(np).ge.30.1875).and.(lat(np).le.45.9375)) then
!!!! CHECK of direction of profile
               if ( dir(np) .eq. "A" ) then
                  j = 0
!!!! CHECK of QUALITY CONTROL for P, T and S
              do n = 1, lev
!                 if (( pre_qc(n,np) .ne. presqmis ) .and. &
!                       ( tem_qc(n,np) .ne. temqmis ) .and. &
!                       ( sal_qc(n,np) .ne. salqmis )) then
!                    nobs=nobs+1
!                 endif
              if (( pre_qc(n,np) .eq. 1. ) .and. (tem_qc(n,np) .eq. 1. ) &
                 .and. ( sal_qc(n,np) .eq. 1. )) then
!!!! Check on the values of the TEMP and PSAL (0<T<35 0<S<45)
                 if((tem(n,np).le.35. .and. tem(n,np).ge.0.0) .and. &
                    (sal(n,np).le.45. .and. sal(n,np).ge.0.0)) then
                    j = j + 1
                    DAT(j,1) = dpt(n,np)
                    DAT(j,2) = tem(n,np)
                    DAT(j,3) = sal(n,np)
                 else
                    print*,'Profile rejected'
                    nprof=nprof+1
                    if ( pres(n,np) .eq. presmis ) then
                         pres(n,np) = -999.
                    endif
                    if ( tem(n,np) .eq. temmis ) then
                         tem(n,np) = -999.
                    endif
                    if ( sal(n,np) .eq. salmis ) then
                         sal(n,np) = -999.
                    endif
                    do oo=1,lev
                    if (( pre_qc(oo,np) .ne. presqmis ) .and. &
                       ( tem_qc(oo,np) .ne. temqmis ) .and. &
                       ( sal_qc(oo,np) .ne. salqmis )) then
                       nolm=nolm+1
                       write(34,11)dateb,',',lon(np),',',lat(np), &
                        ',',pres(oo,np),',',tem(oo,np),',', &
                        sal(oo,np),',',trim(plnall),',',5
                    endif
                    enddo
!                    stop
                 end if
              else
                 write(99,1) n
                 if ( pres(n,np) .eq. presmis ) then
                     pres(n,np) = -999.
                 endif
                 if ( tem(n,np) .eq. temmis ) then
                      tem(n,np) = -999.
                 endif
                 if ( sal(n,np) .eq. salmis ) then
                      sal(n,np) = -999.
                 endif
                 if (( pre_qc(n,np) .ne. presqmis ) .and. &
                       ( tem_qc(n,np) .ne. temqmis ) .and. &
                       ( sal_qc(n,np) .ne. salqmis )) then
                 noqc=noqc+1
                 write(34,11)dateb(np),',',lon(np),',',lat(np),',', &
                   pres(n,np),',',tem(n,np),',',sal(n,np),',', &
                   trim(plnall),',',4
                 endif
               end if
               enddo
               if (( j .eq. 0 )) then !(A)
                  write(99,'(a20)') 'no good data in the profile'
                  nprof=nprof+1
               else if ( j .eq. 1 ) then
                  write(99,'(a24)') 'there is only one datum '
                  nprof=nprof+1
               else
                  M=j

                  allocate( X(M,3) )

                  do n = 1, M
                     X(n,1) = DAT(n,1)
                     X(n,2) = DAT(n,2)
                     X(n,3) = DAT(n,3)
                  enddo
!!!! Check of distance between two subsequent measurements of T and S
!!!! (< 40 in the first 300 m)
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
                  holes=0 
!                  print*,holes 
                  q=0
                  if ( M .ne. 0 .and. M .ne. 1 ) then
                     do i=1, P-1
                        if ( PRO(i+1,1)-PRO(i,1) .ge. 40 ) then
                           holes=1
!                          if (holes .gt. 0) exit
                           q=q+1
                           PROH(q,:)=X(i,:)
                        end if
                     enddo
                  end if
                  print*,holes

                  if ((holes .eq. 0).or.(X(1,1).lt.35.)) then !(B)
                     print*,"ok"
                     kmss=M
                     print*,"write"
                     if (kmss.ge.2) then !(C) 
                        do k=1,kmss
                           if (X(k,1).lt.2.) then
                              nvals=nvals+0
                              ndue=ndue+1
                              temf_qc(k,np)=4
                              salf_qc(k,np)=4
                              dptf_qc(k,np)=4
!                              temf(k,np)=9.96921e+36
!                              salf(k,np)=9.96921e+36
!                              dptf(k,np)=9.96921e+36
                           else
                              nvals=nvals+1
                              ndue=ndue+0
                              temf_qc(k,np)=1
                              salf_qc(k,np)=1
                              dptf_qc(k,np)=1
                              temf(k,np)=X(k,2)
                              salf(k,np)=X(k,3)
                              dptf(k,np)=X(k,1)
                           endif
                        enddo
                     endif !(C)
                  else
                    write(99,'(a54)') 'data lack in the thermocline, &
                       profile has been deleted'
                    nprof=nprof+1
                    do oo=1,lev
                       if ( pres(oo,np) .eq. presmis ) then
                          pres(oo,np) = -999.
                       endif
                       if ( tem(oo,np) .eq. temmis ) then
                          tem(oo,np) = -999.
                       endif
                       if ( sal(oo,np) .eq. salmis ) then
                          sal(oo,np) = -999.
                       endif
                       if (( pre_qc(n,np) .ne. presqmis ) .and. &
                          ( tem_qc(n,np) .ne. temqmis ) .and. &
                          ( sal_qc(n,np) .ne. salqmis )) then
                       nohl=nohl+1
                       write(34,11)dateb(np),',',lon(np),',',lat(np), &
                         ',',pres(oo,np),',',tem(oo,np), &
                         ',',sal(oo,np),',',trim(plnall),',',6
                       endif
                    enddo 
                  endif !(B)
                  deallocate ( X, PRO, PROH )
               endif !(A)
!                 deallocate ( se, r, errt, errs )
!                  end if !(continuare da prima di questo endif) (C)
!                  deallocate ( bfrq, xx, X, PRO, PROH )
!                  deallocate ( X, PRO, PROH )
!               end if  !(fine stability check)
!               deallocate ( bfrq, xx, X, PRO, PROH )
            else
               write(99,'(a70)') 'Descending profile skipped ',infile
               nprof=nprof+1
               do oo=1,lev
                  if ( pres(oo,np) .eq. presmis ) then
                      pres(oo,np) = -999.
                  endif
                  if ( tem(oo,np) .eq. temmis ) then
                      tem(oo,np) = -999.
                  endif
                  if ( sal(oo,np) .eq. salmis ) then
                      sal(oo,np) = -999.
                  endif
                  if (( pre_qc(oo,np) .ne. presqmis ) .and. &
                       ( tem_qc(oo,np) .ne. temqmis ) .and. &
                       ( sal_qc(oo,np) .ne. salqmis )) then
                     nods=nods+1
                     write(34,11)dateb(np),',',lon(np),',',lat(np),',', &
                      pres(oo,np),',',tem(oo,np),',', &
                      sal(oo,np),',',trim(plnall),',',3
                  endif
               enddo
            endif
            else 
            write(99,'(a70)') 'No good lon',infile
            nprof=nprof+1
            do oo=1,lev
               if ( pres(oo,np) .eq. presmis ) then
                   pres(oo,np) = -999.
               endif
               if ( tem(oo,np) .eq. temmis ) then
                   tem(oo,np) = -999.
               endif
               if ( sal(oo,np) .eq. salmis ) then
                   sal(oo,np) = -999.
               endif
               if (( pre_qc(oo,np) .ne. presqmis ) .and. &
                       ( tem_qc(oo,np) .ne. temqmis ) .and. &
                       ( sal_qc(oo,np) .ne. salqmis )) then
                  nolo=nolo+1
                  write(34,11)dateb(np),',',lon(np),',',lat(np),',', &
                    pres(oo,np),',',tem(oo,np),',',sal(oo,np),&
                    ',',trim(plnall),',',2
               endif
            enddo
            end if !(End check on Longitude value)
         else
            write(99,'(a70)') 'no qc on time and position',infile
            nprof=nprof+1
            do oo=1,lev
               if ( pres(oo,np) .eq. presmis ) then
                   pres(oo,np) = -999.
               endif
               if ( tem(oo,np) .eq. temmis ) then
                   tem(oo,np) = -999.
               endif
               if ( sal(oo,np) .eq. salmis ) then
                   sal(oo,np) = -999.
               endif
               if (( pre_qc(oo,np) .ne. presqmis ) .and. &
                   ( tem_qc(oo,np) .ne. temqmis ) .and. &
                   ( sal_qc(oo,np) .ne. salqmis )) then
                  nodp=nodp+1
                  write(34,11)dateb(np),',',lon(np),',',lat(np),',', &
                    pres(oo,np),',',tem(oo,np),',',sal(oo,np),&
                    ',',trim(plnall),',',1
               endif
            enddo
         end if !(End check on LON )
      enddo
!       print*,nvals
!------- WRITE OUTPUT FILE
      print*,"Create NetCDF file"
      ist = nf_create(trim(outdir)//'/'//trim(infile), nf_NoClobber,ncio)
      call handle_err(ist)
      !!------- ADD DIMENSIONS -------
      ist=nf_def_dim(ncio, 'DEPTH', lev , depoid)
      call handle_err(ist)
      ist=nf_def_dim(ncio, 'POSITION', prof , posoid)
      call handle_err(ist)
      ist=nf_def_dim(ncio, 'LONGITUDE', prof , lonoid)
      call handle_err(ist)
      ist=nf_def_dim(ncio, 'LATITUDE', prof , latoid)
      call handle_err(ist)
      ist=nf_def_dim(ncio, 'TIME', prof, timoid)
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
      dimenst(2)=timoid
      dimenst(1)=stroid

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
      call handle_err(ist)
      ist=nf_def_var(ncio, 'DEPH_QC', nf_byte, 2,dimen, pqoid)
      call handle_err(ist)
      ist=nf_def_var(ncio, 'TEMP', nf_float, 2,dimen, toid) 
      call handle_err(ist)
!      ist=nf_copy_att(ncid, idtem, '_FillValue', ncio, toid)
!      call handle_err(ist)
      ist=nf_put_att_real(ncio, toid, '_FillValue', nf_float, &
          1, 9.96921e+36 )
      call handle_err(ist)
      ist=nf_def_var(ncio, 'TEMP_QC', nf_byte, 2,dimen, tqoid) 
      call handle_err(ist)
      ist=nf_def_var(ncio, 'PSAL', nf_float, 2,dimen, soid) 
      call handle_err(ist)
!      ist=nf_copy_att(ncid, idsal, '_FillValue', ncio, soid)
!      call handle_err(ist)
      ist=nf_put_att_real(ncio, soid, '_FillValue', nf_float, &
          1, 9.96921e+36 )
      call handle_err(ist)
      ist=nf_def_var(ncio, 'PSAL_QC', nf_byte, 2,dimen, sqoid) 
      call handle_err(ist)
!      sist = nf_get_att_text(ncid,n_global,"wmo_inst_type",wmo)
!      IF (sist .NE. NF_NOERR) THEN
!         PRINT *,"wmo_inst_type doesn't exist"
         wmo='999'
         ist = nf_put_att_text(ncio,nf_global,'wmo_inst_type',3,wmo)
         call handle_err(ist)
!      ELSE
!         ist=nf_copy_att(ncid, nf_global, 'wmo_inst_type', ncio,nf_global)
!         call handle_err(ist)
!      ENDIF
!      wist = nf_get_att_text (ncid,n_global,"wmo_platform_code",wpc)
!      IF (wist .ne. NF_NOERR) then
!         PRINT *,"wmo_platform_code doesn't exist"
         if ( len(trim(plnall)) .eq. 5) then
            wpc=plnalld//(trim(plnall))
         else if ( len(trim(plnall)) .eq. 6) then
            wpc=plnallu//(trim(plnall))
         else if ( len(trim(plnall)) .eq. 7) then
            wpc=trim(plnall)
         else
            wpc='0000000'
         endif
         ist = nf_put_att_text(ncio,nf_global,'wmo_platform_code',7,wpc)
         call handle_err(ist)
!      ELSE
!         ist=nf_copy_att(ncid, nf_global, 'wmo_platform_code', ncio,nf_global)
!         call handle_err(ist)
!      ENDIF
      ist=nf_def_var(ncio, 'DC_REFERENCE', nf_char, 2,dimenst, pnoid)
      call handle_err(ist)
      ist = nf_enddef(ncio)
      call handle_err(ist)
      print*,"Variables declared"

      ist=nf_put_var_double(ncio, tmoid, jul)
      call handle_err(ist)
      ist=nf_put_var_double(ncio, tmqoid, jul_qc)
      call handle_err(ist)
      ist=nf_put_var_double(ncio, lonvoid, lon)
      call handle_err(ist)
      ist=nf_put_var_double(ncio, latvoid, lat)
      call handle_err(ist)
      ist=nf_put_var_double(ncio, posqoid, pos_qc)
      call handle_err(ist)
      ist=nf_put_var_real(ncio, poid, dptf)
      call handle_err(ist)
      ist=nf_put_var_int(ncio, pqoid, dptf_qc)
      call handle_err(ist)
      ist=nf_put_var_real(ncio, toid, temf)
      call handle_err(ist)
      ist=nf_put_var_int(ncio, tqoid, temf_qc)
      call handle_err(ist)
      ist=nf_put_var_real(ncio, soid, salf)
      call handle_err(ist)
      ist=nf_put_var_int(ncio, sqoid, salf_qc)
      call handle_err(ist)
      print*,"ok"
      ist=nf_put_var_text(ncio, pnoid, dcr)
      call handle_err(ist)
      ist = nf_close (ncio)
      ist = nf_close (ncid)

      write(33,20)  &
      nodp*2,',',nolo*2,',',nods*2,',', &
      noqc*2,',',nolm*2,',',nohl*2,',', &
      ndue*2,',',nprof,',',nvals*2

      close(33)
      close(34)
      close(35)
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
10 format(i8,i8,f10.5,f10.5,f10.5,f10.5,f10.5,f10.5)
11 format(i8,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,a8,a1,i2)
20 format(i6,a1,i6,a1,i6,a1,i6,a1,i6,a1,i6,a1, &
      i6,a1,i6,a1,i6)
21 format(a90)
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
      real function pot_tem(tem1,sal1,pres1)

      real*8 tem,sal,pres
      real   tem1,sal1,pres1

      tem=tem1
      sal=sal1
      pres=pres1*0.1

      pot_tem = tem -   &
                pres * ( 3.6504e-4 + 8.3198e-5*tem - 5.4065e-7*tem**2  &
                       + 4.0274e-9*tem**3 ) -                          &
                pres * ( sal - 35.) * (1.7439e-5 - 2.9778e-7*tem)  -   &
                pres**2 * ( 8.9309e-7 - 3.1628e-8*tem + 2.1987e-10*tem**2 ) &
               + 4.1057e-9 * (sal-35.) * pres**2 -                          &
                 pres**3 * ( -1.6056e-10 + 5.0484e-12*tem)
      end

!----------------------------------------------------------------------
!----------------------------------------------------------------------
      SUBROUTINE bn2g ( km, tem, sal, dep, bn2)


      INTEGER jj
      REAL zgde3w, zt, zs, zh, zalbet, zbeta
      REAL fsalbt, fsbeta
      REAL pft, pfh
      REAL tem(km), sal(km), dep(km), bn2(km), dz(km)

!---
      fsalbt( pft, pfs, pfh ) =                                           &
        ( ( ( -0.255019e-07 * pft + 0.298357e-05 ) * pft                  &
                                  - 0.203814e-03 ) * pft                  &
                                  + 0.170907e-01 ) * pft                  &
                                  + 0.665157e-01                          &
       +(-0.678662e-05 * pfs - 0.846960e-04 * pft + 0.378110e-02 ) * pfs  &
       +  ( ( - 0.302285e-13 * pfh                                        &
              - 0.251520e-11 * pfs                                        &
              + 0.512857e-12 * pft * pft          ) * pfh                 &
                                   - 0.164759e-06   * pfs                 &
           +(   0.791325e-08 * pft - 0.933746e-06 ) * pft                 &
                                   + 0.380374e-04 ) * pfh

      fsbeta( pft, pfs, pfh ) =                                           &
        ( ( -0.415613e-09 * pft + 0.555579e-07 ) * pft                    &
                                - 0.301985e-05 ) * pft                    &
                                + 0.785567e-03                            &
       +( 0.515032e-08 * pfs + 0.788212e-08 * pft - 0.356603e-06 ) * pfs  &
       +(  (   0.121551e-17 * pfh                                         &
             - 0.602281e-15 * pfs                                         &
             - 0.175379e-14 * pft + 0.176621e-12 ) * pfh                  &
                                  + 0.408195e-10   * pfs                  &
          +( - 0.213127e-11 * pft + 0.192867e-09 ) * pft                  &
                                  - 0.121555e-07 ) * pfh
!---
       do k=1,km-1
          dz(k) = dep(k+1)-dep(k)
          zgde3w = 9.81/dz(k)
          zt = 0.5*( tem(k) + tem(k+1) )
          zs = 0.5*( sal(k) + sal(k+1) ) - 35.0
          zh = 0.5*( dep(k) + dep(k+1) )
          zalbet = fsalbt( zt, zs, zh )
          zbeta  = fsbeta( zt, zs, zh )
          bn2(k) = zgde3w * zbeta                                   &
              * ( zalbet * ( tem(k) - tem(k+1) ) - ( sal(k) - sal(k+1) ) )
       enddo


       END
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
