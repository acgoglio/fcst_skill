SHELL = /bin/sh

############################################################################
#
#        Makefile for QVR.dir 
#
############################################################################
#
#    Copyright 2020 Antonio Mariani, CMCC, Bologna
#
############################################################################
#
# INTEL 

F90=mpiifort 
P_P = -Dopt_netcdf
P_C = cpp -traditional-cpp
F_O = -c
F_M = -g set_knd_oceanvar.f90 obs_str_oceanvar.f90
#
RM  = rm -f
EXTINC = $(FFLAGS)
EXTLIB = $(LDFLAGS)


SRC = sstean.f90 sstcloudean.f90 slaeaneur.f90 prep_ARGO_3dvar_C3_V3.f90 prep_XBT_3dvar_C3_V3.f90 prep_GLIDER_3dvar_C3_V3.f90
SRC2 = argoean.f90 gliderean.f90 xbtean.f90 argoean_18.f90 xbtean_18.f90 argoean_18_m.f90


OBJS = $(SRC:.f90=.o)
EXEC = $(SRC:.f90=.exe)
EXEC2 = $(SRC2:.f90=.exe)


all: $(EXEC) $(EXEC2) 
	@echo $(EXEC) are compiled
	@echo $(EXEC2) are compiled

$(EXEC) :
	$(F90)  $(@:.exe=.f90)  -o $@  $(EXTINC) $(EXTLIB)

$(EXEC2):
	$(F90) $(F_M) $(@:.exe=.f90) -o $@ $(EXTINC) $(EXTLIB) 

clean:
	$(RM) *.o *.mod *.exe
