      program calcean
!-----------------------------------------------------------------------------!
! This program reads the input data file for the 3Dvar,                       !
! interpolates horizontaly and verticaly the model on the observations        !
! then writes an ascii file with the results in order to calculate            !
! the EAN.                                                                    !
! Structure of the program                                                    !
! 1- Variable declaration                                                     !
! 2- Reading of Argo observations taken from routine ini_arg_oceanvar.f90     !
!    Version 1: S.Dobricic, January 2007                                      !
! 3- Splitting in profiles                                                    !
! 4- Horizontal interpolation taken from Class4 routine                       !
!    A.Grandi and S.Dobricic 2006                                             !
! 5- Finding region where the profile is located                              !
! 6- Vertical interpolation                                                   !
! 7- Writing ASCII output file                                                !
! Structure of the output file (INPUT.csv):                                   !
! region,variable_id (1=Temperature,2=Salinity),longitude,latitude,depth,     !
! model, observation, instrument_id (1=ARGO,2=XBT,3=GLIDER)                   ! 
! Please refer to the README.txt file in this directory for the complete      !
! documentation about this program.                                           !
!                                                                             !
! Written by A.Grandi September 2016                                          !
!-----------------------------------------------------------------------------!

 use set_knd_oceanvar
 use obs_str_oceanvar

   implicit none

      integer(i_p) :: idm, k
      integer:: xx, yy, startc, endc, lenpr, tab, l, nn, nreg, kk
      real*4, allocatable, dimension (:,:)::matr
!      real*4, allocatable, dimension (:):: temper, salinita, r
      integer, parameter:: znt=18, idt=1, ids=2, nonum=0, insid=1
      real*4, dimension (znt):: toc, soc, depv
      real*4, dimension (znt):: temper, salinita, r
      character*256 :: infile
      logical :: file_exists 

      call getarg(1,infile)

      if(iargc().ne.1)stop 'Stop wrong number of arguments'
      INQUIRE(file='INSITU.csv',EXIST=file_exists)
      if (file_exists) then
         open(12,file='INSITU.csv',form='formatted',position='append')
      else
         open(12,file='INSITU.csv',form='formatted')
      endif

!----------------------------------------------!
!  READ FILE WITH ARGO OBSERVATIONS            !
!----------------------------------------------!

        open(411,file='ARGO.dat',form='formatted',status='old',err=1234)

        read(411,"(i8)") arg%no

      go to 1235
 1234 continue
      arg%no = 0
 1235 continue

 if(arg%no.ne.0)then

   allocate ( arg%ino(arg%no), arg%par(arg%no), arg%val(arg%no), arg%err(arg%no))
   allocate ( arg%lon(arg%no), arg%lat(arg%no), arg%dpt(arg%no), arg%tim(arg%no))

! ---
! Read observations
          startc=1
        do k=1,arg%no
           arg%ino(k) = 1
           read(411,"(I5,I4,6F10.5,I8)")       idm , arg%par(k), arg%lon(k)    &
                                       , arg%lat(k), arg%dpt(k)                &
                                       , arg%tim(k), arg%val(k), arg%err(k)    &
                                       , arg%ino(k)
           if ( k.eq.1 ) then
              print*,"first point"
           else if ( k.ne.arg%no) then
           if ( (arg%lon(k).ne.arg%lon(k-1)).or. &
              (arg%lat(k).ne.arg%lat(k-1)).or. &
              (arg%tim(k).ne.arg%tim(k-1)) ) then
              ! Last line of the profile
              endc=k-1
              ! Length of the profile
              lenpr=(endc-startc+1)/2
              ! Last line with the value of T
              ! tab+1 first line with the value of S   
              tab=startc+lenpr-1
              allocate ( matr(lenpr,3) )
!              allocate ( temper(lenpr) )
!              allocate ( salinita(lenpr), r(lenpr) )
              temper=-999999999
              salinita=-999999999
              matr(:,1)=arg%dpt(startc:tab)
              matr(:,2)=arg%val(startc:tab)
              matr(:,3)=arg%val(tab+1:endc)
!---
! Horizontal interpolation
              call inter_sys(trim(infile),arg%lon(k-1), &
                   arg%lat(k-1),xx,yy,depv,toc,soc)
!---
! Region 
              call find_reg(xx,yy,nreg)
              !-
              ! Vertical interpolation
              ! Only observations with
              ! 8 sea points are taken 
              ! in account
              !-
!              print*,matr(:,1)       
              do nn=1,znt
                 do l=1,lenpr-1
