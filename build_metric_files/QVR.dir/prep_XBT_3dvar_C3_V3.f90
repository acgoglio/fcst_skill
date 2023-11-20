      include './netcdf.inc'

!INPUT:
! 1-file name 2-Date

      character*256 :: indir, outdir, infile,listfile
      character*28 :: oufile
      integer noqc, nosp, nofq, nohl, nolm, ndue
      integer nopr, noml, nodp, nolo
      integer nprof, nods, oo, nobs, iddcr
      character(len=32),allocatable :: dcr(:)
      integer ::  ist, ncid,  prof, lev, N, start(2), count(2)
      double precision,dimension(:), allocatable :: jul, lat, lon
      double precision,dimension(:), allocatable :: julo
      integer ,dimension(:), allocatable :: dateb
      double precision,dimension(:), allocatable :: jul_qc,pos_qc
      double precision :: dptqmis, temqmis
      integer::  iihour, iimini, yyyy, mm, dd
!     integer::  iiday, iimon, iiyear
      integer :: dimen(2), diment(1), dimenst(2), dimenstb(1)
      integer :: dimenla(1), dimenlo(1), dimenp(1)
      integer :: depoid, posoid, lonoid, latoid, timoid, toid
      integer :: tmoid, tmqoid, lonvoid, latvoid, posqoid, wmooid
      integer :: poid, pqoid, tqoid, pnoid, stroid,strboid
!      real::  rday, ijul
      integer::  kkk, kk, rr, rrr, nn, gg, l, rs
      integer, parameter:: t=3000, tt=3001
      integer,dimension(t):: idepth
      real,dimension(t):: re
      real :: dptmis, temmis
      integer, dimension(:), allocatable:: v
      real,dimension(t):: r
      real,dimension(:,:), allocatable:: tem_qc
      real,dimension(:,:), allocatable :: dpt_qc
      real,dimension(:,:), allocatable :: tem
      real,dimension(:,:), allocatable :: dpt
      real :: matr(3000,2)
!      real,dimension(:,:), allocatable :: matr
      integer,dimension(:,:), allocatable:: temf_qc, dptf_qc
      real,dimension(:,:), allocatable:: temf, dptf
 !     real,dimension(:), allocatable:: rday, ijul
     ! integer,dimension(:), allocatable:: iiday, iimon, iiyear, iihour,
     ! iimin 
      character*2 :: cmon, cday,chr,cmin
      character*4 cyear
      character(len=10)::odate
      character(len=5)::  otime
      character*8 date
      parameter(nlns=1000*1000, nprofs=10000)
      parameter(km=37,kms=10000)
      real :: ERR(3,3)
      real :: errf(6)
      dimension depw(km),valw(km),deps(kms),vals(kms)
      dimension iw(km),tw(km), ts(kms)
      dimension lnprf(nprofs),lnpre(nprofs)
      dimension errxbt(146)
      integer inoa(nlns), para(nlns)
      real lona(nlns), lata(nlns), dpta(nlns), tima(nlns)
      real vala(nlns), erra(nlns)
      integer kline, inoaii, parai
      real lonai,latai, dptai,timai,valai,errai
      character*1 CHAR1
      character*4 CHAR4
      character*10 CDATE
      character*5 CHOUR
      character*3 wmo
      character*7 wpc
      character*2 cinm, cind, chrs, cdys, cdya
      character*4 ciny , cwin
      character*90 plnall
      character*1 plnallu
      character*2 plnalld
      character*3 plnallt
      logical :: file_exists
      real pot_tem
