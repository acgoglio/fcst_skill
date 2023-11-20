      program intsla_nc
!-----------------------------------------------------------------------
!--------------------------------------------------------------
!  PROGRAMMA interpolazione lungo traccia SLA
!--------------------------------------------------------------

! NB. distinguere tra le diverse tracce dello stesso giorno e aggiungere: addizione della stericheight (call steric_height)
! e rimozione della media lungo la traccia sia per 'slaa' che per 'slacm'

      use netcdf

      integer dimenb(5), dimen(5)
      integer :: startb(5), countb(5)
      integer areasid, metricsid, metricsnid, depthsid, forecastsid
      integer timeid, ncid
      integer, parameter:: idsla=4
      character*17, dimension(3) :: fpatha
      character*3:: satel
      integer :: indexsat 
      character*100 :: fpatho, fpathd
      character*4 :: tnamo,tnama
      integer i,ii,nt,ncito,idtime,idnla,idnlo,idslav,idtrack,status,stat
      integer ilt,iln,nta,idt,it,jj,nx,ny,ff,kma,kmo, idflag, hh, idx
      integer ncita, idtima, idlata, idlona, idslaa, idtimo, ijln, pp
      integer iddac, idot, idit
      integer ncitm, idlatm, idlonm, idmdt, ix, iy, rr,iter,i1,k,timp
      integer stdim
      integer, parameter :: imt=1307, jmt=380, zmt=141, nc=2 !, kmt=871 a che serve questo?
      integer nlonv, nlonl, nlatv, nlatl, cc, ld, zz, counter, tt
      real*8, parameter :: fillvalue=-999.
      real*4, parameter :: fillvalues=9999.
      real*4, parameter :: dep=0.
      integer :: xx, yy, nj
      real*8 :: dx, dy, lonv, lonl, latv, latl, p, q
      real*8 :: slaaso, slaano, slaase, slaane, atime
      real*8 dsm,dxx,dyy,dist,sumtb,sumib,sumto,sumio,sumi,sumt
      real*4, dimension (nc,nc) :: c, slaavt
      real*8, dimension (imt,jmt):: slaa,sossh,mddt
      real*8, dimension (imt,jmt):: navlon, navlat, lonm, latm, diff
      real*8, dimension (imt,jmt):: mlt, mln, mdt
      real slamis,lonmis,latmis,scsla,sclon,sclat,timmis,dacmis,scdac
      real scocti, scinti, octimis, intimis
      double precision, dimension (:), allocatable :: date
      integer*4, allocatable, dimension (:) :: track
      integer, dimension (1307,380) :: masreg
      integer*8, allocatable, dimension (:) :: satlat, satlon
      real*8, allocatable, dimension (:) :: slam, slao, longitude
      real*8, allocatable, dimension (:) :: slamf, latitude, dac
      real*8, allocatable, dimension (:) :: slaaint, slares, regs
      real*8, allocatable, dimension (:) :: octi, inti
      integer :: ixx 
      integer*4, allocatable, dimension (:) :: slaflag
      real*8, allocatable, dimension (:) :: slaob, slabb
      character*2 :: day, month, zone
      character*4 :: year, sysnm
      real*4:: misfit, sumobs, summod
      real*4:: obsmean, modmean, mse
      integer*4 km,kk,lg,ka,ko,kl,tn,st,et,ll
      real*8 sumslaa,sumslao
      real*8, allocatable, dimension (:) :: meanslao,meanslaa,slaintr,slaor,lenght
      real*8 sterich
      real*8, dimension(4) :: sterichm
      character*8::dateo, dan
      character*10 :: strF
      character*100::slafile, infile
      integer, parameter:: zzr=345, ttr=129
      real, dimension(zzr,ttr) :: navlonr, navlatr, ref
      integer refs(zzr,ttr)
      real, dimension(zzr) :: lonr
      real, dimension(ttr) :: latr
      logical :: file_exists
!------  per lettura file steric -------------------
       character*200 :: fpathm, fpathr
       integer ncidm, ncidr, idro
       integer idet1, idet2, idet3, idmask
       integer idep, idtemp, idsal
       real*8, dimension (imt,jmt,zmt):: ttlat, e3t, llev, Tpot, Sal, ro0
       real*8, dimension (imt,jmt) :: llon, llat, e1t, e2t
       integer, dimension (imt,jmt,zmt):: tmask
!-------- end ---------------------------------------

!------  per scrittura file netCDF -------------------
       character*5, dimension(3) :: slane, slaner
       character*12, dimension(3) :: slalong
       character*9, dimension(3) :: slalongr
       integer, dimension(3) :: sladim, sladr
       integer obdim, shid,  iddt, fiid, mid, fudim,ftdim,andim,sladimf
       integer, dimension(2) :: kmk
       real*8, allocatable, dimension (:,:) :: meanslam
       
!---------end-----------------------------------------