!                 do nn=1,znt-1
!                    if (matr(l,1).lt.depv(1)) then
                    if (depv(nn).lt.matr(1,1)) then
                       temper(nn)=matr(1,2)
                       salinita(nn)=matr(1,3)
                    endif
!                    if ((matr(l,1).ge.depv(nn)).and. &
!                       ( matr(l,1).le.depv(nn+1)) ) then
                    if ((depv(nn).ge.matr(l,1)).and. &
                       (depv(nn).le.matr(l+1,1)) ) then
                       r(nn)=(depv(nn)-matr(l,1))/(matr(l+1,1)-matr(l,1))
                          if ((matr(l,2).gt.0).and. &
                             (matr(l+1,2).gt.0)) then
                             temper(nn)=matr(l,2)+r(nn)*(matr(l+1,2)-matr(l,2))
                             salinita(nn)=matr(l,3)+r(nn)*(matr(l+1,3)-matr(l,3))
                          else
                             temper(nn)=-999999999
                             salinita(nn)=-999999999
                          endif
                    endif
                 enddo
              enddo
!              matr(:,4)=temper
!              matr(:,5)=salinita
!---
! Writng results
              do kk=1,znt
                 if (temper(kk).gt.-10) then
                    write(12,11)nreg,',',idt,',',arg%lon(k-1),',', &
                       arg%lat(k-1),',',depv(kk),',',toc(kk),',', &
                       temper(kk),',',insid
                 endif
              enddo
              do kk=1,znt
                 if (temper(kk).gt.-10) then
                    write(12,11)nreg,',',ids,',',arg%lon(k-1),',', &
                       arg%lat(k-1),',',depv(kk),',',soc(kk),',', &
                       salinita(kk),',',insid
                 endif
              enddo
!              deallocate ( matr, temper, salinita, r )
              deallocate ( matr )
              startc=k
           endif
           else
           ! last profile of the ARGO.dat
              endc=k
              lenpr=(endc-startc+1)/2
              tab=startc+lenpr-1
              allocate ( matr(lenpr,3) )
!              allocate ( temper(lenpr) )
!              allocate ( salinita(lenpr), r(lenpr) )
              temper=-999999999
              salinita=-999999999
              matr(:,1)=arg%dpt(startc:lenpr)
              matr(:,2)=arg%val(startc:tab)
              matr(:,3)=arg%val(tab+1:endc)
              call inter_sys(trim(infile),arg%lon(k-1), &
                   arg%lat(k-1),xx,yy,depv,toc,soc)
              call find_reg(xx,yy,nreg)
!              do l=1,lenpr
!                 do nn=1,znt-1
!                    if (matr(l,1).lt.depv(1)) then
!                       temper(l)=toc(1)
!                       salinita(l)=soc(1)
!                    endif
!                    if ((matr(l,1).ge.depv(nn)).and. &
!                       ( matr(l,1).le.depv(nn+1)) ) then
!                       r(l)=(matr(l,1)-depv(nn))/(depv(nn+1)-depv(nn))
!                          if ((toc(nn).gt.0).and. &
!                             (toc(nn+1).gt.0)) then
!                             temper(l)=toc(nn)+r(l)*(toc(nn+1)-toc(nn))
!                             salinita(l)=soc(nn)+r(l)*(soc(nn+1)-soc(nn))
!                          else
!                             temper(l)=-999999999
!                             salinita(l)=-999999999
!                          endif
!                    endif
!                 enddo
!              enddo
              do nn=1,znt
                 do l=1,lenpr-1
                    if (depv(nn).lt.matr(1,1)) then
                       temper(nn)=matr(1,2)
                       salinita(nn)=matr(1,3)
                    endif
                    if ((depv(nn).ge.matr(l,1)).and. &
                       (depv(nn).le.matr(l+1,1)) ) then
                       r(nn)=(depv(nn)-matr(l,1))/(matr(l+1,1)-matr(l,1))
                          if ((matr(l,2).gt.0).and. &
                             (matr(l+1,2).gt.0)) then
                             temper(nn)=matr(l,2)+r(nn)*(matr(l+1,2)-matr(l,2))
                             salinita(nn)=matr(l,3)+r(nn)*(matr(l+1,3)-matr(l,3))
                          else
                             temper(nn)=-999999999
                             salinita(nn)=-999999999
                          endif
                    endif
                 enddo
              enddo
