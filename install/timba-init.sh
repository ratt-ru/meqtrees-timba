# timba-init.sh
# source this file into your .bashrc to have all Timba paths set up at login


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
  for f in $TIMBA_PATH/install/$pattern/bin; do
    if [ -d $f ]; then
      f=${f%/bin}
      f=${f##*/}
      _tvers="$_tvers $f"
    fi
  done
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
  if [ "$PRE_TIMBA_PATH" == "" ]; then
    export PRE_TIMBA_PATH=$PATH
  fi
  if [ "$PRE_TIMBA_LD_LIBRARY_PATH" == "" ]; then
    export PRE_TIMBA_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
  fi
  if [ "$PRE_TIMBA_PYTHONPATH" == "" ]; then
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
    versions="`valid-timba-versions $1`"
    if [ -z "$versions" ]; then
      echo "No MeqTree version matching $TIMBA_PATH/install/*$1* found" 
      echo "You need to re-run timba-setup <version>"
      echo -n "where version is one of: "
      valid-timba-versions
      echo ""
    elif [ "$versions" != "${versions% *}" ]; then
      echo "Multiple MeqTree versions matching $TIMBA_PATH/install/*$1* found" 
      echo "You need to re-run timba-setup <version>"
      echo "where version is one of: $versions"
    else
      export PATH=$TIMBA_PATH/install/$versions/bin:$PRE_TIMBA_PATH
      export PYTHONPATH=$TIMBA_PATH/install/$versions/libexec/python:.:$PRE_TIMBA_PYTHONPATH
      export LD_LIBRARY_PATH=$TIMBA_PATH/install/$versions/lib:$PRE_TIMBA_LD_LIBRARY_PATH
      echo "Using MeqTree version $TIMBA_PATH/install/$versions"
      export TIMBA_CURRENT_VERSION="$versions"
    fi
  }
  _timba-setup() 
  { 
    timba-setup $*
  }

  timba-setup current
fi
