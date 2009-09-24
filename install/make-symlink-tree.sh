#!/bin/bash

makedir()
{
  if [ -d $1 ]; then
    echo "$1 exists"
  else
    echo -n "Creating $1... "
    if ! mkdir $1; then
      exit 1;
    fi
    echo "OK"
  fi
}

ln-s()
{
  if [ "$2" == "" ]; then
    fn=${1##*/}
  else
    fn=$2
  fi
  if [ -h $fn ]; then
    echo "$fn exists, removing"
    rm -f $fn
  fi
  echo -n "Creating $fn... "
  if ! ln -s $1 $fn; then
    exit 1;
  fi
  echo "OK"
}


if [ "$1" == "" ]; then
  cat <<END
  $0: creates a tree of symlinks for Timba.
  Usage:
    $0 build_flavour
  will create a tree called symlinked-build_flavour.
END
  exit 1
fi

flavour=${1#symlinked-}

makedir symlinked-$flavour 
cd symlinked-$flavour
makedir bin
makedir lib
makedir libexec

cd bin
ln-s ../../../TimBase/src/gprof-run
ln-s ../../../PyApps/src/meqbrowser.py
ln -s meqbrowser.py meqbrowser
if [ -f ../../../build/$flavour/MeqServer/meqserver ]; then
  ln-s ../../../build/$flavour/MeqServer/meqserver
else
  echo "WARNING: meqserver binary not found"
fi
ln-s ../../../PyApps/src/tdlrun.py
ln-s ../../../PyApps/src/trut
ln-s ../../../PyApps/src/trutify
ln-s ../../../PyApps/src/trut.py
ln-s ../../../PyApps/src/Purr/purr.py
ln-s ../../../TimBase/src/gprof-run
ln-s ../../../build/$flavour/AppAgent/AppUtils/addbitflagcol


if [ -f meqserver-mpi ]; then
  echo "meqserver-mpi exists";
else
  cat <<END >meqserver-mpi
#!/bin/bash
source \$HOME/Timba/install/timba-init.sh 
timba-setup symlinked-$flavour
meqserver \$*
END
  chmod 755 meqserver-mpi
fi

cd ../lib
find ../../.. -name "*so" -o -name "*dylib"
for libname in `find ../../.. -name "*so" -o -name "*dylib" | grep -v svn-base | grep -v symlinked-$flavour | grep /$flavour/`; do
  ln-s $libname
done

cd ../libexec
ln-s ../../../build/$flavour/TimBase/src/gprof-helper.so
makedir python
cd python
#ln-s ../../../../FW/Meow
#ln-s ../../../../FW/Siamese
#ln-s ../../../../FW/Calico
#ln-s ../../../../FW/Ionosphere
ln-s ../../../../PyApps/src/Purr
ln-s ../../../../PyApps/src/meqbrowser.py
makedir Timba
cd Timba
ln-s ../../../../../PyApps/src/Apps
ln-s ../../../../../PyApps/src/Contrib
ln-s ../../../../../OCTOPython/src/version_info
ln-s ../../../../../OCTOPython/src/dmi.py
ln-s ../../../../../OCTOPython/src/dmi_repr.py
ln-s ../../../../../PyApps/src/Grid
ln-s ../../../../../PyApps/src/GUI
ln-s ../../../../../OCTOPython/src/__init__.py
ln-s ../../../../../PyApps/src/Meq
ln-s ../../../../../MeqServer/src/meqkernel.py
ln-s ../../../../../build/$flavour/PyApps/mequtils.dylib
ln-s ../../../../../build/$flavour/PyApps/mequtils.so
ln-s ../../../../../OCTOPython/src/octopussy.py
ln-s ../../../../../build/$flavour/OCTOPython/liboctopython.dylib octopython.dylib
ln-s ../../../../../build/$flavour/OCTOPython/liboctopython.so octopython.so
ln-s ../../../../../PyParmDB/src/ParmDB.py
ln-s ../../../../../build/$flavour/PyApps/libparmtables.dylib parmtables.dylib
ln-s ../../../../../build/$flavour/PyApps/libparmtables.so parmtables.so
ln-s ../../../../../PyApps/src/Plugins
ln-s ../../../../../PyApps/src/pretty_print.py
ln-s ../../../../../MeqServer/src/pynode.py
ln-s ../../../../../build/$flavour/PyParmDB/pyparmdb.dylib
ln-s ../../../../../build/$flavour/PyParmDB/pyparmdb.so
ln-s ../../../../../OCTOPython/src/qt_threading.py
ln-s ../../../../../PyApps/src/TDL
ln-s ../../../../../PyApps/src/Trees
ln-s ../../../../../PyApps/src/Trut
ln-s ../../../../../OCTOPython/src/utils.py
ln-s ../../../../../OCTOPython/src/array.py
cd ..
makedir icons
cd icons
ln-s ../../../../../PyApps/src/icons/treebrowser
ln-s ../../../../../PyApps/src/icons/purr
