#!/bin/bash

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

export DATE_STR=$(date +%Y%m%d)
export DAILY_DIR=$HOME/DAILY${DATE_STR}
export SVN_REPOSITORY="file:///var/svn/repos/trunk/Timba"
export CCACHE_PREFIX=distcc
export WEB_DIR="$HOME/public_html"

export DOCSUBDIR=pydoc
export GENERATEDOCSSCRIPT=$DAILY_DIR/Timba/Tools/Build/generate-docs.py


export PYTHONPATH=$DAILY_DIR/Timba/install/symlinked/libexec/python
export PATH=".:$HOME/usr/bin:/usr/local/bin:/usr/bin:/bin:/usr/X11R6/bin:$DAILY_DIR/Timba/install/symlinked/bin"
export LD_LIBRARY_PATH="$HOME/usr/lib:/aips++/rh7/pgplot:/usr/local/lib:/usr/lib:/lib:/usr/X11R6/lib"


source /aips++/prod/aipsinit.sh
#aipsinit gnu34


export TOTAL_TESTS=0
export FAILED_TESTS=0

export SERVER_START="MeqServer startup attempt: "


function Cleanup {
    rm -rf $DAILY_DIR && \
    mkdir $DAILY_DIR && \
    cd $DAILY_DIR
}





function GenerateDocs {
    DOCSOUTPUT=$1 && \
    pushd $DOCSOUTPUT && \
    python $GENERATEDOCSSCRIPT $DAILY_DIR/TIMBA/install/symlinked/libexec/python/Timba && \
    ln -s Timba.html index.html && \
    popd
}





function Checkout {
    cd $DAILY_DIR && \
    svn checkout $SVN_REPOSITORY && \
    ln -s $DAILY_DIR/Timba/install/symlinked $DAILY_DIR/Timba/install/current
}





function BuildVariant {
   variant=$1 && \
   \
   pushd $DAILY_DIR/Timba && \
   ./bootstrap && \
   cd $DAILY_DIR/Timba/build/$variant &&\
   ../../lofarconf --with-old-lsqfit && \
   make -j 24 && \
   popd
}






function FilterWarnings {
   Filename=$1 && \
   grep -i warning $Filename |\
   grep -v "underquoted definition"|\
   grep -v "mt_allocator.h"|\
   grep -v -e "pyconfig\.h.*_POSIX_C_SOURCE"|\
   grep -v -e "/usr/include/features\.h.*this is the location of the "|\
   grep -v -e "ThreadCond\.cc:132:.* missing initializer for member"|\
   grep -v -e "ThreadCond\.cc:174:.* missing initializer for member"|\
   grep -v -e "ProxyWPObject\.cc:371:.* missing initializer for member"|\
   grep -v -e "ProxyWPObject\.cc:413:.* missing initializer for member"|\
   grep -v -e "^\*\*\*"|\
   grep -v "configure: WARNING: compiler ccache .* mismatches build"|\
   grep -v "configure: WARNING: ccache .* is an unknown compiler"|\
   grep -v -e "^distcc.*Warning: failed to distribute"
}







function FilterErrors {
   filename=$1 && \
   grep -i error $filename|\
   grep -v -e "^distcc.*(dcc_writex) ERROR: failed to write:"|\
   grep -v -e "^distcc.*(dcc_select_for_read) ERROR: IO timeout"|\
   grep -v -e "^distcc.*(dcc_r_token_int) ERROR: read failed while waiting for token \"DONE\""
}

  





function LineCount {
   wc $1|sed -e"s/[ ]*\([0-9]*\) .*/\1/"
}






function BuildAndFilter {
   variant=$1 && \
   logfile=$DAILY_DIR/${variant}.log && \
   warningfile=$DAILY_DIR/${variant}.warnings && \
   errorfile=$DAILY_DIR/${variant}.errors && \
   echo Building $variant && \
   \
   BuildVariant   $variant  &> $logfile
   FilterWarnings $logfile  &> $warningfile
   FilterErrors   $logfile  &> $errorfile
}


function ReportVariant {
   variant=$1 && \
   \
   warningfile=$DAILY_DIR/$variant.warnings && \
   errorfile=$DAILY_DIR/$variant.errors && \
   echo Variant $variant has `LineCount $errorfile` errors and `LineCount $warningfile` warnings "(<a href=\"${variant}.log\">full log</a>)"
}





function PrintErrorsWarnings {
    echo Errors $1:
    echo -----------------------------------------------------
    cat $DAILY_DIR/$1.errors
    echo -----------------------------------------------------
    echo
    echo Warnings $1:
    echo -----------------------------------------------------
    cat $DAILY_DIR/$1.warnings
    echo -----------------------------------------------------
}



function InitializeTesting {
   TOTAL_TESTS=0
   FAILED_TESTS=0
}





function RunAssayScript {
   assayscript=$1
   logfile=$2
   python $assayscript -assayrecord -opt -dassayer=2 -- -mt 2>&1 >> $logfile&
   pythonpid=$!
   meqserverpid=`ps --ppid $pythonpid | grep meqserver|awk '{print $1}'`
}







