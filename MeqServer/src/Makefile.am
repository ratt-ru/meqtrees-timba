dmi_dir = $(lofar_sharedir)/../DMI

lib_LTLIBRARIES = libmeqserver.la

DOCHDRS = MeqServer.h VisDataMux.h VisHandlerNode.h Sink.h Spigot.h

libmeqserver_la_SOURCES = \
  AID-MeqServer-Registry.cc \
  MeqServer.cc \
  VisDataMux.cc \
  VisHandlerNode.cc \
  Sink.cc Spigot.cc
  
bin_PROGRAMS   		= meqserver
  
meqserver_SOURCES		    = meqserver.cc
meqserver_LDADD		      = libmeqserver.la 
# -lglish -lsos -lnpd
meqserver_DEPENDENCIES	= libmeqserver.la $(LOFAR_DEPEND)


# --- begin generate defrec maps (copy this into local Makefiles)
#     (shouldn't require any changes)

# this defines the name of the local defrec script
DEFREC_MAP = $(srcdir)/defrecs_$(PACKAGE).g

# this rule shouldn't require any changes
MAKEDEFREC = $(lofar_sharedir)/../CEP/CPA/PSS4/MEQ/src/makedefrecs.pl
$(DEFREC_MAP): $(DOCHDRS) $(MAKEDEFREC)
	$(MAKEDEFREC) $@ $(addprefix $(srcdir)/,$(DOCHDRS))
  
defrecs: $(DEFREC_MAP)

all install: defrecs

.PHONY: defrecs

# --- end generate defrec maps

# more glish scripts here
glishdir = $(libexecdir)/glish/meq
dist_glish_SCRIPTS = $(DEFREC_MAP) meqserver.g defrecs.g \
  meptools.g msuvw_to_mep.g fitpolcs_mqs.g fitpolcs_wlc.g 

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

