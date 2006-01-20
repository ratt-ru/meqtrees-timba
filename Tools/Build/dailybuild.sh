#!/bin/bash

export DATE_STR=$(date +%Y%m%d)
export DAILY_DIR=$HOME/DAILY${DATE_STR}
export CVSROOT=:pserver:brentjens@cvs:/cvs/cvsroot
export CCACHE_PREFIX=distcc
export WEB_DIR="$HOME/public_html"


export PYTHONPATH=$DAILY_DIR/LOFAR/installed/current/libexec/python
export PATH=".:$HOME/usr/bin:/usr/local/bin:/usr/bin:/bin:/usr/X11R6/bin:$DAILY_DIR/LOFAR/installed/current/bin"
export LD_LIBRARY_PATH="$HOME/usr/lib:/aips++/rh7/pgplot:/usr/local/lib:/usr/lib:/lib:/usr/X11R6/lib"


source /aips++/sys1/aipsinit.sh
aipsinit gnu


export TOTAL_TESTS=0
export FAILED_TESTS=0

export SERVER_START="MeqServer startup attempt: "


function Cleanup {
    rm -rf $DAILY_DIR && \
    mkdir $DAILY_DIR && \
    cd $DAILY_DIR
}





function Checkout {

    cvs co LOFAR/autoconf_share && \
    cvs co LOFAR/LCS/Common && \
    cvs co LOFAR/Timba && \
    \
    mkdir LOFAR/installed && \
    cd $DAILY_DIR/LOFAR/installed && \
    tar xvzf ../Timba/install-symlinked.tgz && \
    ln -s symlinked current && \
    \
    mkdir -p $DAILY_DIR/LOFAR/LCS/Common/build
}






function BuildVariant {
   variant=$1 && \
   \
   cd $DAILY_DIR/LOFAR/LCS/Common && \
   ./bootstrap && \
   mkdir -p $DAILY_DIR/LOFAR/LCS/Common/build/$variant && \
   cd $DAILY_DIR/LOFAR/LCS/Common/build/$variant && \
   ../../lofarconf && \
   \
   \
   cd $DAILY_DIR/LOFAR/Timba && \
   ./bootstrap && \
   mkdir -p $DAILY_DIR/LOFAR/Timba/build/$variant && \
   cd $DAILY_DIR/LOFAR/Timba/build/$variant && \
   ../../lofarconf && \
   make -j 24
}






function FilterWarnings {
   Filename=$1 && \
   grep -i warning $Filename |\
   grep -v "underquoted definition"|\
   grep -v "mt_allocator.h"|\
   grep -v -e "pyconfig\.h.*_POSIX_C_SOURCE"|\
   grep -v -e "/usr/include/features\.h.*this is the location of the "|\
   grep -v -e "^\*\*\*"|grep -v "configure: WARNING: compiler ccache .* mismatches build"|\
   grep -v "configure: WARNING: ccache .* is an unknown compiler"
}







function FilterErrors {
   filename=$1 && \
   grep -i error $filename
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
   BuildVariant   $variant  &> $logfile && \
   FilterWarnings $logfile  &> $warningfile && \
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
   servername=$DAILY_DIR/LOFAR/Timba/MeqServer/build/$variant/src/meqserver
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
echo 'http://lofar9.astron.nl/~brentjens/index.html'
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