function ExecuteTest {
   testname=$1
   if $testname; then 
       echo "$testname: PASS";
       ((TOTAL_TESTS++));
   else
       echo "$testname: FAILED";
       ((TOTAL_TESTS++));
       ((FAILED_TESTS++));
   fi
}



function PrintTestResults {
   if test $FAILED_TESTS == 0; then
       echo "All $TOTAL_TESTS PASSED";
   else
       echo "$FAILED_TESTS / $TOTAL_TESTS FAILED";
   fi
}



function CheckStartupOfMeqServer {
   variant=$1
   servername=$DAILY_DIR/Timba/MeqServer/build/$variant/src/meqserver
   echo Starting $servername
   $servername &> $DAILY_DIR/meqserver.$variant.log&
   serverpid=$!
   echo PID=$serverpid
   sleep 20
   if test $(ps -o cmd= $serverpid|wc|sed -e"s/[ ]*\([0-9]*\) .*/\1/") == 0; then
       echo $variant: meqserver FAILED to start;
       SERVER_START="$SERVER_START $variant: FAILED"
   else
       echo $variant: meqserver still running after 20 s;
       kill $serverpid
       SERVER_START="$SERVER_START $variant: SUCCESS"
   fi
   
}





function HTMLReportFrontmatter {
   filename=$1
   
   echo '<?xml version="1.0" encoding="ISO-8859-1"?>' > $filename
   echo '<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"' >>$filename
   echo '\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">' >> $filename
   echo '<html>'      >> $filename
   echo '    <head>'  >>$filename
   echo '    <title>MeqTree daily build</title>' >>$filename
   echo '    <style>' >> $filename
   echo '    strong{text-style:bold;}'>>$filename
   echo '    strong.success{color:green;}'>>$filename    
   echo '    strong.failure{color:red;}'>>$filename    
   echo '    </style>'>> $filename 
   echo '    </head>' >> $filename
   echo '    <body>'  >> $filename
   echo "        <h1>MeqTree daily build ${DATE_STR}</h1>" >> $filename
}




function HTMLReportMainmatter {
   filename=$1

   
   echo '<p>'>>$filename
   ReportVariant gnu3_debug >>$filename
   echo '</p>'>>$filename
   echo '<p>'>>$filename
   ReportVariant gnu3_opt >>$filename  
   echo '</p>'>>$filename
   echo '<p>'>>$filename
   echo $SERVER_START|sed -e"s/FAILED/<strong class=\"failure\">FAILED<\/strong>/g"|sed -e"s/SUCCESS/<strong class=\"success\">SUCCESS<\/strong>/g">>$filename
   echo '</p>'>>$filename
   echo '<br/>'>>$filename
   echo '<br/>'>>$filename
   echo '<br/>'>>$filename
   echo '<p>'>>$filename
   echo '<a href="pydoc">Fresh PYDOC documentation</a>' >>$filename
   echo '</p>'>>$filename
   
   echo '<pre>'>>$filename
   PrintErrorsWarnings gnu3_debug>>$filename
   echo '</pre>'>>$filename
   
   echo '<pre>'>>$filename
   PrintErrorsWarnings gnu3_opt>>$filename
   echo '</pre>'>>$filename
}



function HTMLReportBackmatter {
   filename=$1
   echo '    </body>' >> $filename
   echo '</html>'     >> $filename
        
}


function HTMLReport {
    HTMLReportFrontmatter $1
    HTMLReportMainmatter  $1
    HTMLReportBackmatter  $1
}



# Main program
echo
echo \*\*\*  Full checkout and build of MeqTree: `date`  \*\*\*
echo 'http://lofar9.astron.nl/~brentjens/index.html'
echo
echo Cleanup...
Cleanup
echo Checkout...
Checkout      &> $DAILY_DIR/checkout.log
echo
BuildAndFilter gnu3_debug
CheckStartupOfMeqServer gnu3_debug
ReportVariant gnu3_debug
echo
BuildAndFilter gnu3_opt
CheckStartupOfMeqServer gnu3_opt
ReportVariant gnu3_opt
echo
echo Done: `date`


echo
echo
echo
PrintErrorsWarnings gnu3_opt
echo 
echo
echo
PrintErrorsWarnings gnu3_debug

# For the daily build archive
HTMLReport $DAILY_DIR/index.html

# The main report
cp $DAILY_DIR/gnu3_debug.log  $DAILY_DIR/gnu3_opt.log $WEB_DIR
HTMLReport $WEB_DIR/index.html

# For the web archive
mkdir $WEB_DIR/$DATE_STR
cp $DAILY_DIR/gnu3_debug.log  $DAILY_DIR/gnu3_opt.log $WEB_DIR/$DATE_STR
HTMLReport $WEB_DIR/$DATE_STR/index.html

mkdir -p "${WEB_DIR}/${DOCSUBDIR}"
GenerateDocs "${WEB_DIR}/${DOCSUBDIR}"

mkdir -p "${WEB_DIR}/${DATE_STR}/${DOCSUBDIR}"
GenerateDocs "${WEB_DIR}/${DATE_STR}/${DOCSUBDIR}"
