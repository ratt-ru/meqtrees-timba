SUBDIRS	= .

LOCALHDRS = MeqVocabulary.h RequestId.h 

LOCALSRCS = \
  Axis.cc Domain.cc	Cells.cc Request.cc RequestId.cc \
  Vells.cc VellSet.cc Result.cc \
  Node.cc Function.cc CompoundFunction.cc \
  Funklet.cc Polc.cc EventGenerator.cc Forest.cc 

## removed for now, as it needs to be re-worked for the new Vells
## structure
# ResampleMachine.cc 

DOCHDRS		= $(LOCALHDRS) \
            $(addsuffix .h,$(basename $(LOCALSRCS))) 

lib_LTLIBRARIES 	= libmeq.la

libmeq_la_SOURCES 	= $(DOCHDRS) $(LOCALSRCS) \
  Node_Riders.cc AID-Meq-Registry.cc

check_PROGRAMS = 

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

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
