# Get LOFAR root directory from this script's name.
a_dir=`dirname $0`
a_dir=`cd $a_dir; pwd`
a_root=`echo $a_dir | sed -e 's%/LOFAR/.*%/LOFAR%'`
echo "Executing finddep ..."

# Find out where pkgdep is located.
$a_root/autoconf_share/finddep
if [ -f $a_dir/pkgdep ]; then
  a_pkgdep=$a_dir/pkgdep
else
  a_pkgdep=$a_root/LCS/Common/build/gnu_debug/src/pkgdep
fi
echo "Executing pkgdep ..."
$a_pkgdep finddep.pkg top strip xhtml hdrtxt="%pkg% Package Directory Tree" href='<a href="makepage.php?name=%pkg%" target="description">' > finddep-pkg.html
$a_pkgdep finddep.used xhtml > finddep-used.html
$a_pkgdep finddep.uses xhtml > finddep-uses.html
$a_pkgdep finddep.used-all xhtml hdrtxt="%pkg% Cross Reference Tree<br>(shows in a recursive way the packages where %pkg% is used)" split=".used.html" 
$a_pkgdep finddep.uses-all xhtml hdrtxt="%pkg% Uses Dependency Tree<br>(shows in a recursive way the packages used by %pkg%)" split=".uses.html" 
$a_pkgdep finddep.uses-all xhtml flat hdrtxt="%pkg% Flat Dependency Tree<br>(shows the packages used by %pkg%)" split=".flat.html" 
