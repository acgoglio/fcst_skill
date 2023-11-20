      program sstean 
!---------------------------------------------------------------------!
! This program reads the SST from Satellite on the model grid,        !
! produced by the script sst2NEMO.sh, and the sea surface temperature ! 
! from the NEMO output file; then writes an ascii file with the       !
! coordinates of each sea point, oserved sst and model sst.           !                           
! Structure of the program                                            !
! 1- Variable declaration                                             !
! 2- Reading of SST observations                                      !
! 3- Reading of the model SST                                         !
! 4- Reading of the regions                                           !
! 4- Writing ASCII output file                                        !
!                                                                     !
! Structure of the output file (SST.csv):                             !
! region,variable_id (3=SST),longitude,latitude,depth,                !
! model, observation                                                  !
! Please refer to the README.txt file in this directory for the       ! 
! complete documentation about this program.                          !
!                                                                     !
! Written by A.Grandi October 2016                                    ! 
!---------------------------------------------------------------------!  

 
      use netcdf 
      
      integer ii, jj, iii, jjj      
      integer idsst, idreg
      real, parameter:: dpt=0.
      integer, parameter:: idt=3
      real*4, dimension (821,253) :: sst, sstmod, mlon, mlat
      integer, dimension (821,253) :: masreg 
      character*256 :: infile
      logical :: file_exists

      call getarg(1,infile)
      if(iargc().ne.1)stop 'Stop wrong number of arguments'
      INQUIRE(file='SST.csv',EXIST=file_exists)
      if (file_exists) then
         open(12,file='SST.csv',form='formatted',position='append')
      else
         open(12,file='SST.csv',form='formatted')
      endif

!---------------------------------------------------------------
!              READ FILE WITH SST OBSERVATIONS                      
!---------------------------------------------------------------

      ist = nf90_open('sst.nc',NF90_NOWRITE, ncio)
      call handle_err(ist)
       

      !!!! SST !!!!
      ist = nf90_inq_varid (ncio,'analysed_sst',idsst)
      call handle_err(ist)

      ist = nf90_get_var(ncio,idsst,sst)
      call handle_err(ist)

      ist = nf90_close (ncio)
      print*,'OK reading SST observations'

!-------------------------------------------
!              READ MODEL FILE                      
!-------------------------------------------

      call read_sys(trim(infile),mlon,mlat,sstmod)

! Mask of Gulf of Biscay and the Atlantic boxes

      do iii=1,250
         do jjj=1,45
            sstmod(iii,jjj)=0.
         enddo
      enddo
      do iii=1,250
         do jjj=191,253
            sstmod(iii,jjj)=0.
         enddo
      enddo

!-------------------------------------------
!            READ FILE WITH REGIONS                      
!-------------------------------------------

      ist = nf90_open('MFS_QVR_17r_16_20.nc', NF90_NOWRITE , ncir)
      call handle_err(ist)

      !!!! REGS !!!!
      ist = nf90_inq_varid (ncir,'regs',idreg)
      call handle_err(ist)

      ist = nf90_get_var  (ncir,idreg,masreg)
      call handle_err(ist)

      ist = nf90_close (ncir)


      do ii=1,821
         do jj=1,253
            if ( sstmod(ii,jj).gt.0. .and. sst(ii,jj).gt.0) then 
               write(12,11)masreg(ii,jj),',',idt,',',mlon(ii,jj),',', &
                       mlat(ii,jj),',',dpt,',',sstmod(ii,jj),',', &
                       (sst(ii,jj)*0.01)
            endif
         enddo
      enddo

      close(12)
11 format(i2,a1,i1,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5,a1,f10.5)
      stop

      end program sstean 
!!-----------------------------------------------------------------------
!!----------------------------------------------------------------------- 
               
               subroutine read_sys(fileTm,navlon,navlat,sstfld) 
               use netcdf 
              
               character*37::fileTm
               integer, parameter::imt=821, jmt=253, zmt=1
               integer :: idtempv 
               real*4, dimension (imt,jmt):: navlon, navlat
               real*4, dimension (imt,jmt):: sstfld 
               real*4, dimension (imt,jmt):: sst_int 
               real*4, dimension (imt,jmt,zmt):: tempv
               integer ist
               print*,trim(fileTm)
               ist = nf90_open( trim(fileTm) , NF90_NOWRITE , ncim)
	       call handle_err(ist)
               ist = nf90_inq_varid (ncim, 'nav_lat', idnla)
               call handle_err(ist)
               ist = nf90_get_var (ncim,idnla,navlat)
               call handle_err(ist)
               ist = nf90_inq_varid (ncim, 'nav_lon', idnlo)
               call handle_err(ist)
               ist = nf90_get_var (ncim,idnlo,navlon)
               call handle_err(ist)
	      ! ist = nf90_inq_varid (ncim, 'votemper', idtempv)
               ist = nf90_inq_varid (ncim, 'sst_int', idtempv)
               call handle_err(ist)
               !ist = nf90_get_var  (ncim,idtempv,tempv)
               ist = nf90_get_var  (ncim,idtempv,sst_int)
               call handle_err(ist)
               ist = nf90_close (ncim)
               !sstfld=tempv(:,:,1) 
               sstfld=sst_int
               print*,'Open model file'
 
               return
               end  
!------------------------------------------!
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