! NB. controllare numero caratteri e aggiungere campi forecast 2,4-10
      character*100::nsla
      integer yyyy, mm, dd
      real dt1,dt2
      
      stat_sla=9999.

      call getarg(1,infile)
      call getarg(2,slafile)
      call getarg(3,dateo)
      call getarg(4,satel)
      call getarg(5,sysnm)
 
      if(iargc().ne.5)stop 'Stop wrong number of arguments' 

      INQUIRE(file='SLA.csv',EXIST=file_exists)
      if (file_exists) then
         open(12,file='SLA.csv',form='formatted',position='append')
      else
         open(12,file='SLA.csv',form='formatted')
      endif

      read(dateo(1:4),'(i4)')yyyy
      read(dateo(5:6),'(i2)')mm
      read(dateo(7:8),'(i2)')dd
      call conv_date_jul(dd,mm,yyyy,ijln)

      print*,satel
      if(satel=="s3a") then
         indexsat=1
      else if(satel=="c2 ") then
         indexsat=2
      else if(satel=="c2n") then
         indexsat=2
      else if(satel=="j3 ") then
         indexsat=3
      else if(satel=="j3n") then
         indexsat=3
      else if(satel=="j1 ") then
         indexsat=4
      else if(satel=="j2g") then
         indexsat=5
      else if(satel=="al ") then
         indexsat=6
      else if(satel=="s3b") then
         indexsat=7
      else if(satel=="s6a") then
         indexsat=8
       else if(satel=="h2a") then
         indexsat=9
      else
         indexsat=10
      endif
      print*,indexsat

      rinday = real(ijln) 
      obdy1  = rinday
      obdy2  = rinday + 1
!---               Mean Dynamic Topography          ---
       print*,"Open Mean Dynamic Topography"
!       status= nf90_open('MFS_16_72_n_cut.nc', nf90_nowrite, ncitm);
       status= nf90_open('MFS_24_y_mdt_final_full.nc', nf90_nowrite, ncitm);
       if (status /= nf90_noerr) call handle_err(status);


!       status = nf90_inq_varid(ncitm, 'lat', idlatm)
!       if (status /= nf90_noerr) call handle_err(status)
!       status = nf90_get_var(ncitm, idlatm, mlt)
!       if (status /= nf90_noerr) call handle_err(status)


!       status = nf90_inq_varid (ncitm, 'lon', idlonm)
!       if (status /= nf90_noerr) call handle_err(status)
!       status = nf90_get_var(ncitm, idlonm, mln)
!       if (status /= nf90_noerr) call handle_err(status)


       status = nf90_inq_varid (ncitm, 'mdt', idmdt)
       if (status /= nf90_noerr) call handle_err(status)
       status = nf90_get_var(ncitm, idmdt, mddt)
       if (status /= nf90_noerr) call handle_err(status)

       ist = nf90_inq_varid (ncitm,'regs',idreg)
       call handle_err(ist)

       ist = nf90_get_var  (ncitm,idreg,masreg)
       call handle_err(ist)    
       
       ist = nf90_close (ncitm)

!---              SLA Observations             ---
   
      print*,trim(slafile) 
 
      status= nf90_open(trim(slafile), nf90_nowrite, ncito);
      if (status /= nf90_noerr) call handle_err(status);
      
      status = nf90_inq_dimid(ncito, 'time', idtime)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_inquire_dimension(ncito,idtime,tnamo,nt)
      if (status /= nf90_noerr) call handle_err(status)
      
      allocate(date(nt))
      allocate(track(nt))
      allocate(satlat(nt))
      allocate(satlon(nt))
      allocate(latitude(nt))
      allocate(longitude(nt))
      allocate(slao(nt))
      allocate(slam(nt))
      allocate(slaflag(nt))
      allocate(regs(nt))
      allocate(dac(nt))
      allocate(octi(nt))
      allocate(inti(nt))

      status = nf90_inq_varid(ncito, 'time', idtimo)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_get_var(ncito,idtimo,date)
      if (status /= nf90_noerr) call handle_err(status)
      
      status = nf90_inq_varid (ncito, 'track', idtrack)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_get_var(ncito,idtrack,track)
      if (status /= nf90_noerr) call handle_err(status)

      km=1
      do kl=2,nt
      if(track(kl).ne.track(kl-1)) then
      km=km+1
      end if
      end do

      status = nf90_inq_varid(ncito, 'latitude', idnla)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_get_var(ncito, idnla, satlat)
      if (status /= nf90_noerr) call handle_err(status)
      stat = nf90_get_att(ncito,idnla,'scale_factor',sclat)
      stat = nf90_get_att(ncito,idnla,'_FillValue',latmis)

      status = nf90_inq_varid (ncito, 'longitude', idnlo)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_get_var(ncito, idnlo, satlon)
      if (status /= nf90_noerr) call handle_err(status)
      stat = nf90_get_att(ncito,idnlo,'scale_factor',sclon)
      stat = nf90_get_att(ncito,idnlo,'_FillValue',lonmis)

      status = nf90_inq_varid (ncito, 'flag', idflag)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_get_var(ncito,idflag,slaflag)
      if (status /= nf90_noerr) call handle_err(status)

      status = nf90_inq_varid (ncito, 'sla_filtered', idslav)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_get_var(ncito, idslav, slao)
      if (status /= nf90_noerr) call handle_err(status)
      stat = nf90_get_att(ncito,idslav,'scale_factor',scsla)
      stat = nf90_get_att(ncito,idslav,'_FillValue',slamis)

      status = nf90_inq_varid (ncito, 'dac', iddac)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_get_var(ncito, iddac, dac)
      if (status /= nf90_noerr) call handle_err(status)
      stat = nf90_get_att(ncito,iddac,'scale_factor',scdac)
      stat = nf90_get_att(ncito,iddac,'_FillValue',dacmis)
      
      status = nf90_inq_varid (ncito, 'ocean_tide', idot)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_get_var(ncito, idot, octi)
      if (status /= nf90_noerr) call handle_err(status)
      stat = nf90_get_att(ncito,idot,'scale_factor',scocti)
      stat = nf90_get_att(ncito,idot,'_FillValue',octimis)

      status = nf90_inq_varid (ncito, 'internal_tide', idit)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_get_var(ncito, idit, inti)
      if (status /= nf90_noerr) call handle_err(status)
      stat = nf90_get_att(ncito,idit,'scale_factor',scinti)
      stat = nf90_get_att(ncito,idit,'_FillValue',intimis)
      do ld=1,nt
          if (.not.((satlon(ld).eq.lonmis).or.(satlat(ld).eq.latmis))) then
