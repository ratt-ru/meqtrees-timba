SUBDIRS	= .

LOCALHDRS = 

LOCALSRCS = \
    Constant.cc Parm.cc Freq.cc Time.cc Selector.cc Composer.cc Add.cc \
    Subtract.cc Multiply.cc Divide.cc  Sin.cc Cos.cc Exp.cc Pow.cc Sqr.cc \
    Sqrt.cc Conj.cc ToComplex.cc  UVW.cc LMN.cc StatPointSourceDFT.cc \
    PointSourceDFT.cc  ModRes.cc Condeq.cc Solver.cc ZeroFlagger.cc \
    MergeFlags.cc Resampler.cc ReqSeq.cc  \
    ParmTable.cc 

DOCHDRS		= $(LOCALHDRS) \
            $(addsuffix .h,$(basename $(LOCALSRCS))) 

lib_LTLIBRARIES 	= libmeqnodes.la

libmeqnodes_la_SOURCES 	= $(DOCHDRS) $(LOCALSRCS) \
  AID-MeqNodes-Registry.cc

check_PROGRAMS = 

# this defines the name of the local defrec script
DEFREC_MAP = $(srcdir)/defrecs_$(PACKAGE).g

# this rule shouldn't require any changes
MAKEDEFREC = $(lofar_sharedir)/../CEP/CPA/PSS4/MEQ/src/makedefrecs.pl
$(DEFREC_MAP): $(DOCHDRS) $(MAKEDEFREC)
	$(MAKEDEFREC) $@ $(addprefix $(srcdir)/,$(DOCHDRS))
# ---------
  
# place scripts into libexec/glish/meq
glishdir = $(libexecdir)/glish/meq
dist_glish_SCRIPTS = $(DEFREC_MAP) meptable.g

defrecs: $(DEFREC_MAP)

all install: defrecs

.PHONY: defrecs

# --- end generate defrec maps

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids
