INCLUDE_DIRECTORIES(${CASACORE_INCLUDE_DIR}/casacore)
MEQPACKAGE( DMI TimBase )
set(dmi_includes
    src/AID-DMI.h
    src/AIPSPP-Hooks.h
    src/Allocators.h
    src/AtomicID.h
    src/BlockSet.h
    src/BObj.h
    src/BOIO.h
    src/ConfigMgr.h
    src/Container.h
    src/ContainerIter.h
    src/CountedRefBase.h
    src/CountedRef.h
    src/CountedRefTarget.h
    src/CountedRefTraits.h
    src/DMI.h
    src/DynamicTypeManager.h
    src/Events.h
    src/Exception.h
    src/Global-Registry.h
    src/HashMap.h
    src/HIID.h
    src/HIIDSet.h
    src/List.h
    src/NC-ConstHooks.h
    src/NC-Hooks.h
    src/NC-Hooks-Templ.h
    src/NumArrayFuncs.h
    src/NumArray.h
    src/ObjectAssignerMacros.h
    src/Packer.h
    src/Record.h
    src/Registry.h
    src/SmartBlock.h
    src/TID-DMI.h
    src/Timestamp.h
    src/TypeId.h
    src/TypeInfo.h
    src/TypeIter-DMI.h
    src/TypeIterMacros.h
    src/Vec.h
)
INCLUDE_SETUP(DMI ${dmi_includes})
set(dmi_loki_includes
    src/Loki/NullType.h
    src/Loki/Typelist.h
    src/Loki/TypeManip.h
    src/Loki/TypeTraits.h
   )
INCLUDE_SETUP(DMI/Loki ${dmi_loki_includes})

set(src 
        src/AID-DMI-Registry.cc
        src/AID-Global-Registry.cc
        src/AtomicID.cc
        src/BlockSet.cc
        src/BObj.cc
        src/BOIO.cc
        src/ConfigMgr.cc
        src/Container.cc
        src/CountedRefBase.cc
        src/CountedRefTarget.cc
        src/DMI.cc
        src/DynamicTypeManager.cc
        src/Exception.cc
        src/HIID.cc
        #        src/HIIDSet.cc
        src/List.cc
        src/NumArray.cc
        src/NumArrayFuncs2.cc
        src/NumArrayFuncs3.cc
        src/NumArrayFuncs4.cc
        src/NumArrayFuncs5.cc
        src/NumArrayFuncs6.cc
        src/NumArrayFuncs7.cc
        src/NumArrayFuncs8.cc
        src/NumArrayFuncs.cc
        src/Record.cc
        src/Registry.cc
        src/SmartBlock.cc
        src/Timestamp.cc
        src/TypeInfo.cc
        src/Vec.cc
)

add_library(dmi ${src})
install(TARGETS dmi DESTINATION ${LIBRARY_INSTALL_DIR})
MEQPACKAGE_ADD_LIBRARIES(dmi ${CASACORE_LIBRARIES})
