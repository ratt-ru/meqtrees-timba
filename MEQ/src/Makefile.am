SUBDIRS	= .

LOCALHDRS = MeqVocabulary.h RequestId.h 

LOCALSRCS = \
  Domain.cc	Cells.cc Vells.cc VellSet.cc Result.cc \
  ResampleMachine.cc Request.cc RequestId.cc EventGenerator.cc \
  Node.cc Function.cc CompoundFunction.cc Polc.cc Forest.cc 

DOCHDRS		= $(LOCALHDRS) \
            $(addsuffix .h,$(basename $(LOCALSRCS))) 
  
lib_LTLIBRARIES 	= libmeq.la

libmeq_la_SOURCES 	= $(DOCHDRS) $(LOCALSRCS) \
  Node_Riders.cc AID-Meq-Registry.cc

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
dist_glish_SCRIPTS = $(DEFREC_MAP) meqtypes.g

defrecs: $(DEFREC_MAP)

all install: defrecs

.PHONY: defrecs

# --- end generate defrec maps

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids
