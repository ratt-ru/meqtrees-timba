#!/bin/bash
# timba-init.sh
# source this file into your .bashrc to have all Timba paths set up at login

echo "TIMBA PATH SET TO '$TIMBA_PATH'"
if [ -z "$TIMBA_PATH" ]; then
  # under bash, we can figure out the name of our script, and extract the path
  if [ "$BASH_SOURCE" != "" ]; then
    if [ "${BASH_SOURCE[0]/Timba\//}" != "${BASH_SOURCE[0]}" ]; then
      export TIMBA_PATH="${BASH_SOURCE[0]/Timba\/*/Timba}"
      # if we end up with a relative path, make it absolute
      if [ "${TIMBA_PATH#/}" = "$TIMBA_PATH" ]; then
        export TIMBA_PATH=`pwd`/$TIMBA_PATH
      fi
    fi
  fi
  if [ -z "$TIMBA_PATH" ]; then
    export TIMBA_PATH=$HOME/Timba
  fi
  echo "Using \$TIMBA_PATH $TIMBA_PATH"
fi

valid-timba-versions()
{
  _tvers=""
  if [ -z $1 ]; then
    pattern="*";
  else
    pattern="*$1*"
  fi
  paths=$TIMBA_PATH/install/$pattern/bin
  for f in $paths; do
    if [ -d $f ]; then
      f=${f%/bin}
      f=${f##*/}
      _tvers="$_tvers $f"
    fi
  done
  _tvers=${_tvers# }
  echo -n $_tvers
}

timba_versions=`valid-timba-versions`

if [ ! -d $TIMBA_PATH/install ]; then
  echo "Warning: cannot find a MeqTree install under $TIMBA_PATH"
  echo "If MeqTrees are installed elsewhere, please set your TIMBA_PATH variable appropriately."
elif [ -z "$timba_versions" ]; then
  echo "Warning: cannot find any MeqTree versions in $TIMBA_PATH/install"
  echo "If MeqTrees are installed elsewhere, please set your TIMBA_PATH variable appropriately."
else
  echo "Available MeqTree versions: $timba_versions";
  if [ "$PRE_TIMBA_PATH" = "" ]; then
    export PRE_TIMBA_PATH=$PATH
  fi
  if [ "$PRE_TIMBA_LD_LIBRARY_PATH" = "" ]; then
    export PRE_TIMBA_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
  fi
  if [ "$PRE_TIMBA_PYTHONPATH" = "" ]; then
    export PRE_TIMBA_PYTHONPATH=$PYTHONPATH
  fi

  timba-setup()
  {
    if [ -z $1 ]; then
      echo "timba-setup: sets up paths, etc. for running MeqTrees"
      echo "Usage: timba-setup <version>"
      echo -n "where version is one of: "
      valid-timba-versions
      return
    fi
    # find versions matching $1 pattern
    versions="`valid-timba-versions $1`"
    # none found: return
    if [ -z "$versions" ]; then
      echo "No MeqTree version matching $TIMBA_PATH/install/*$1* found"
      echo "You need to re-run timba-setup <version>"
      echo -n "where version is one of: "
      valid-timba-versions
      echo ""
      return
    fi
    # single version found: use that
    if [ "$versions" = "${versions% *}" ]; then
      version=$versions
    # else multiple versions found. Check for an exact match
    else
      unset version
      for v in $versions; do
        if [ "$v" = "$1" -o "${v#*-}" = "$1" ]; then
          version=$v
          break
        fi
      done
      if [ -z "$version" ]; then
        echo "Multiple MeqTree versions matching $TIMBA_PATH/install/*$1* found"
        echo "You need to re-run timba-setup <version>"
        echo "where version is one of: $versions"
        return
      fi
    fi
    export PATH=$TIMBA_PATH/install/$version/bin:$PRE_TIMBA_PATH
    export PYTHONPATH=$CATTERYPATH:~/Purr:$TIMBA_PATH/install/$version/libexec/python:.:$PRE_TIMBA_PYTHONPATH
#    if [ "${version%debug}" != "$version" ]; then
#      export LD_LIBRARY_PATH=/usr/lib/debug:$TIMBA_PATH/install/$version/lib:$PRE_TIMBA_LD_LIBRARY_PATH
#    else
      export LD_LIBRARY_PATH=$TIMBA_PATH/install/$version/lib:$PRE_TIMBA_LD_LIBRARY_PATH
#    fi
    echo "Using MeqTree version $TIMBA_PATH/install/$version"
    export TIMBA_CURRENT_VERSION="$version"
  }
  _timba-setup()
  {
    timba-setup $*
  }
  versions="`valid-timba-versions current`"
  if [ "$versions" != "" ]; then
    timba-setup current
  else
    echo "Please use 'timba-setup <version>' to set up paths for a MeqTree version"
  fi
fi
