      include 'netcdf.inc'

!INPUT:
! 1-file name 2-Date

      character*256 :: indir, outdir, infile, listfile
      character*28 :: oufile
      integer ::  ist, ncid,  prof, lev, N, cln, start(2), count(2)
      integer :: yyyy, mm, dd, longitude, latitude, posit
      double precision,dimension(:), allocatable :: jul, lat, lon
      double precision,dimension(:), allocatable :: jul_qc,pos_qc
      character*32 ::  pln
      integer::  iihour, iimin, A, B, M, P, Q
      double precision,dimension(:), allocatable:: tem_qc, sal_qc, pre_qc
      real,dimension(:), allocatable :: pres, tem, sal, dpt
      real,dimension(:), allocatable :: bfrq, xx
      real,dimension(:,:), allocatable :: X, PRO, PROH
      real :: DATA(5000,3), DAT(5000,3),  limit, mean
      character*2 :: cmon, cday,chr,cmin
      character*4 cyear
      character*8 date
      character(len=10)::odate
      character(len=5)::  otime
!!!!! DICHIARAZIONE VARIABILE 2 PROGRAMMA
      parameter(nlns=1000*1000,nprofs=10000)
      parameter(km=46,kmt=72,km2=2*km,kms=10000)
      real,dimension(:), allocatable ::  deps, targ, sarg
! real,dimension(:) ::  deps, targ, sarg
      dimension lnprf(nprofs),lnpre(nprofs)
      integer inoa(nlns), para(nlns)
      integer platn
      integer indx
      real lona(nlns), lata(nlns), dpta(nlns), tima(nlns), vala(nlns), erra(nlns)
      character*1 CHAR1
      character*4 CHAR4
      character*10 CDATE
      character*5 CHOUR
      character*3 datatype
      character*2 cinm, cind, chrs, cdys, cdya
      character*4 ciny , cwin
      character*1 indxx
      real pot_tem

      call getarg(1,indir)
      call getarg(2,outdir)
      call getarg(3,infile)
      call getarg(4,date)
      if(iargc().ne.4)stop 'Stop wrong number of arguments'
      print*,trim(infile)
      read(date(1:4),'(i4)')yyyy
      read(date(5:6),'(i2)')mm
      read(date(7:8),'(i2)')dd
      datatype=infile(14:15)
      if ( datatype == "PF" ) then
         indx = 1
      else
         indx = 2
      end if

      call conv_date_jul(dd,mm,yyyy,ijln)
      rinday = real(ijln) 
      obdy1  = rinday
      obdy2  = rinday +1

      open(12,file=trim(outdir)//'/'//date//'.ARGO.dat',form='formatted',position='append')
      nvals = 0

! open input nc file
      ist = nf_open(trim(indir)//'/'//infile,nf_read, ncid)
      call handle_err(ist)
      ! get id variable
      
      !!!! PLATFORM NUMBER !!!!
      ist = nf_get_att_text (ncid,nf_global,"wmo_platform_code",pln)
      call handle_err(ist)
    
      !!!! TIME !!!!
      ist = nf_inq_varid (ncid,'TIME',idjul)
      call handle_err(ist)
      !PRINT *,'TIME'

      !!!! LATITUDE !!!!
      ist = nf_inq_varid (ncid,'LATITUDE',idlat)
      call handle_err(ist)
      !PRINT *,'LATITUDE'

      !!!! LONGITUDE !!!!
      ist = nf_inq_varid (ncid,'LONGITUDE',idlon)
      call handle_err(ist)
      !PRINT *,'LONGITUDE'

      !!!! DEPH !!!!
      ist = nf_inq_varid (ncid,'DEPH',idpre)
      call handle_err(ist)
      !PRINT *,'DEPH'

      !!!! TEMP !!!!
      ist = nf_inq_varid (ncid,'TEMP',idtem)
      call handle_err(ist)
      !PRINT *,'TEMP'

      !!!! PSAL !!!!
      ist = nf_inq_varid (ncid,'PSAL',idsal)
      call handle_err(ist)
      !PRINT *,'PSAL'

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

      !!!! LATITUDE !!!!
      allocate ( lat(prof) )
      ist = nf_get_var_double(ncid,idlat,lat)
      call handle_err(ist)

      !!!! LONGITUDE !!!!
      allocate ( lon(prof) )
      ist = nf_get_var_double(ncid,idlon,lon)
      call handle_err(ist)

      !! INDEXES OF ARRAY
      start(1)=1
      start(2)=1
      count(1)=lev
      count(2)=1

      !!!! DEPH !!!! so la variabile preesistente PRES per leggere DEPH
      allocate ( pres(lev) )
      ist = nf_get_vara_real(ncid,idpre,start,count,pres)
      call handle_err(ist)

      !!!! TEM !!!!
      allocate ( tem(lev) )
      ist = nf_get_vara_real(ncid,idtem,start,count,tem)
      call handle_err(ist)

      !!!! PSAL !!!!
      Allocate ( sal(lev) )
      ist = nf_get_vara_real(ncid,idsal,start,count,sal)
      call handle_err(ist)

!!!! CONTROL ON TIME AND LONGITUDE VALUE

      np=1
      call conv_jul_date(iiday,iimon,iiyear,iihour,iimin,jul(np))
      call conv_date_jul(iiday,iimon,iiyear,ijln)
      iihour=ijln*24+ iihour
      rday = (real(iihour)+real(iimin)/60.)/24.
      if (.not.(rday.ge.obdy1 .and. rday.lt.obdy2 )) then
         print*,'Profile is not in the time window ',rday,obdy1,obdy2
         stop
      else
         print*,'Profile is in the time window ',rday,obdy1,obdy2
!!!! CONVERSION PRESSION TO DEPTH (non necessaria)

      allocate( dpt(lev) )
      do n = 1, lev
         dpt(n) = pres(n)
      enddo

      do k=1,lev
        theta=pot_tem(tem(k),sal(k),pressure(dpt(k),lat(1)))
        tem(k)=theta
      enddo
            
      do k=1,lev
         if (dpt(k).lt.5000) then
            !write(12,"(I5,I4,6f10.5,I8)")       &
            write(12,"(I5,I4,6f10.5,1X,A7)")       &
            indx, 1, lon(1), lat(1), dpt(k), rday - rinday, tem(k), 0, pln(1:7)
         endif
      enddo
    
      do k=1,lev
         if (dpt(k).lt.5000) then
            !write(12,"(I5,I4,6f10.5,I8)")       &
            write(12,"(I5,I4,6f10.5,1X,A7)")       &
            indx, 2, lon(1), lat(1), dpt(k), rday - rinday, sal(k), 0, pln(1:7)
         endif
      enddo
      endif
      close(12)
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
               + 4.1057e-9 * (sal-35.) * pres**2 - &
                 pres**3 * ( -1.6056e-10 + 5.0484e-12*tem)
      end

!----------------------------------------------------------------------
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
