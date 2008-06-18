SUBDIRS	= .

LOCALHDRS = \
	MeqMPI.h MPIProxy.h

LOCALSRCS = \
	MeqMPI.cc MeqMPI_commands.cc MPIProxy.cc

DOCHDRS		= $(LOCALHDRS) 

lib_LTLIBRARIES 	= libmeqmpi.la

libmeqmpi_la_SOURCES 	= $(DOCHDRS) $(LOCALSRCS) AID-MeqMPI-Registry.cc
  
libmeqmpi_la_LIBADD = 

check_PROGRAMS = 

# --- end generate defrec maps

include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
