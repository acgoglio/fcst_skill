MODULE set_knd_oceanvar

!-----------------------------------------------------------------------
!                                                                      !
! The precision of reals and integers                                  !
!                                                                      !
! Version 1: S.Dobricic 2006                                           !
!-----------------------------------------------------------------------


implicit none

public

   INTEGER, PARAMETER ::                &
      r_p = SELECTED_REAL_KIND(12,307) ,  &  ! model precission for real
      i_p = SELECTED_INT_KIND(9)             ! model precission for integer

   INTEGER, PARAMETER ::                &
      r4 = SELECTED_REAL_KIND( 6, 37),  &  ! real*4
      r8 = SELECTED_REAL_KIND(12,307)      ! real*8

   INTEGER, PARAMETER ::                &
      i4 = SELECTED_INT_KIND(9) ,       &  ! integer*4
      i8 = SELECTED_INT_KIND(14)           ! integer*8

END MODULE set_knd_oceanvar