!              if (satlon(ld)*sclon.gt.50) then
!                  satlon(ld)=satlon(ld)-(360*1000000)
!              endif
              longitude(ld)=satlon(ld)*sclon
              latitude(ld)=satlat(ld)*sclat
          endif
      enddo
            
      do nj=1,nt
         if ((longitude(nj).ge.-6).and.(longitude(nj).le.36.25).and. &
             (latitude(nj).ge.30.1875).and.(latitude(nj).le.45.9375)) then
             if (.not.((longitude(nj).ge.-6).and.(longitude(nj).le.0.).and. &
                 (latitude(nj).ge.43).and.(latitude(nj).le.45.9375))) then
                 if (.not.((longitude(nj).ge.26.5).and.(longitude(nj).le.42.).and. &
                    (latitude(nj).ge.41.).and.(latitude(nj).le.50.))) then
                    if (slao(nj).ne.slamis) then
                    if(sysnm=="EAS5") then
                       slam(nj)=(slao(nj)*scsla)+(dac(nj)*scdac)
                    else
                       slam(nj)=(slao(nj)*scsla)+(dac(nj)*scdac)+(octi(nj)*scocti)+(inti(nj)*scinti)
                    endif
                    else
                       slam(nj)=slamis
                    endif
                 else
                    slam(nj)=slamis
                 endif
             else
                 slam(nj)=slamis
             endif
         else
             slam(nj)=slamis
         endif
      enddo
      ist = nf90_close (ncito) 

!---              Model fields          ---
      print*,trim(infile)
      status= nf90_open(trim(infile), nf90_nowrite, ncita);
      if (status /= nf90_noerr) call handle_err(status);

       status = nf90_inq_varid(ncita, 'nav_lat', idlata)
       if (status /= nf90_noerr) call handle_err(status)
       status = nf90_get_var(ncita, idlata, navlat)
       if (status /= nf90_noerr) call handle_err(status)
       status = nf90_inq_varid (ncita, 'nav_lon', idlona)
       if (status /= nf90_noerr) call handle_err(status)
       status = nf90_get_var(ncita, idlona, navlon)
       if (status /= nf90_noerr) call handle_err(status)

      status = nf90_inq_varid (ncita, 'sossheig', idslaa)
      if (status /= nf90_noerr) call handle_err(status)
      status = nf90_get_var(ncita, idslaa, sossh)
      if (status /= nf90_noerr) call handle_err(status)

      ist = nf90_close (ncita)

!      call steric(e1t,e2t,e3t,tmask,llev,ttlat,Tpot,Sal,ro0,sterich)

!      sterichm(ff)=sterich
!      slaa=slaa+sterichm(ff)

!--------  Subtraction of the MDT to the model ssh ---------
       do ix=1,imt
         do iy=1,jmt
            if (mddt(ix,iy).ne.0 .and. mddt(ix,iy).ne.-9999) then
            slaa(ix,iy)=sossh(ix,iy)-mddt(ix,iy)
            else
            slaa(ix,iy)=1E+20
            end if
          end do
        end do

!---------------------------------------------------------


      allocate(slaaint(nt))
      allocate(slamf(nt))

!!! MISSING VALUE

!      stat = nf90_get_att(ncito,idslav,'_FillValue',slamis)

!-------------------------------------------------------------

          
! calcolo dei pesi
         do it=1,nt
          if ((date(it).lt.obdy1).or.(date(it).ge.obdy2).or.(slam(it).eq.slamis)) then
          slaaint(it)=-999.
          slamf(it)=-999
          else
!            if (longitude(it).gt.180) then
!            longitude(it)=longitude(it)-360.
!            end if
!            call ref_inter(ref,navlonr,navlatr,longitude(it),latitude(it),refsub)
               slamf(it)=slam(it)
	       lonm(:,:)=navlon(:,:)-longitude(it)
	       latm(:,:)=navlat(:,:)-latitude(it)
	       diff(:,:)=abs(lonm(:,:)) + abs(latm(:,:))
	       do ii=2,imt-1
	          do jj=2,jmt-1
	     if (diff(ii,jj).lt.diff(ii,jj+1).and.diff(ii,jj).lt.diff(ii,jj-1)) then
             if (diff(ii,jj).lt.diff(ii+1,jj).and.diff(ii,jj).lt.diff(ii-1,jj)) then 
			    nx=ii
			    ny=jj
			 endif
		     endif
		  enddo
	       enddo
!               xx=821-(36.25-longitude(it))/0.0625
               xx=1307-(36.29167-longitude(it))/0.04166666666667
	       dx=xx-nx
	       if (dx.lt.0) then
	          nlonv=nx-1
		  nlonl=nx
	       else if (dx.eq.0) then
	          nlonv=nx
		  nlonl=nx+1
	       else
	          nlonv=nx
		  nlonl=nx+1
	       endif
!	       yy=253-(45.9375-latitude(it))/0.0625
               yy=380-(45.97917-latitude(it))/0.04166666666667
	       dy=yy-ny
	       if (dy.lt.0) then
	          nlatv=ny-1
		  nlatl=ny
	       else if (dy.eq.0) then
	          nlatv=ny
		  nlatl=ny+1
	       else
	          nlatv=ny
		  nlatl=ny+1
	       endif
               regs(it)=masreg(xx,yy)
	       lonv=navlon(nlonv,nlatv)
	       lonl=navlon(nlonl,nlatl)
	       latv=navlat(nlonv,nlatv)
	       latl=navlat(nlonl,nlatl)
               slaavt=slaa(nlonv:nlonl,nlatv:nlatl)
	       slaaso=slaa(nlonv,nlatv)
	       slaano=slaa(nlonv,nlatl)
	       slaase=slaa(nlonl,nlatv)
               slaane=slaa(nlonl,nlatl)

	       p=(longitude(it)-lonv)/(lonl-lonv)
	       q=(latitude(it)-latv)/(latl-latv)
	       c=slaavt
	       where(c.gt.1E+18)
	             c=0
	       elsewhere
	             c=1
	       end where
	          if ((c(1,1)+c(1,2)+c(2,1)+c(2,2)).eq.4) then
		     slaaint(it)=((1-q)*((1-p)*slaaso+p*slaase)+q*((1-p)*slaano+p*slaane))
		  else
		     slaaint(it)=-999.
		  endif
      end if
      end do  !nt
      print*,"Horizontal interpolation done"
      
!------- calcolo del residuo ----------------------

!slaaint-slam
!      allocate(slares(nt))
      allocate(slaob(nt))
      allocate(slabb(nt))

      do rr=1,nt
       if (slaaint(rr).ne.fillvalue.and.slam(rr).ne.slamis) then
!      print*,'slam=',slam(rr),'  slaaint=',slaaint(rr)
!       slares(rr)=slamf(rr)-slaaint(rr)
        slaob(rr)=slamf(rr)
        slabb(rr)=slaaint(rr)
       else
!       slares(rr)=-999.
        slaob(rr)=-999.
        slabb(rr)=-999.
       end if
      end do

! calcolo e rimozione del bias
!      allocate(slaob(nt))
!      allocate(slabb(nt))

!      slaob=slamf
!      slabb=slaaint

      do iter=1,3

!     slabia(:)=0.0
      timp=track(1)
      dsm=100.
      i1=1
      
      do k=2,nt

      dxx=6371.*3.14/180.*(longitude(k)-longitude(k-1))*cos(latitude(k)*3.14/180.)
      dyy=6371.*3.14/180.*(latitude(k)-latitude(k-1))
      dist=sqrt(dxx**2+dyy**2)
      
!      print*,dxx, dyy,   dist

        if((track(k).ne.timp.or.dist.gt.dsm).and.k.gt.1) then
!          sumt=0.0
!          sumi=0.0
          sumtb=0.0
          sumto=0.0
          sumib=0.0
          sumio=0.0
           do i=i1,k-1
!           print*,slaflag(i),slares(i)
            if( (slabb(i).ne.-999.).or.(slaob(i).ne.-999.) ) then
