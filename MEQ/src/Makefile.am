SUBDIRS	= .

DOCHDRS		 	= MeqVocabulary.h RequestId.h \
Domain.h Cells.h Vells.h VellSet.h Result.h Polc.h \
Node.h Function.h Function1.h Function2.h \
Constant.h Parm.h Freq.h Time.h Selector.h Composer.h \
Add.h Subtract.h Multiply.h Divide.h \
Sin.h Cos.h Exp.h Pow.h Sqr.h Sqrt.h Conj.h ToComplex.h \
UVW.h Request.h \
Condeq.h Solver.h \
Forest.h ParmTable.h

lib_LTLIBRARIES 	= libmeq.la

libmeq_la_SOURCES 	= $(DOCHDRS)		\
Domain.cc	Cells.cc Vells.cc VellSet.cc Result.cc Polc.cc \
RequestId.cc Node.cc Function.cc Function1.cc Function2.cc \
Constant.cc Parm.cc Freq.cc Time.cc Selector.cc Composer.cc \
Add.cc Subtract.cc Multiply.cc Divide.cc \
Sin.cc Cos.cc Exp.cc Pow.cc Sqr.cc Sqrt.cc Conj.cc ToComplex.cc \
UVW.cc Request.cc \
Condeq.cc Solver.cc \
Forest.cc ParmTable.cc \
AID-Meq-Registry.cc


check_PROGRAMS = 
# uvwparm

# uvwparm_SOURCES	 	= uvwparm.cc 
# uvwparm_LDADD		= libmeq.la 
# uvwparm_DEPENDENCIES	= libmeq.la $(LOFAR_DEPEND)

# --- begin generate defrec maps (copy this into local Makefiles)
#     (shouldn't require any changes)

# this defines the name of the local defrec script
DEFREC_MAP = $(srcdir)/defrecs_$(PACKAGE).g

# this rule shouldn't require any changes
MAKEDEFREC = $(lofar_sharedir)/../CEP/CPA/PSS4/MEQ/src/makedefrecs.pl
$(DEFREC_MAP): $(DOCHDRS) $(MAKEDEFREC)
	$(MAKEDEFREC) $@ $(addprefix $(srcdir)/,$(DOCHDRS))
# ---------
  
# place scripts into libexec/glish/meq
glishdir = $(libexecdir)/glish/meq
dist_glish_SCRIPTS = $(DEFREC_MAP) parmtable.g

defrecs: $(DEFREC_MAP)

all install: defrecs

.PHONY: defrecs

# --- end generate defrec maps

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids
