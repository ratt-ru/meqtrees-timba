CXXFLAGS += -D_GNU_SOURCE 

check_PROGRAMS		= IMTest glish_reflector

bin_PROGRAMS   		= 

AIDHDRS = IMTestWP.h

# test_glish_SOURCES 	= test_glish.cc EchoWP.cc AID-Testing-Registry.cc
#
# test_glish_LDADD		= ../src/Glish/liboctopussy-glish.la \
#  ../src/liboctopussy.la -lglish -lsos -lnpd
#
# test_glish_DEPENDENCIES	= ../src/liboctopussy.la $(LOFAR_DEPEND)

IMTest_SOURCES		= IMTestWP.h IMTestWP.cc IMTest.cc 
IMTest_LDADD		  = ../src/liboctoglish.la -lglish -lsos -lnpd
IMTest_DEPENDENCIES	= ../src/liboctoglish.la $(LOFAR_DEPEND)

glish_reflector_SOURCES		    = glish_reflector.cc
glish_reflector_LDADD		      = ../src/liboctoglish.la -lglish -lsos -lnpd
glish_reflector_DEPENDENCIES	= ../src/liboctoglish.la $(LOFAR_DEPEND)

TESTS				=  

EXTRA_DIST			=

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