!            if(slaflag(i).eq.1.and.slares(i).ne.-999.) then
!            sumt=sumt+slares(i)
!            sumi=sumi+1.0
             sumtb=sumtb+slabb(i)
             sumib=sumib+1.0
             sumto=sumto+slaob(i)
             sumio=sumio+1.0
            end if
           end do
!         if(sumi.gt.0.) sumt=sumt/sumi
         if(sumib.gt.0.) sumtb=sumtb/sumib
         if(sumio.gt.0.) sumto=sumto/sumio
          do i=i1,k-1
           if ( (slabb(i).ne.-999.).or.(slaob(i).ne.-999.) ) then
!           slares(i)=slares(i)-sumt
           slaob(i)=slaob(i)-sumto
           slabb(i)=slabb(i)-sumtb
!           slabia(i)=sumt
           else
!          slares(i)=-999.
            slaob(i)=-999.
            slabb(i)=-999.
           end if
          end do
         timp=track(k)
         i1=k
         else if(k.eq.nt.and.k.ge.i1) then
!         sumt=0.0
!         sumi=0.0
           sumtb=0.0
           sumto=0.0
           sumib=0.0
           sumio=0.0
          do i=i1,k
          if( (slabb(i).ne.-999.).or.(slaob(i).ne.-999.) ) then
!           if(slaflag(i).eq.1.and.slares(i).ne.-999.) then
!           sumt=sumt+slares(i)
!           sumi=sumi+1.0
            sumtb=sumtb+slabb(i)
            sumib=sumib+1.0
            sumto=sumto+slaob(i)
            sumio=sumio+1.0
           end if
          end do
!           if(sumi.gt.0.) sumt=sumt/sumi
           if(sumib.gt.0.) sumtb=sumtb/sumib
           if(sumio.gt.0.) sumto=sumto/sumio
           do i=i1,k
            if ( (slabb(i).ne.-999.).or.(slaob(i).ne.-999.) ) then
!            slares(i)=slares(i)-sumt
             slaob(i)=slaob(i)-sumto
             slabb(i)=slabb(i)-sumtb
!           slabia(i)=sumt
            else
!            slares(i)=-999.
             slaob(i)=-999.
             slabb(i)=-999.
            end if
           end do
         end if
      end do !k
      end do !iter
      do hh=1,nt
         if ( (slabb(hh).ne.-999.).or.(slaob(hh).ne.-999.) ) then
            write(12,11)int(regs(hh)),',',idsla,',', &
                       longitude(hh),',',latitude(hh), &
                       ',',dep,',',slabb(hh),',', &
                       slaob(hh),',',indexsat
         end if
      enddo
      close(12)
11 format(i2,a1,i1,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,i2)
      end
!****************************************************************************
      SUBROUTINE handle_err(status)
      use netcdf
      integer, intent (in) :: status
      character (len = 80) :: nf_90_strerror
      if (status /= nf90_noerr) then
      write (*,*) nf90_strerror(status)
      stop 'Stopped'
      end if
      end subroutine handle_err
!****************************************************************************
!----------------------------------------------------------------------
      subroutine conv_date_jul(iiday,iimon,iiyear,iijul)

      dimension idmn(12)
      data idmn/ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31/

      iijul = 0

      if(iiyear.lt.1950) stop 'wrong input year'

      do k=1950,iiyear-1
      iijul = iijul + 365
      if(mod(k,4).eq.0)  iijul = iijul + 1
      enddo

      if(iimon.gt.1)then
      do k=1,iimon-1
      iijul = iijul + idmn(k)
      if(k.eq.2 .and. mod(iiyear,4).eq.0)  iijul = iijul + 1
      enddo
      endif

      iijul = iijul + iiday -1

      return
      end
!----------------------------------------------------------------------

      SUBROUTINE steric(e1t,e2t,e3t,tmask,llev,ttlat,Tpot,Sal,ro0,sterr)
!!---------------------------------------------------------------------
!!                  ***  ROUTINE STERIC  ***
!! ** Purpose :  compute STER effe!t as in Mellor and Ezer (1995)
!!
!! ** Method  :
!!               Sub-domain indexes and output frequency are hard-coded
!! History :
!!          11-011  (A. Bonaduce)
!!----------------------------------------------------------------------

      implicit none

! Define indices of the horizontal-vertical output zoom
! ------------------------------------------------------------

      integer x1, x2, y1, y2, z1, z2
      parameter(x1=1, x2=1307, y1=1, y2=380, z1=1, z2=141)

      integer sx,sy,sz
      parameter(sx=1+(x2-x1), sy=1+(y2-y1),sz=1+(z2-z1))

      integer tmask(sx,sy,sz)
      real*8 e1t(sx,sy), e2t(sx,sy), e3t(sx,sy,sz), llev(sx,sy,sz)
      real*8 Tpot(sx,sy,sz), Sal(sx,sy,sz), ttlat(sx,sy,sz)
      real*8 Ti(sx,sy,sz),Presd(sx,sy,sz)
      real*8 SSH(sx,sy), slaa(sx,sy)

      integer x,y,z,zz

      real*8 surf,vol

      real*8 rtemp, ttemp, sigmao, SSHo, STER, sterr, dsigma
      real*8 SVAN
      real*8 sigma(sx,sy,sz), ro0(sx,sy,sz)
      real*8 t_insitu

     

!!----------------------------------------------------------------------
!! Start routine
!!----------------------------------------------------------------------

! 0. Initialisation

! Remove Biscay from tmask_s

      DO z=1,sz
      DO y=200,sy
      DO x=1,100
      tmask(x,y,z)= 0.
      END DO
      END DO
      END DO


! Mediterranean basin area

      surf = 0.
      DO y=1,sy
      DO x=1,sx
      surf=surf+e1t(x,y)*e2t(x,y)*tmask(x,y,1)
      END DO
      END DO


! Mediterranean basin volume

      vol = 0.
      DO z=1,sz
      DO y=1,sy
      DO x=1,sx
      vol=vol+e1t(x,y)*e2t(x,y)*e3t(x,y,z)*tmask(x,y,z)
      END DO
      END DO
      END DO

!!----------------------------------------------------------------------
!! Start computation
!!----------------------------------------------------------------------


      call ref_pressure(llev,ttlat,Presd)


      STER = 0.
      Ti(:,:,:) = 0.
      sigma(:,:,:) = 0.
      DO z=1,sz
      DO y=1,sy
      DO x=1,sx

      IF (Sal(x,y,z).gt.1E+19.and.Tpot(x,y,z).gt.1E+19) THEN
      else

      call POTMP(Presd(x,y,z),Tpot(x,y,z),Sal(x,y,z),0.0,t_insitu)

      Ti(x,y,z) = t_insitu
      rtemp=SVAN(Sal(x,y,z),Ti(x,y,z),Presd(x,y,z),sigmao)
      sigma(x,y,z) = sigmao+1000.

!       write(99,102) Tpot(x,y,z),Ti(x,y,z)
!       print*,'T in situ=',Ti(x,y,z),'sigma=',sigma(x,y,z)

      dsigma=(sigma(x,y,z)-ro0(x,y,z))/ro0(x,y,z)
      STER=STER+dsigma*e1t(x,y)*e2t(x,y)*e3t(x,y,z)*tmask(x,y,z)


       END IF
       END DO
       END DO
       END DO


       sterr=-1*STER/surf

!       print*, 'STER', sterr


       return
       end

!----------------------------------------------------------------------
!----------------------------------------------------------------------
!----------------------------------------------------------------------
!----------------------------------------------------------------------
!******************************************************************************
       REAL*8 FUNCTION SVAN(S,T,P0,SIGMA)
!******************************************************************************
!
!  MODIFIED RCM
!
! ******************************************************
! SPECIFIC VOLUME ANOMALY (STER ANOMALY) BASED ON 1980 EQUATION
! OF STATE FOR SEAWATER AND 1978 PRACTICAL SALINITY SCALE.
! REFERENCES
! MILLERO, ET AL (1980) DEEP-SEA RES.,27A,255-264
! MILLERO & POISSON 1981,DEEP-SEA RES.,28A PP 625-629.
! BOTH ABOVE REFERENCES ARE ALSO FOUND IN UNESCO REPORT 38 (1981)
! UNITS:
!       PRESSURE        P0       DECIBARS
!       TEMPERATURE     T        DEG CELSIUS (IPTS-68)
!       SALINITY        S        PSU (IPSS-78)
!       SPEC. VOL. ANA. SVAN     M**3/KG *1.0E-8
!       DENSITY ANA.    SIGMA    KG/M**3
! CHECK VALUE: SVAN = 981.30190 M**3/KG FOR S = 40 PSU,
! T = 40 DEG C, P0= 10000 DECIBARS.
! ******************************************************************
! *****************************
! CHECK VALUE: SIGMA = 59.82037  KG/M**3 FOR S = 40 PSU,
! T = 40 DEG C, P0= 10000 DECIBARS.
! *******************************************************
      REAL*8 P0,SIGMA
      REAL*8 P,T,S,SIG,SR,R1,R2,R3,R4
      REAL*8 A,B,C,D,E,A1,B1,AW,BW,K,K0,KW,K35
! EQUIV
      EQUIVALENCE (E,D,B1),(BW,B,R3),(C,A1,R2)
      EQUIVALENCE (AW,A,R1),(KW,K0,K)
! ********************
! DATA
      DATA R3500,R4/1028.1063,4.8314E-4/
      DATA DR350/28.106331/
!   R4 IS REFERED TO AS  C  IN MILLERO & POISSON 1981
! CONVERT PRESSURE TO BARS AND TAKE SQUARE ROOT SALINITY.
      P=P0/10.
      SR = SQRT(ABS(S))
! *********************************************************
! PURE WATER DENSITY AT ATMOSPHERIC PRESSURE
!   BIGG P.H.,(1967) BR. J. APPLIED PHYSICS 8 PP 521-537.
!
      R1 = ((((6.536332E-9*T-1.120083E-6)*T+1.001685E-4)*T &
      -9.095290E-3)*T+6.793952E-2)*T-28.263737
! SEAWATER DENSITY ATM PRESS.
!  COEFFICIENTS INVOLVING SALINITY
!  R2 = A   IN NOTATION OF MILLERO & POISSON 1981
      R2 = (((5.3875E-9*T-8.2467E-7)*T+7.6438E-5)*T-4.0899E-3)*T &
      +8.24493E-1
!  R3 = B  IN NOTATION OF MILLERO & POISSON 1981
      R3 = (-1.6546E-6*T+1.0227E-4)*T-5.72466E-3
!  INTERNATIONAL ONE-ATMOSPHERE EQUATION OF STATE OF SEAWATER
      SIG = (R4*S + R3*SR + R2)*S + R1
! SPECIFIC VOLUME AT ATMOSPHERIC PRESSURE
      V350P = 1.0/R3500
      SVA = -SIG*V350P/(R3500+SIG)
      SIGMA=DR350-(SVA/(V350P*(V350P+SVA)))
!  SCALE SPECIFIC VOL. ANAMOLY TO NORMALLY REPORTED UNITS
      SVAN=SVA*1.0E+8
      IF(P.EQ.0.0) RETURN
! ******************************************************************
! ******  NEW HIGH PRESSURE EQUATION OF STATE FOR SEAWATER ********
! ******************************************************************
!        MILLERO, ET AL , 1980 DSR 27A, PP 255-264
!               CONSTANT NOTATION FOLLOWS ARTICLE
!********************************************************
! COMPUTE COMPRESSION TERMS
      E = (9.1697E-10*T+2.0816E-8)*T-9.9348E-7
      BW = (5.2787E-8*T-6.12293E-6)*T+3.47718E-5
      B = BW + E*S
!
      D = 1.91075E-4
      C = (-1.6078E-6*T-1.0981E-5)*T+2.2838E-3
      AW = ((-5.77905E-7*T+1.16092E-4)*T+1.43713E-3)*T &
      -0.1194975
      A = (D*SR + C)*S + AW
!
      B1 = (-5.3009E-4*T+1.6483E-2)*T+7.944E-2
      A1 = ((-6.1670E-5*T+1.09987E-2)*T-0.603459)*T+54.6746 
      KW = (((-5.155288E-5*T+1.360477E-2)*T-2.327105)*T &
      +148.4206)*T-1930.06
      K0 = (B1*SR + A1)*S + KW
! EVALUATE PRESSURE POLYNOMIAL
! ***********************************************
!   K EQUALS THE SECANT BULK MODULUS OF SEAWATER
!   DK=K(S,T,P)-K(35,0,P)
!  K35=K(35,0,P)
! ***********************************************
      DK = (B*P + A)*P + K0
      K35  = (5.03217E-5*P+3.359406)*P+21582.27
      GAM=P/K35
      PK = 1.0 - GAM
      SVA = SVA*PK + (V350P+SVA)*P*DK/(K35*(K35+DK))
!  SCALE SPECIFIC VOL. ANAMOLY TO NORMALLY REPORTED UNITS
      SVAN=SVA*1.0E+8
      V350P = V350P*PK
!  ****************************************************
! COMPUTE DENSITY ANAMOLY WITH RESPECT TO 1000.0 KG/M**3
!  1) DR350: DENSITY ANAMOLY AT 35 PSU 0 DEG. C & ATMOSPHERIC PRES.
!  2) DR35P: DENSITY ANAMOLY 35 PSU 0 DEG. C , WITH PRES. VARIATION
!  3) DVAN : DENSITY ANAMOLY VARIATIONS INVOLVING SPECFIC VOL. ANAMOLY
! ********************************************************************
! CHECK VALUE: SIGMA = 59.82037  KG/M**3 FOR S = 40 PSU,
! T = 40 DEG C, P0= 10000 DECIBARS.
! *******************************************************
      D350=GAM/PK
      DR35P=R3500*D350
      DVAN=SVA/(V350P*(V350P+SVA))
      SIGMA=DR350+DR35P-DVAN
      RETURN
      END

! ------------------------------------------------------------------
      SUBROUTINE POTMP(RP,TEMP,S,PRESS,POTEMP)
