MODULE obs_str_oceanvar

!-----------------------------------------------------------------------
!                                                                      !
! Observational vectors                                                !
!                                                                      !
! Version 1: S.Dobricic 2006                                           !
! Version 2: J.Pistoia, February 2013                                  !
!-----------------------------------------------------------------------

   use set_knd_oceanvar

implicit none


public

! ---
! Observational vector for SLA
   TYPE sla_t

        INTEGER(i8)              ::  no         ! Number of all observations
        INTEGER(i8)              ::  nc         ! Number of good observations
        REAL(r8)                 ::  dep        ! Minimum depth for observations
        INTEGER(i8)              ::  kdp        ! Model level corresponding to dep
        INTEGER(i8), POINTER     ::  ino(:)     ! Instrument
        INTEGER(i8), POINTER     ::  flg(:)     ! Quality flag
        INTEGER(i8), POINTER     ::  flc(:)     ! Temporary flag for multigrid
        REAL(r8),    POINTER     ::  lon(:)     ! Longitute
        REAL(r8),    POINTER     ::  lat(:)     ! Latitude
        REAL(r8),    POINTER     ::  tim(:)     ! Time
        REAL(r8),    POINTER     ::  val(:)     ! Observed value
        REAL(r8),    POINTER     ::  bac(:)     ! Background value
        REAL(r8),    POINTER     ::  inc(:)     ! Increments
        REAL(r8),    POINTER     ::  bia(:)     ! Bias
        REAL(r8),    POINTER     ::  err(:)     ! Observational error
        REAL(r8),    POINTER     ::  res(:)     ! residual
        REAL(r8),    POINTER     ::  b_a(:)     ! Background - analyses
        INTEGER(i8), POINTER     ::  ib(:)      ! i index of the nearest west point
        REAL(r8)   , POINTER     ::  pb(:)      ! distance from the nearest west point
        INTEGER(i8), POINTER     ::  jb(:)      ! j index of the nearest south point
        REAL(r8)   , POINTER     ::  qb(:)      ! distance from the nearest south point
        REAL(r8)   , POINTER     ::  pq1(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq2(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq3(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq4(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  dtm(:)     ! Mean of the dynamic topography
        REAL(r8)   , POINTER     ::  mdt(:,:)   ! Mean dynamic topography

   END TYPE sla_t

   TYPE (sla_t)                 :: sla
! ---
! Observational vector for ARGO floats
   TYPE arg_t

        INTEGER(i8)              ::  no         ! Number of all observations
        INTEGER(i8)              ::  nc         ! Number of good observations
        REAL(r8)                 ::  dep        ! Minimum depth for observations
        INTEGER(i8)              ::  kdp        ! Model level corresponding to dep
        INTEGER(i8), POINTER     ::  ino(:)     ! Float number
        INTEGER(i8), POINTER     ::  par(:)     ! Parameter flag (1-temperature, 2-salinity)
        INTEGER(i8), POINTER     ::  flg(:)     ! Quality flag
        INTEGER(i8), POINTER     ::  flc(:)     ! Temporary flag for multigrid
        REAL(r8),    POINTER     ::  lon(:)     ! Longitute
        REAL(r8),    POINTER     ::  lat(:)     ! Latitude
        REAL(r8),    POINTER     ::  dpt(:)     ! Depth
        REAL(r8),    POINTER     ::  tim(:)     ! Time
        REAL(r8),    POINTER     ::  val(:)     ! Observed value
        REAL(r8),    POINTER     ::  bac(:)     ! Background value
        REAL(r8),    POINTER     ::  inc(:)     ! Increments
        REAL(r8),    POINTER     ::  bia(:)     ! Bias
        REAL(r8),    POINTER     ::  err(:)     ! Observational error
        REAL(r8),    POINTER     ::  res(:)     ! residual
        REAL(r8),    POINTER     ::  b_a(:)     ! Background - analyses
        INTEGER(i8), POINTER     ::  ib(:)      ! i index of the nearest west point
        REAL(r8)   , POINTER     ::  pb(:)      ! distance from the nearest west point
        INTEGER(i8), POINTER     ::  jb(:)      ! j index of the nearest south point
        REAL(r8)   , POINTER     ::  qb(:)      ! distance from the nearest south point
        INTEGER(i8), POINTER     ::  kb(:)      ! k index of the nearest point below
        REAL(r8)   , POINTER     ::  rb(:)      ! distance from the nearest point below
        REAL(r8)   , POINTER     ::  pq1(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq2(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq3(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq4(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq5(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq6(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq7(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq8(:)     ! Interpolation parameter for masked grids

   END TYPE arg_t

   TYPE (arg_t)                 :: arg

! ---
! Observational vector for XBT profiles
   TYPE xbt_t

        INTEGER(i8)              ::  no         ! Number of all observations
        INTEGER(i8)              ::  nc         ! Number of good observations
        REAL(r8)                 ::  dep        ! Minimum depth for observations
        INTEGER(i8)              ::  kdp        ! Model level corresponding to dep
        INTEGER(i8), POINTER     ::  ino(:)     ! Float number
        INTEGER(i8), POINTER     ::  par(:)     ! Parameter flag (1-temperature)
        INTEGER(i8), POINTER     ::  flg(:)     ! Quality flag
        INTEGER(i8), POINTER     ::  flc(:)     ! Temporary flag for multigrid
        REAL(r8),    POINTER     ::  lon(:)     ! Longitute
        REAL(r8),    POINTER     ::  lat(:)     ! Latitude
        REAL(r8),    POINTER     ::  dpt(:)     ! Depth
        REAL(r8),    POINTER     ::  tim(:)     ! Time
        REAL(r8),    POINTER     ::  val(:)     ! Observed value
        REAL(r8),    POINTER     ::  bac(:)     ! Background value
        REAL(r8),    POINTER     ::  inc(:)     ! Increments
        REAL(r8),    POINTER     ::  bia(:)     ! Bias
        REAL(r8),    POINTER     ::  err(:)     ! Observational error
        REAL(r8),    POINTER     ::  res(:)     ! residual
        REAL(r8),    POINTER     ::  b_a(:)     ! Background - analyses
        INTEGER(i8), POINTER     ::  ib(:)      ! i index of the nearest west point
        REAL(r8)   , POINTER     ::  pb(:)      ! distance from the nearest west point
        INTEGER(i8), POINTER     ::  jb(:)      ! j index of the nearest south point
        REAL(r8)   , POINTER     ::  qb(:)      ! distance from the nearest south point
        INTEGER(i8), POINTER     ::  kb(:)      ! k index of the nearest point below
        REAL(r8)   , POINTER     ::  rb(:)      ! distance from the nearest point below
        REAL(r8)   , POINTER     ::  pq1(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq2(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq3(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq4(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq5(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq6(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq7(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq8(:)     ! Interpolation parameter for masked grids

   END TYPE xbt_t

   TYPE (xbt_t)                 :: xbt

! ---
! Observational vector for SST profiles
   TYPE sst_t

        INTEGER(i8)              ::  no         ! Number of all observations
        INTEGER(i8)              ::  nc         ! Number of good observations
        REAL(r8)                 ::  dep        ! Minimum depth for observations
        INTEGER(i8)              ::  kdp        ! Model level corresponding to dep
        INTEGER(i8), POINTER     ::  ino(:)     ! Float number
        INTEGER(i8), POINTER     ::  par(:)     ! Parameter flag (1-temperature)
        INTEGER(i8), POINTER     ::  flg(:)     ! Quality flag
        INTEGER(i8), POINTER     ::  flc(:)     ! Temporary flag for multigrid
        REAL(r8),    POINTER     ::  lon(:)     ! Longitute
        REAL(r8),    POINTER     ::  lat(:)     ! Latitude
        REAL(r8),    POINTER     ::  dpt(:)     ! Depth
        REAL(r8),    POINTER     ::  tim(:)     ! Time
        REAL(r8),    POINTER     ::  val(:)     ! Observed value
        REAL(r8),    POINTER     ::  bac(:)     ! Background value
        REAL(r8),    POINTER     ::  inc(:)     ! Increments
        REAL(r8),    POINTER     ::  bia(:)     ! Bias
        REAL(r8),    POINTER     ::  err(:)     ! Observational error
        REAL(r8),    POINTER     ::  res(:)     ! residual
        REAL(r8),    POINTER     ::  b_a(:)     ! Background - analyses
        INTEGER(i8), POINTER     ::  ib(:)      ! i index of the nearest west point
        REAL(r8)   , POINTER     ::  pb(:)      ! distance from the nearest west point
        INTEGER(i8), POINTER     ::  jb(:)      ! j index of the nearest south point
        REAL(r8)   , POINTER     ::  qb(:)      ! distance from the nearest south point
        INTEGER(i8), POINTER     ::  kb(:)      ! k index of the nearest point below
        REAL(r8)   , POINTER     ::  rb(:)      ! distance from the nearest point below
        REAL(r8)   , POINTER     ::  pq1(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq2(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq3(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq4(:)     ! Interpolation parameter for masked grids

   END TYPE sst_t

   TYPE (sst_t)                 :: sst

! ---

! ---
! Observational vector for gliders
   TYPE gld_t

        INTEGER(i8)              ::  no         ! Number of all observations
        INTEGER(i8)              ::  nc         ! Number of good observations
        REAL(r8)                 ::  dep        ! Minimum depth for observations
        INTEGER(i8)              ::  kdp        ! Model level corresponding to dep
        INTEGER(i8), POINTER     ::  ino(:)     ! Glider number
        INTEGER(i8), POINTER     ::  par(:)     ! Parameter flag (1-temperature, 2-salinity)
        INTEGER(i8), POINTER     ::  flg(:)     ! Quality flag
        INTEGER(i8), POINTER     ::  flc(:)     ! Temporary flag for multigrid
        REAL(r8),    POINTER     ::  lon(:)     ! Longitute
        REAL(r8),    POINTER     ::  lat(:)     ! Latitude
        REAL(r8),    POINTER     ::  dpt(:)     ! Depth
        REAL(r8),    POINTER     ::  tim(:)     ! Time
        REAL(r8),    POINTER     ::  val(:)     ! Observed value
        REAL(r8),    POINTER     ::  bac(:)     ! Background value
        REAL(r8),    POINTER     ::  inc(:)     ! Increments
        REAL(r8),    POINTER     ::  bia(:)     ! Bias
        REAL(r8),    POINTER     ::  err(:)     ! Observational error
        REAL(r8),    POINTER     ::  res(:)     ! residual
        REAL(r8),    POINTER     ::  b_a(:)     ! Background - analyses
        INTEGER(i8), POINTER     ::  ib(:)      ! i index of the nearest west point
        REAL(r8)   , POINTER     ::  pb(:)      ! distance from the nearest west point
        INTEGER(i8), POINTER     ::  jb(:)      ! j index of the nearest south point
        REAL(r8)   , POINTER     ::  qb(:)      ! distance from the nearest south point
        INTEGER(i8), POINTER     ::  kb(:)      ! k index of the nearest point below
        REAL(r8)   , POINTER     ::  rb(:)      ! distance from the nearest point below
        REAL(r8)   , POINTER     ::  pq1(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq2(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq3(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq4(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq5(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq6(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq7(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq8(:)     ! Interpolation parameter for masked grids

   END TYPE gld_t

   TYPE (gld_t)                 :: gld

! ---

! ---
! Observational vector for velocity from drifters
   TYPE vdr_t

        INTEGER(i8)              ::  no         ! Number of all observations
        INTEGER(i8)              ::  nc         ! Number of good observations
        REAL(r8)                 ::  dep        ! Minimum depth for observations
        INTEGER(i8), POINTER     ::  flg(:)     ! Quality flag
        INTEGER(i8), POINTER     ::  flc(:)     ! Temporary flag for multigrid
        INTEGER(i8), POINTER     ::  ino(:)     ! Float number
        INTEGER(i8), POINTER     ::  par(:)     ! Parameter flag (1 - u component, 2 - v component)
        REAL(r8),    POINTER     ::  lon(:)     ! Longitude
        REAL(r8),    POINTER     ::  lat(:)     ! Latitude
        REAL(r8),    POINTER     ::  dpt(:)     ! Depth
        INTEGER(i8), POINTER     ::  kdp(:)     ! Model level corresponding to dep
        REAL(r8),    POINTER     ::  tim(:)     ! Time
        REAL(r8),    POINTER     ::  tms(:)     ! Starting time for averaging
        REAL(r8),    POINTER     ::  tme(:)     ! Final time for averaging
        REAL(r8),    POINTER     ::  val(:)     ! Observed value
        REAL(r8),    POINTER     ::  bac(:)     ! Background value
        REAL(r8),    POINTER     ::  inc(:)     ! Increments
        REAL(r8),    POINTER     ::  bia(:)     ! Bias
        REAL(r8),    POINTER     ::  err(:)     ! Observational error
        REAL(r8),    POINTER     ::  res(:)     ! residual
        REAL(r8),    POINTER     ::  b_a(:)     ! Background - analyses
        INTEGER(i8), POINTER     ::  ib(:)      ! i index of the nearest west point
        REAL(r8)   , POINTER     ::  pb(:)      ! distance from the nearest west point
        INTEGER(i8), POINTER     ::  jb(:)      ! j index of the nearest south point
        REAL(r8)   , POINTER     ::  qb(:)      ! distance from the nearest south point
        INTEGER(i8), POINTER     ::  nav(:)     ! Number of time steps for averaging
        INTEGER(i8), POINTER     ::  kb(:)      ! k index of the nearest point below
        REAL(r8)   , POINTER     ::  rb(:)      ! distance from the nearest point below
        REAL(r8)   , POINTER     ::  pq1(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq2(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq3(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq4(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq5(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq6(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq7(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq8(:)     ! Interpolation parameter for masked grids

   END TYPE vdr_t

   TYPE (vdr_t)                 :: vdr

! ---
! Observational vector for velocity from gliders
   TYPE gvl_t

        INTEGER(i8)              ::  no         ! Number of all observations
        INTEGER(i8)              ::  nc         ! Number of good observations
        REAL(r8)                 ::  dep        ! Minimum depth for observations
        INTEGER(i8), POINTER     ::  flg(:)     ! Quality flag
        INTEGER(i8), POINTER     ::  flc(:)     ! Temporary flag for multigrid
        INTEGER(i8), POINTER     ::  ino(:)     ! Float number
        INTEGER(i8), POINTER     ::  par(:)     ! Parameter flag (1 - u component, 2 - v component)
        REAL(r8),    POINTER     ::  lon(:)     ! Longitude
        REAL(r8),    POINTER     ::  lat(:)     ! Latitude
        REAL(r8),    POINTER     ::  dpt(:)     ! Depth
        REAL(r8),    POINTER     ::  dzr(:,:)   ! Relative thickness of layers
        INTEGER(i8), POINTER     ::  kdp(:)     ! Model level corresponding to dep
        REAL(r8),    POINTER     ::  tim(:)     ! Time
        REAL(r8),    POINTER     ::  tms(:)     ! Starting time for averaging
        REAL(r8),    POINTER     ::  tme(:)     ! Final time for averaging
        REAL(r8),    POINTER     ::  val(:)     ! Observed value
        REAL(r8),    POINTER     ::  bac(:)     ! Background value
        REAL(r8),    POINTER     ::  inc(:)     ! Increments
        REAL(r8),    POINTER     ::  bia(:)     ! Bias
        REAL(r8),    POINTER     ::  err(:)     ! Observational error
        REAL(r8),    POINTER     ::  res(:)     ! residual
        REAL(r8),    POINTER     ::  b_a(:)     ! Background - analyses
        INTEGER(i8), POINTER     ::  ib(:)      ! i index of the nearest west point
        REAL(r8)   , POINTER     ::  pb(:)      ! distance from the nearest west point
        INTEGER(i8), POINTER     ::  jb(:)      ! j index of the nearest south point
        REAL(r8)   , POINTER     ::  qb(:)      ! distance from the nearest south point
        INTEGER(i8), POINTER     ::  nav(:)     ! Number of time steps for averaging
        INTEGER(i8), POINTER     ::  kb(:)      ! k index of the nearest point below
        REAL(r8)   , POINTER     ::  rb(:)      ! distance from the nearest point below
        REAL(r8)   , POINTER     ::  pq1(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq2(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq3(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq4(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq5(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq6(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq7(:)     ! Interpolation parameter for masked grids
        REAL(r8)   , POINTER     ::  pq8(:)     ! Interpolation parameter for masked grids

   END TYPE gvl_t

   TYPE (gvl_t)                 :: gvl


END MODULE obs_str_oceanvar