!              matr(:,4)=temper
!              matr(:,5)=salinita
!---
! Writng results
!              do kk=1,lenpr
!                 if (matr(kk,4).gt.-10) then
!                    write(12,11)nreg,',',idt,',',arg%lon(k-1),',', &
!                       arg%lat(k-1),',',matr(kk,1),',',matr(kk,4),',', &
!                       matr(kk,2),',',insid
!                 endif
!              enddo
!              do kk=1,lenpr
!                 if (matr(kk,5).gt.-10) then
!                    write(12,11)nreg,',',ids,',',arg%lon(k-1),',', &
!                       arg%lat(k-1),',',matr(kk,1),',',matr(kk,5),',', &
!                       matr(kk,3),',',insid
!                 endif
!              enddo
              do kk=1,znt
                 if (temper(kk).gt.-10) then
                    write(12,11)nreg,',',idt,',',arg%lon(k-1),',', &
                       arg%lat(k-1),',',depv(kk),',',toc(kk),',', &
                       temper(kk),',',insid
                 endif
              enddo
              do kk=1,znt
                 if (temper(kk).gt.-10) then
                    write(12,11)nreg,',',ids,',',arg%lon(k-1),',', &
                       arg%lat(k-1),',',depv(kk),',',soc(kk),',', &
                       salinita(kk),',',insid
                 endif
              enddo
!              deallocate ( matr, temper, salinita, r )
              deallocate ( matr )
           endif
        enddo !end read observations
      else
         write(12,11)nonum,',',nonum,',',nonum,',', &
                       nonum,',',nonum,',',nonum,',', &
                       nonum,',',insid   
      endif !end if statement arg%no.ne.0
      close(12)
11 format(i2,a1,i1,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,i1)
! ---
      stop

      end program calcean
!------------------------------------!
!------------------------------------!
!        Routines section            !
!------------------------------------!
!------------------------------------!
!----------------------------------------------!
! This routine opens NEMO output file and      !
! interpolates model on the data position      !
! N.B. The NEMO file doesn't have the          !
! Athlantic box.                               !
!----------------------------------------------!
      subroutine inter_sys(fileTm,longitude,latitude,nlonl,nlatl,livello,tom,som)
      use netcdf

      character*33::fileTm
      real*8 :: latitude, longitude, dpt
!      integer, parameter::imt=821, jmt=253, zmt=72, nc=2
      integer, parameter::imt=1307, jmt=380, zmt=18, nc=2
      integer :: idnla, idnlo, iddt, idtempv,idsalv
      real*4, dimension (zmt):: livello, tempso, tempno, tempse, tempne
      real*4, dimension (zmt):: salso, salno, salse, salne, tom, som, depm
      real*4, dimension (imt,jmt):: navlon, navlat, lonm, latm,diff
      real*4, dimension (nc,nc,zmt):: tempvt, salvt, c
      real*4, dimension (zmt) :: diffz
      real*4, dimension (imt,jmt,zmt):: tempv, salv
      real*4 :: dx, dy, xx, yy, lonv, lonl, latv, latl, p, q, zz
      integer :: ii, jj, nx, ny, nni, i, j, z, nz, iz
      integer ist, nlonv, nlonl, nlatv, nlatl, cc, t, ndepv , ndepl
 
      !--------------------------!
      !  Open NEMO output file   !
      !--------------------------!
      print*,trim(fileTm)
!      print*,longitude,latitude
      ist = nf90_open( trim(fileTm) , NF90_NOWRITE , ncim)
      call handle_err(ist)
      print*,"File opened"
      ist = nf90_inq_varid (ncim, 'nav_lat', idnla)
      call handle_err(ist)
      ist = nf90_get_var (ncim,idnla,navlat)
      call handle_err(ist)
      ist = nf90_inq_varid (ncim, 'nav_lon', idnlo)
      call handle_err(ist)
      ist = nf90_get_var (ncim,idnlo,navlon)
      call handle_err(ist)
      ist = nf90_inq_varid (ncim, 'deptht', iddt)
      call handle_err(ist)
      ist = nf90_get_var  (ncim,iddt,livello)
      call handle_err(ist)
      ist = nf90_inq_varid (ncim, 'votemper', idtempv)
      call handle_err(ist)
      ist = nf90_get_var  (ncim,idtempv,tempv)
      call handle_err(ist)
      ist = nf90_inq_varid (ncim, 'vosaline', idsalv)
      call handle_err(ist)
      ist = nf90_get_var  (ncim,idsalv,salv)
      call handle_err(ist)
      ist = nf90_close (ncim)
!      print*,'Model file opened'

      !--------------------------------------------!
      ! Find the 4 nearest model points to the obs !
      !--------------------------------------------!
      lonm(:,:)=navlon(:,:)-longitude
      latm(:,:)=navlat(:,:)-latitude
      diff(:,:)=abs(lonm(:,:)) + abs(latm(:,:))
      do ii=2,imt-1
         do jj=2,jmt-1
            if (diff(ii,jj).le.diff(ii,jj+1).and. &
               diff(ii,jj).lt.diff(ii,jj-1)) then
               if (diff(ii,jj).le.diff(ii+1,jj).and. &
                  diff(ii,jj).lt.diff(ii-1,jj)) then
                  nx=ii
                  ny=jj
               endif
            endif
         enddo
      enddo
!      xx=821-(36.25-longitude)/0.0625
      xx=1307-(36.29167-longitude)/0.04166666666667
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
!      yy=253-(45.9375-latitude)/0.0625
      yy=380-(45.97917-latitude)/0.04166666666667
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
      lonv=navlon(nlonv,nlatv)
      lonl=navlon(nlonl,nlatl)
      latv=navlat(nlonv,nlatv)
      latl=navlat(nlonl,nlatl)
      !---------------------------------------------------!
      ! Extraction of the water column around the profile !
      !---------------------------------------------------!
      tempvt=tempv(nlonv:nlonl,nlatv:nlatl,:)
      tempso=tempv(nlonv,nlatv,:)
      tempno=tempv(nlonv,nlatl,:)
      tempse=tempv(nlonl,nlatv,:)
      tempne=tempv(nlonl,nlatl,:)
      salvt=salv(nlonv:nlonl,nlatv:nlatl,:)
      salso=salv(nlonv,nlatv,:)
      salno=salv(nlonv,nlatl,:)
      salse=salv(nlonl,nlatv,:)
      salne=salv(nlonl,nlatl,:)
      ist = nf_close (ncim)
!      print*,'Extraction of model variable ok'
      !----------------------------!
      ! Calculation of the weights !
      !----------------------------!
      p=(longitude-lonv)/(lonl-lonv)
      q=(latitude-latv)/(latl-latv)  
      do nn=1,zmt
         if (salso(nn).eq.0.) then
            salso(nn)=0
         endif
         if (salse(nn).eq.0.) then
            salse(nn)=0
         endif
         if (salno(nn).eq.0.) then
            salno(nn)=0
         endif
         if (salne(nn).eq.0.) then
            salne(nn)=0
         endif
         if (tempso(nn).eq.0.) then
            tempso(nn)=0
         endif
         if (tempse(nn).eq.0.) then
            tempse(nn)=0
         endif
         if (tempno(nn).eq.0.) then
            tempno(nn)=0
         endif
         if (tempne(nn).eq.0.) then
            tempne(nn)=0
         endif
      enddo  
      c=salvt
      do i=1,2
         do j=1,2
            do z=1,18
               if (c(i,j,z).eq.0.) then
                  c(i,j,z)=0
               else
                  c(i,j,z)=1
               endif
            enddo
         enddo
      enddo
      !-----------------------------------!
      ! Horizontal wieghted interpolation !
      ! Only levels with 4 sea points are !
      ! taken in account                  !
      !-----------------------------------!
      do nn=1,zmt
         if ((c(1,1,nn)+c(1,2,nn)+c(2,1,nn)+c(2,2,nn)).eq.4.) then
            tom(nn)=(1-q)*((1-p)*tempso(nn)+p*tempse(nn))+q*((1-p)*tempno(nn)+p*tempne(nn))
            som(nn)=(1-q)*((1-p)*salso(nn)+p*salse(nn))+q*((1-p)*salno(nn)+p*salne(nn))
         else
            tom(nn)=-99999
            som(nn)=-99999
         endif
      enddo
      print*,'Horizontal interpolation done'
      return
      end
!------------------------------------------!
!------------------------------------------!
! Find region where the profile is located !
! using the rule of the nearest point      !
!------------------------------------------! 
      subroutine find_reg(aa,bb,ix)
      use netcdf

      real*4, dimension (1307,380) :: masreg
      integer :: ix
      integer :: aa, bb

!      print*,aa,bb
!      ist = nf90_open('MFS_16_72_n_cut.nc', NF90_NOWRITE , ncir)
      ist = nf90_open('MFS_24_y_mdt_final_full.nc', NF90_NOWRITE , ncir)
      call handle_err(ist)

      !!!! REGS !!!!
      ist = nf90_inq_varid (ncir,'regs',idreg)
      call handle_err(ist)

      ist = nf90_get_var  (ncir,idreg,masreg)
      call handle_err(ist)

      ist = nf90_close (ncir)
      ix=nint(masreg(aa,bb))
!      print*,ix
      return
      end 
!--------------------------------------------------------------
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