!-----------------------------------------------------
      call getarg(1,indir)
      call getarg(2,outdir)
      call getarg(3,infile)
      call getarg(4,date)
      call getarg(5,plnall)
  
      if(iargc().ne.5)stop 'Stop wrong number of arguments'
      
      plnallu=' '
      plnalld='  '
      plnallt='   '

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Open file with numbers of rejected data for every profile 
! Formatting of the file:
! nodp,nolo,nods,noqc,nolm,nohl,ndue,nprof,nvals
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      open(33,file=trim(outdir)//'/'//date//'.XBT_PPREJC.dat', &
           form='formatted',position='append')
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Open file with list of rejected data for every profile
! Formatting of the file:
! date,lon,lat,depth,tem,buoy,flag
! Flag list:
!  1   Bad quality flags on time and position
!  2   Profile out of the Med
!  3   Descending profile (only for Glider)
!  4   Quality flag of Pres, T or S not=1             
!  5   Value of T or S out of range (0<T<35 0<S<45) (only for ARGO and GLIDERS)                              
!  6   Lack in the thermocline (pres(j+1)-pres(j)>40m in the first 300m)  (only for ARGO and GLIDERS)  
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      open(34,file=trim(outdir)//'/'//date//'.XBT_LISTRJ.dat', &
           form='formatted',position='append')
!      open(35,file=trim(outdir)//'/'//date//'.XBT_WRONG.dat', &
!           form='formatted',position='append')
      nvals = 0 ! (number of good data)
      noqc = 0 ! (for one layer one of the qf is not 1)
      nohl = 0 ! (hole in the thermocline, for XBT=0)
      nolm = 0 ! (value not in 0<T<35, 0<S<45, for XBT=0 )
      nodp = 0 ! (bad qf for position or time)
      nolo = 0 ! (Out of the Med basin)
      nods = 0 ! (Discending profile, for Xbt =0)
      nprof = 0 ! (number of profiles rejected)
!      nobs = 0
      ndue = 0 ! (data in the layer between 0 and 2 m)

      print*,trim(indir)//'/'//trim(infile) 
      print*,trim(plnall)

      ist = nf_open(trim(indir)//'/'//trim(infile),'0', ncid)
      call handle_err(ist)

! get id variable
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

      !!!! POSITION_QC !!!!
      ist = nf_inq_varid (ncid,'POSITION_QC',idpos)
      call handle_err(ist)

!      !!!! DC_REFERENCE !!!!
!      ist = nf_inq_varid (ncid,'DC_REFERENCE',iddcr)
!      call handle_err(ist)

      !!!! DEPTH !!!!
      ist = nf_inq_varid (ncid,'DEPH',idpre)
      IF (ist .NE. NF_NOERR) THEN
         PRINT *,"DEPH doesn't exist"
         ist = nf_inq_varid (ncid,'DEPTH',idpre)
         call handle_err(ist)
      ENDIF

      !!!! DEPTH_QC !!!!
      ist = nf_inq_varid (ncid,'DEPH_QC',idpre_qc)
      IF (ist .NE. NF_NOERR) THEN
         PRINT *,"DEPH_QC doesn't exist"
         ist = nf_inq_varid (ncid,'DEPTH_QC',idpre_qc)
         call handle_err(ist)
      ENDIF
       
      !!!! TEMP !!!!
      ist = nf_inq_varid (ncid,'TEMP',idtem)
      call handle_err(ist)

      !!!! TEMP_QC !!!!
      ist = nf_inq_varid (ncid,'TEMP_QC',idtem_qc)
      call handle_err(ist)

!get dimension and length of variables TIME, DEPTH

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
      allocate ( temf_qc(lev,prof) )
      allocate ( dptf_qc(lev,prof) )
      temf=9.96921e+36
      dptf=-99999.
      temf_qc=4
      dptf_qc=4

      !!!! TIME_QC !!!!
      allocate ( jul_qc(prof) )
      ist = nf_get_var_double(ncid,idjul_qc,jul_qc)
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

!      !!!! DC_REFERENCE !!!!
!      allocate(character(32) :: dcr(prof))
!      ist = nf_get_var_text(ncid,iddcr,dcr)
!      call handle_err(ist)

      !! INDEXES OF ARRAY
      start(1)=1
      start(2)=1
      count(1)=lev
      count(2)=prof

      !!!! DEPTH !!!!
      allocate ( dpt(lev,prof) )
      ist = nf_get_vara_real(ncid,idpre,start,count,dpt)
      call handle_err(ist)
      ist = nf_get_att_real(ncid,idpre,'_FillValue',dptmis)
      call handle_err(ist)

      !!!! DEPTH_QC !!!!
      allocate ( dpt_qc(lev,prof) )
      ist = nf_get_vara_real(ncid,idpre_qc,start,count,dpt_qc)
      call handle_err(ist)
      ist = nf_get_att_double(ncid,idpre_qc,'_FillValue',dptqmis)
      call handle_err(ist)

      !!!! TEM !!!!
      allocate ( tem(lev,prof) )
      ist = nf_get_vara_real(ncid,idtem,start,count,tem)
      call handle_err(ist)
      ist = nf_get_att_real(ncid,idtem,'_FillValue',temmis)
      call handle_err(ist)

      !!!! TEM_QC !!!!
      allocate ( tem_qc(lev,prof) )
      ist = nf_get_vara_real(ncid,idtem_qc,start,count,tem_qc)
      call handle_err(ist)
      ist = nf_get_att_double(ncid,idtem_qc,'_FillValue',temqmis)
      call handle_err(ist)

      print*,'Variables read'
!      ist = nf_close (ncid)

!      call conv_date_jul(iiday,iimon,iiyear,jul) 

!        allocate ( iiday(prof), iimon(prof), iiyear(prof) )
!        allocate ( iihour(prof), iimin(prof) ) 
!        allocate ( ijul(prof) )
      do np=1,prof
!         allocate ( matr(lev,2) )
         if ((jul_qc(np) .eq. 1 ) .and. ( pos_qc(np) .eq. 1 )) then 
            call conv_jul_date(dd,mm,yyyy,hh,mn,julo(np))
            dateb(np)=(yyyy*10000)+(mm*100)+dd
            if ((lon(np).ge.-6).and.(lon(np).le.36.25).and. &
               (lat(np).ge.30.1875).and.(lat(np).le.45.9375)) then
               kkk=0
               do kk=1,lev
!                  if (( dpt_qc(kk,np) .ne. dptqmis ) .and. &
!                     ( tem_qc(kk,np) .ne. temqmis )) then
!                     nobs=nobs+1
!                  endif
                  if ((dpt_qc(kk,np).eq.1).and.(tem_qc(kk,np).eq.1)) then
                     kkk=kkk+1
                     matr(kkk,1) = dpt(kk,np)
                     matr(kkk,2) = tem(kk,np)
                  else
                     if ( dpt(kk,np) .eq. dptmis ) then
                        dpt(kk,np) = -999.
                     endif
                     if ( tem(kk,np) .eq. temmis ) then
                        tem(kk,np) = -999.
                     endif
                     if (( dpt_qc(kk,np) .ne. dptqmis ) .and. &
                        ( tem_qc(kk,np) .ne. temqmis )) then 
                       noqc=noqc+1
                       write(34,11)dateb(np),',',lon(np),',',lat(np),',', &
                        dpt(kk,np),',',tem(kk,np),',',trim(plnall),',',4
                     endif
                  endif
               enddo
!               do k=1,kkk
!                  print*,matr(kkk,2)
!               enddo
               if (kkk.ge.2) then !(C) 
                  do k=1,kkk
                     if (matr(k,1).lt.2.) then
                        nvals=nvals+0
                        ndue=ndue+1
                        temf_qc(k,np)=4
                        dptf_qc(k,np)=4
!                       temf(k,np)=9.96921e+36
!                       dptf(k,np)=9.96921e+36
                     else
                        nvals=nvals+1
                        ndue=ndue+0
                        temf_qc(k,np)=1
                        dptf_qc(k,np)=1
                        temf(k,np)=matr(k,2)
                        dptf(k,np)=matr(k,1)
                     endif
                  enddo
               endif
            else
               write(99,'(a70)') 'No good lon',infile
               nprof=nprof+1
               do oo=1,lev
                  if ( dpt(oo,np) .eq. dptmis ) then
                     dpt(oo,np) = -999.
                  endif
                  if ( tem(oo,np) .eq. temmis ) then
                     tem(oo,np) = -999.
                  endif
                  if (( dpt_qc(oo,np) .ne. dptqmis ) .and. &
                     ( tem_qc(oo,np) .ne. temqmis )) then
                     nolo=nolo+1
                     write(34,11)dateb(np),',',lon(np),',',lat(np),',', &
                      dpt(oo,np),',',tem(oo,np),',',trim(plnall),',',2
                  endif
               enddo
            endif 
         else
            print*,'no quality control on date or position, &
               profile skipped'
            nprof=nprof+1
            do oo=1,lev
               if ( dpt(oo,np) .eq. dptmis ) then
                  dpt(oo,np) = -999.
               endif
               if ( tem(oo,np) .eq. temmis ) then
                  tem(oo,np) = -999.
               endif
               if (( dpt_qc(oo,np) .ne. dptqmis ) .and. &
                   ( tem_qc(oo,np) .ne. temqmis )) then
                   nodp=nodp+1
                  write(34,11)dateb(np),',',lon(np),',',lat(np),',', &
                   dpt(oo,np),',',tem(oo,np),',',trim(plnall),',',1
               endif
            enddo 
         endif
!         deallocate ( matr )           
      enddo

!------- WRITE OUTPUT FILE
      print*,"Create NetCDF file"
      ist = nf_create(trim(outdir)//'/'//trim(infile), nf_NoClobber, ncio)
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
          1, -99999. )
      ist=nf_def_var(ncio, 'DEPH_QC', nf_byte, 2,dimen, pqoid)
      call handle_err(ist)
      ist=nf_def_var(ncio, 'TEMP', nf_float, 2,dimen, toid) 
      call handle_err(ist)
!      ist=nf_copy_att(ncid, idtem, '_FillValue', ncio, toid)
!      call handle_err(ist)
      ist=nf_put_att_real(ncio, toid, '_FillValue', nf_float, &
          1, 9.96921e+36 )
      ist=nf_def_var(ncio, 'TEMP_QC', nf_byte, 2,dimen, tqoid) 
      call handle_err(ist)
!!!! WMO_INST_TYPE !!!!
!      sist = nf_get_att_text(ncid,n_global,"wmo_inst_type",wmo)
!      IF (sist .NE. NF_NOERR) THEN
!         PRINT *,"wmo_inst_type doesn't exist"
         wmo='996'
         ist = nf_put_att_text(ncio,nf_global,'wmo_inst_type',3,wmo)
         call handle_err(ist)
!      ELSE 
!         ist=nf_copy_att(ncid, nf_global, 'wmo_inst_type', ncio, nf_global)
!         call handle_err(ist)
!      ENDIF
!      ist=nf_copy_att(ncid, nf_global, 'wmo_platform_code', ncio, nf_global)
!      ist = nf_get_att_text (ncid,n_global,"wmo_platform_code",wpc)
!      if (ist .EQ. NF_NOERR) then
!         PRINT *,"wmo_platform_code doesn't exist"
         if ( len(trim(plnall)) .eq. 4) then
            wpc=plnallt//(trim(plnall))
         else if ( len(trim(plnall)) .eq. 5) then
            wpc=plnalld//(trim(plnall))
         else if ( len(trim(plnall)) .eq. 6) then
            wpc=plnallu//(trim(plnall))
         else if ( len(trim(plnall)) .eq. 7) then
            wpc=trim(plnall)
         else
            wpc='0000000'
         endif
         print*,wpc 
         ist = nf_put_att_text(ncio,nf_global,'wmo_platform_code',7,wpc)
         call handle_err(ist)
!      else
!         ist=nf_copy_att(ncid, nf_global, 'wmo_platform_code', ncio, nf_global)
!         call handle_err(ist)
!      endif
!      ist=nf_copy_att(ncid, nf_global, 'wmo_inst_type', ncio, nf_global)
!      call handle_err(ist)
!      ist=nf_copy_att(ncid, nf_global, 'wmo_platform_code', ncio, nf_global)
!      call handle_err(ist)
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
      print*,"ok"
      ist=nf_put_var_text(ncio, pnoid, dcr)
      call handle_err(ist)
      ist = nf_close (ncio)
      ist = nf_close (ncid)

      print*,"NetCDF file written"

      write(33,20)  &
      nodp,',',nolo,',',nods,',', &
      noqc,',',nolm,',',nohl,',', &
      ndue,',',nprof,',',nvals

      close(12)
      close(33)
      close(34)
1 format(i4,i4,f10.5,f10.5,f10.5,f10.5,f10.5,f10.5)
11 format(i8,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,a8,a1,i2)
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
