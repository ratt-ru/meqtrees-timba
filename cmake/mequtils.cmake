# target etags/tags
IF (UNIX)
    ADD_CUSTOM_TARGET(tags etags --members --declarations  `find . -name 
        *.cc -or -name *.hh -or -name *.cpp -or -name *.h -or -name *.c -or 
        -name *.f`)
    ADD_CUSTOM_TARGET(etags DEPENDS tags)
ENDIF (UNIX)
