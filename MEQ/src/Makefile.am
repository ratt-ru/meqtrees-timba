SUBDIRS	= .

DOCHDRS		 	= 			\
Domain.h					\
Cells.h Polc.h \
Node.h Function.h \
Parm.h ParmPolc.h ParmPolcStored.h \
Add.h Cos.h \
Vells.h VellsTmp.h VellsRep.h \
VellsRealSca.h VellsRealArr.h \
VellsComplexSca.h VellsComplexArr.h \
Result.h \
Forest.h \
ParmTable.h

lib_LTLIBRARIES 	= libmeq.la

libmeq_la_SOURCES 	= $(DOCHDRS)		\
Domain.cc					\
Cells.cc Polc.cc \
Node.cc Function.cc \
Parm.cc ParmPolc.cc ParmPolcStored.cc \
Add.cc Cos.cc \
Vells.cc VellsTmp.cc VellsRep.cc \
VellsRealSca.cc VellsRealArr.cc \
VellsComplexSca.cc VellsComplexArr.cc \
Request.cc Result.cc \
Forest.cc \
ParmTable.cc \
AID-MEQ-Registry.cc

#EXTRA_DIST		=			\
#Beam.m						\
#spectralfft.m					\
#Simulate.out

include $(lofar_sharedir)/Makefile.common
