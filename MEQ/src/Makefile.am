SUBDIRS	= .

DOCHDRS		 	= 			\
Domain.h					\
Cells.h Result.h ResultSet.h Polc.h \
Node.h Function.h Function1.h Function2.h \
Parm.h Freq.h Time.h Selector.h Composer.h \
Add.h Subtract.h Multiply.h Divide.h \
Sin.h Cos.h Exp.h Pow.h Sqr.h Sqrt.h Conj.h ToComplex.h \
UVW.h \
Vells.h VellsTmp.h VellsRep.h \
VellsRealSca.h VellsRealArr.h \
VellsComplexSca.h VellsComplexArr.h \
Request.h \
Forest.h \
ParmTable.h

lib_LTLIBRARIES 	= libmeq.la

libmeq_la_SOURCES 	= $(DOCHDRS)		\
Domain.cc	Cells.cc Result.cc ResultSet.cc \
Polc.cc \
Node.cc Function.cc Function1.cc Function2.cc \
Parm.cc Freq.cc Time.cc Selector.cc Composer.cc \
Add.cc Subtract.cc Multiply.cc Divide.cc \
Sin.cc Cos.cc Exp.cc Pow.cc Sqr.cc Sqrt.cc Conj.cc ToComplex.cc \
UVW.cc \
Vells.cc VellsTmp.cc VellsRep.cc \
VellsRealSca.cc VellsRealArr.cc \
VellsComplexSca.cc VellsComplexArr.cc \
Request.cc \
Forest.cc \
ParmTable.cc \
AID-Meq-Registry.cc


bin_PROGRAMS = uvwparm

uvwparm_SOURCES	 	= uvwparm.cc 
uvwparm_LDADD		= ../src/libmeq.la 
uvwparm_DEPENDENCIES	= ../src/libmeq.la $(LOFAR_DEPEND)

#EXTRA_DIST		=			\
#Beam.m						\
#spectralfft.m					\
#Simulate.out

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids
