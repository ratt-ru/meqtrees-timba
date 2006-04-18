#gnu3.compiler.conf: CXX=ccache\ g++-3.4 --with-cppflags="-m32 -msse -m3dnow -msse2 -Wno-deprecated -Wa,--32" --with-threads --with-sse --with-ldflags="--enable-new-dtags"
#gnu3.compiler.aipspp.var: --with-aipspp=/aips++/prod/linux_gnu

#gnu3.compiler.conf: CXX=ccache\ /usr/local/gcc-3.4.3/bin/g++ --with-cppflags="-m32 -msse -m3dnow -msse2 -Wno-deprecated -Wa,--32" --with-threads --with-sse --with-ldflags="--enable-new-dtags"
#gnu3.compiler.aipspp.var: --with-aipspp=/aips++/prod/linux_gnu

# gnu3f: builds w/o -fPIC. This doesn't work for shared libraries, so only useful for testing
gnu3f.compiler.conf: CXX=ccache\ g++-3.4 --with-cppflags="-march=k8 -m64 -Wno-deprecated -Wno-unused-parameter -DAIPS_64B" --with-ldflags="-rpath /lib64"--with-threads --with-sse --with-ldflags="--enable-new-dtags"
gnu3f.compiler.aipspp.var: --with-aipspp=/aips++/amd64/linux_gnu_x86_64

# gnu3 build with -fPIC 
gnu3.compiler.conf: CXX=ccache\ g++-3.4 --with-cppflags="-march=k8 -m64 -Wno-deprecated -Wno-unused-parameter -fPIC -DAIPS_64B" --with-ldflags="-rpath /lib64"--with-threads --with-sse --with-ldflags="--enable-new-dtags"
gnu3.compiler.aipspp.var: --with-aipspp=/aips++/amd64/linux_gnu

sse.var: --with-sse

optimize.var:	--with-optimize='-O4'
debugopt.var:	--with-debug='-ggdb -O4'
profiler.var: 	--with-debug='-ggdb -pg'
profopt.var: 	--with-optimize='-O4 -pg'

debugopt.variant.conf: 	$(standard) $(debugopt)
profopt.variant.conf: 	$(standard) $(profopt)
prof.variant.conf: 	$(standard) $(profiler)

# debug.variant.conf: $(standard) --with-optimize='-ggdb -DDMI_USE_MALLOC_ALLOC'