!        REAL*8 FUNCTION POTMP(RP,TEMP,S,PRESS,POTEMP)
!
!    TITLE:
!    *****
!
!      POTMP  -- CALCULATE POTENTIAL TEMPERATURE FOR AN ARBITRARY
!                REFERENCE PRESSURE
!
!    PURPOSE:
!    *******
!
!      TO CALCULATE POTENTIAL TEMPERATURE
!
!      REF: N.P. FOFONOFF
!           DEEP SEA RESEARCH
!           IN PRESS NOV 1976
!
!    PARAMETERS:
!    **********
!
!      PRESS  -> PRESSURE IN DECIBARS
!      TEMP   -> TEMPERATURE IN CELSIUS DEGREES
!      S      -> SALINITY PSS 78
!      RP     -> REFERENCE PRESSURE IN DECIBARS
!                (0.0 FOR THE QUANTITY THETA)
!      POTEMP <- POTENTIAL TEMPERATURE (DEG C)
!
        REAL*8 PRESS,TEMP,S,RP,POTEMP
!
!    VARIABLES:
!    *********
!
         INTEGER I,J,N
         REAL*4 DP,P,Q,R1,R2,R3,R4,R5,S1,T,X
!
!    CODE:
!    ****
!
      S1 = S-35.0
      P  = PRESS
      T  = TEMP
!
      DP = RP - P
      N  = IFIX(ABS(DP)/1000.) + 1
      DP = DP/FLOAT(N)
!
      DO 10 I=1,N
         DO 20 J=1,4
!
            R1 = ((-2.1687E-16*T+1.8676E-14)*T-4.6206E-13)*P
            R2 = (2.7759E-12*T-1.1351E-10)*S1
            R3 = ((-5.4481E-14*T+8.733E-12)*T-6.7795E-10)*T
            R4 = (R1+(R2+R3+1.8741E-8))*P+(-4.2393E-8*T+1.8932E-6)*S1
            R5 = R4+((6.6228E-10*T-6.836E-8)*T+8.5258E-6)*T+3.5803E-5
!
            X  = DP*R5
!
            GO TO (100,200,300,400),J
!
  100       CONTINUE
            T = T+.5*X
            Q = X
            P = P + .5*DP
            GO TO 20
!
  200       CONTINUE
            T = T + .29298322*(X-Q)
            Q = .58578644*X + .121320344*Q
            GO TO 20
!
  300       CONTINUE
            T = T + 1.707106781*(X-Q)
            Q = 3.414213562*X - 4.121320344*Q
            P = P + .5*DP
            GO TO 20
!
  400       CONTINUE
            T = T + (X-2.0*Q)/6.0
  20      CONTINUE
  10      CONTINUE
!
        POTEMP = T
        RETURN
!
!        END POTMP
!
        END

!!*********************************************************************
         SUBROUTINE ref_pressure(navlev,navlat,pref)
!!---------------------------------------------------------------------
!!                  ***  ROUTINE p80  ***
!! ** Purpose :  Compute pressure from depth and latitude
!!
!! ** Method  :
!!               Sub-domain indexes and output frequency are hard-coded
!! History :
!!          09-012  (A. Bonaduce)
!!----------------------------------------------------------------------

        implicit none

! Define indices of the horizontal-vertical output zoom
! ------------------------------------------------------------

       integer x1, x2, y1, y2, z1, z2
       parameter(x1=1, x2=1307, y1=1, y2=380, z1=1, z2=141)

       integer sx,sy,sz
       parameter(sx=1+(x2-x1), sy=1+(y2-y1),sz=1+(z2-z1))

!         integer tmask(sx,sy,sz)
       real*8 navlev(sx,sy,sz), navlat(sx,sy,sz), pref(sx,sy,sz)

       real*8 P80

       integer x,y,z
!!----------------------------------------------------------------------
!! Start routine
!!----------------------------------------------------------------------

       DO z=1,sz
       DO y=1,sy
       DO x=1,sx

       pref(x,y,z) = P80(navlev(x,y,z),navlat(x,y,z))

       END DO
       END DO
       END DO


       END


!------- PROFODITA' A PRESSIONE (p80)----------------------------------

!pressure from depth from saunder's formula with eos80.
!reference: saunders,peter m., practical conversion of pressure
!           to depth., j.p.o. , april 1981.
!r millard
!march 9, 1983
!check value: p80=7500.004 dbars;for lat=30 deg., depth=7321.45 meters

!******************************************************************************
        REAL*8 FUNCTION  P80(dpth,xlat)
!******************************************************************************
! pressure from depth from saunder's formula with eos80.
! reference: saunders,peter m., practical conversion of pressure
!            to depth., j.p.o. , april 1981.
! r millard
! march 9, 1983
! check value: p80=7500.004 dbars;for lat=30 deg., depth=7321.45 meters


        REAL*8 plat,d,c1,xlat,dpth,pi

        pi=3.141592654
        plat=abs(xlat*pi/180.)
        d=sin(plat)
        c1=5.92e-3+d**2*5.25e-3
        p80=((1-c1)-sqrt(((1-c1)**2)-(8.84e-6*dpth)))/4.42e-6
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



      return

      end
!----------------------------------------------------------------------




