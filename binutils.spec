# Binutils SPEC file.  Can be invoked with the following parameters:

# --define "binutils_target arm-linux-gnu" to create arm-linux-gnu-binutils.
# --with=bootstrap: Build with minimal dependencies.
# --with=debug: Build without optimizations and without splitting the debuginfo.
# --without=docs: Skip building documentation.
# --without=testsuite: Do not run the testsuite.  Default is to run it.
# --with=testsuite: Run the testsuite.  Default when --with=debug is not to run it.

#---Start of Configure Options-----------------------------------------------

# Do not create deterministic archives by default  (cf: BZ 1195883)
%define enable_deterministic_archives 0

# Enable support for GCC LTO compilation.
%define enable_lto 1

# Disable the default generation of compressed debug sections.
%define default_compress_debug 0

# Default to read-only-relocations (relro) in shared binaries.
%define default_relro 1 

#----End of Configure Options------------------------------------------------

# Default: Not bootstrapping.
%bcond_without bootstrap
# Default: Not debug
%bcond_without debug
# Default: Always build documentation.
%bcond_with docs
# Default: Always run the testsuite.
%bcond_with testsuite

%if %{with bootstrap}
%undefine with_docs
%undefine with_testsuite
%endif

%if %{with debug}
%undefine with_testsuite
%endif

%if 0%{!?binutils_target:1}
%define binutils_target %{_target_platform}
%define isnative 1
%define enable_shared 1
%else
%define cross %{binutils_target}-
%define isnative 0
%define enable_shared 0
%endif

# The opcodes library needs a few functions defined in the bfd
# library, but these symbols are not defined in the stub bfd .so
# that is available at link time.  (They are present in the real
# .so that is used at run time).
%undefine _strict_symbol_defs_build

#----------------------------------------------------------------------------

Summary: A GNU collection of binary utilities
Name: %{?cross}binutils%{?_with_debug:-debug}
Version: 2.30
Release: 12%{?dist}
License: GPLv3+
Group: Development/Tools
URL: https://sourceware.org/binutils

# Note - the Linux Kernel binutils releases are too unstable and contain
# too many controversial patches so we stick with the official FSF version
# instead.

Source: http://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.xz

Source2: binutils-2.19.50.0.1-output-format.sed

#----------------------------------------------------------------------------

# Purpose:  Use /lib64 and /usr/lib64 instead of /lib and /usr/lib in the
#           default library search path of 64-bit targets.
# Lifetime: Permanent, but it should not be.  This is a bug in the libtool
#           sources used in both binutils and gcc, (specifically the
#           libtool.m4 file).  These are based on a version released in 2009
#           (2.2.6?) rather than the latest version.  (Definitely fixed in
#           libtool version 2.4.6).
Patch01: binutils-2.20.51.0.2-libtool-lib64.patch

# Purpose:  Appends a RHEL or Fedora release string to the generic binutils
#           version string.
# Lifetime: Permanent.  This is a RHEL/Fedora specific patch.
Patch02: binutils-2.25-version.patch

# Purpose:  Exports the demangle.h header file (associated with the libiberty
#           sources) with the binutils-devel rpm.
# Lifetime: Permanent.  This is a RHEL/Fedora specific patch.
Patch03: binutils-2.22.52.0.1-export-demangle.h.patch

# Purpose:  Disables the check in the BFD library's bfd.h header file that
#           config.h has been included before the bfd.h header.  See BZ
#           #845084 for more details.
# Lifetime: Permanent - but it should not be.  The bfd.h header defines
#           various types that are dependent upon configuration options, so
#           the order of inclusion is important.
# FIXME:    It would be better if the packages using the bfd.h header were
#           fixed so that they do include the header files in the correct
#           order.
Patch04: binutils-2.22.52.0.4-no-config-h-check.patch

# Purpose:  Import H.J.Lu's Kernel LTO patch.
# Lifetime: Permanent, but needs continual updating.
# FIXME:    Try removing....
Patch05: binutils-2.26-lto.patch

# Purpose:  Include the filename concerned in readelf error messages.  This
#           makes readelf's output more helpful when it is run on multiple
#           input files.
# Lifetime: Permanent.  This patch changes the format of readelf's output,
#           making it better (IMHO) but also potentially breaking tools that
#           depend upon readelf's current format.  Hence it remains a local
#           patch.
Patch06: binutils-2.29-filename-in-error-messages.patch

# Purpose:  Disable an x86/x86_64 optimization that moves functions from the
#           PLT into the GOTPLT for faster access.  This optimization is
#           problematic for tools that want to intercept PLT entries, such
#           as ltrace and LD_AUDIT.  See BZs 1452111 and 1333481.
# Lifetime: Permanent.  But it should not be.
# FIXME:    Replace with a configure time option.
Patch07: binutils-2.29-revert-PLT-elision.patch

# Purpose:  Changes readelf so that when it displays extra information about
#           a symbol, this information is placed at the end of the line.
# Lifetime: Permanent.
# FIXME:    The proper fix would be to update the scripts that are expecting
#           a fixed output from readelf.  But it seems that some of them are
#           no longer being maintained.
Patch08: binutils-readelf-other-sym-info.patch

# Purpose:  Do not create PLT entries for AARCH64 IFUNC symbols referenced in
#           debug sections.
# Lifetime: Permanent.
# FIXME:    Find related bug.  Decide on permanency.
Patch09: binutils-2.27-aarch64-ifunc.patch

# Purpose:  Remove support for inserting PowerPC Speculation Barrier
#           instructions from the linker.  (It has been deprecated in
#           favour of a hardware fix).
# Lifetime: Fixed in 2.30.1 and/or 2.31.
Patch10: binutils-revert-PowerPC-speculation-barriers.patch

# Purpose:  Stop readelf/objdump for searching for DWO links unless
#           explicitly requested by the user.
# Lifetime: Fixed in 2.30.1 and/or 2.31.
Patch11: binutils-skip-dwo-search-if-not-needed.patch

# Purpose:  Fix a bug in the BFD linker's layout algorithm which ended up
#           placing executable and non-executable pages in the same segment.
# Lifetime: Fixed in 2.30.1 and/or 2.31.
Patch12: binutils-page-to-segment-assignment.patch

# Purpose:  Fix a bug in ld for linking against AARCH64 UEFI
# Lifetime: Fixed in 2.30.1 and/or 2.31
Patch13: binutils-2.30-allow_R_AARCH64-symbols.patch

# Purpose:  Stop strip from replacing unknown relocs with null relocs.  Make
#           it return an error status and not strip the file instead.
# Lifetime: Fixed in 2.31.
Patch14: binutils-strip-unknown-relocs.patch

# Purpose:  Improves objdump's function for locating a symbol to match a
#           given address, so that it uses a binary chop algorithm.
# Lifetime: Fixed in 2.31.
Patch15: binutils-speed-up-objdump.patch

# Purpose:  Ignore duplicate indirect symbols generated by GOLD.
# Lifetime: Permanent.
# FIXME:    This problem needs to be resolved in the FSF sources, but the
#           GOLD maintainers seem to be reluctant to address the issue.
Patch16: binutils-2.28-ignore-gold-duplicates.patch

# Purpose:  Treat relosc against STT_GNU_IFUNC symbols in note sections as
#           if they were relocs against STT_FUNC symbols instead.
# Lifetime: Fixed in 2.31.
Patch17: binutils-ifunc-relocs-in-notes.patch

#----------------------------------------------------------------------------

Provides: bundled(libiberty)

%define gold_arches %ix86 x86_64 %arm aarch64 %{power64} s390x

%if %{with bootstrap}
%define build_gold      no
%else
%ifarch %gold_arches
%define build_gold      both
%else
%define build_gold      no
%endif
%endif

%if %{with debug}
# Define this if you want to skip the strip step and preserve debug info.
# Useful for testing.
%define __debug_install_post : > %{_builddir}/%{?buildsubdir}/debugfiles.list
%define debug_package %{nil}
%endif

Buildroot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

# Perl, sed and touch are all used in the %%prep section of this spec file.
BuildRequires: gcc, perl, sed, coreutils

# Gold needs bison in order to build gold/yyscript.c.
# Bison needs m4.
%if "%{build_gold}" == "both"
BuildRequires: bison, m4, gcc-c++
%endif

%if %{without bootstrap}
BuildRequires: gettext, flex, zlib-devel
%endif

%if %{with docs}
BuildRequires: texinfo >= 4.0
# BZ 920545: We need pod2man in order to build the manual pages.
BuildRequires: /usr/bin/pod2man
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
%else
BuildRequires: findutils
%endif

# Required for: ld-bootstrap/bootstrap.exp bootstrap with --static
# It should not be required for: ld-elf/elf.exp static {preinit,init,fini} array
%if %{with testsuite}
# relro_test.sh uses dc which is part of the bc rpm, hence its inclusion here.
BuildRequires: dejagnu, zlib-static, glibc-static, sharutils, bc
%if "%{build_gold}" == "both"
# The GOLD testsuite needs a static libc++
BuildRequires: libstdc++-static
%endif
%endif

Conflicts: gcc-c++ < 4.0.0

# The higher of these two numbers determines the default ld.
%{!?ld_bfd_priority: %global ld_bfd_priority    50}
%{!?ld_gold_priority:%global ld_gold_priority   30}

%if "%{build_gold}" == "both"
Requires(post): coreutils
Requires(post): %{_sbindir}/alternatives
Requires(preun): %{_sbindir}/alternatives
%endif

# On ARM EABI systems, we do want -gnueabi to be part of the
# target triple.
%ifnarch %{arm}
%define _gnu %{nil}
%endif

#----------------------------------------------------------------------------

%description
Binutils is a collection of binary utilities, including ar (for
creating, modifying and extracting from archives), as (a family of GNU
assemblers), gprof (for displaying call graph profile data), ld (the
GNU linker), nm (for listing symbols from object files), objcopy (for
copying and translating object files), objdump (for displaying
information from object files), ranlib (for generating an index for
the contents of an archive), readelf (for displaying detailed
information about binary files), size (for listing the section sizes
of an object or archive file), strings (for listing printable strings
from files), strip (for discarding symbols), and addr2line (for
converting addresses to file and line).

#----------------------------------------------------------------------------

%package devel
Summary: BFD and opcodes static and dynamic libraries and header files
Group: System Environment/Libraries
Provides: binutils-static = %{version}-%{release}
%if %{with docs}
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
%endif
Requires: zlib-devel
Requires: binutils = %{version}-%{release}
# BZ 1215242: We need touch...
Requires: coreutils

%description devel
This package contains BFD and opcodes static and dynamic libraries.

The dynamic libraries are in this package, rather than a seperate
base package because they are actually linker scripts that force
the use of the static libraries.  This is because the API of the
BFD library is too unstable to be used dynamically.

The static libraries are here because they are now needed by the
dynamic libraries.

Developers starting new projects are strongly encouraged to consider
using libelf instead of BFD.

#----------------------------------------------------------------------------

%prep
%setup -q -n binutils-%{version}
%patch01 -p1
%patch02 -p1
%patch03 -p1
%patch04 -p1
%patch05 -p1
%patch06 -p1
%patch07 -p1
%patch08 -p1
%patch09 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1

# We cannot run autotools as there is an exact requirement of autoconf-2.59.

# On ppc64 and aarch64, we might use 64KiB pages
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*ppc.c
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*aarch64.c
sed -i -e '/common_pagesize/s/4 /64 /' gold/powerpc.cc
sed -i -e '/pagesize/s/0x1000,/0x10000,/' gold/aarch64.cc
# LTP sucks
perl -pi -e 's/i\[3-7\]86/i[34567]86/g' */conf*
sed -i -e 's/%''{release}/%{release}/g' bfd/Makefile{.am,.in}
sed -i -e '/^libopcodes_la_\(DEPENDENCIES\|LIBADD\)/s,$, ../bfd/libbfd.la,' opcodes/Makefile.{am,in}
# Build libbfd.so and libopcodes.so with -Bsymbolic-functions if possible.
if gcc %{optflags} -v --help 2>&1 | grep -q -- -Bsymbolic-functions; then
sed -i -e 's/^libbfd_la_LDFLAGS = /&-Wl,-Bsymbolic-functions /' bfd/Makefile.{am,in}
sed -i -e 's/^libopcodes_la_LDFLAGS = /&-Wl,-Bsymbolic-functions /' opcodes/Makefile.{am,in}
fi
# $PACKAGE is used for the gettext catalog name.
sed -i -e 's/^ PACKAGE=/ PACKAGE=%{?cross}/' */configure
# Undo the name change to run the testsuite.
for tool in binutils gas ld
do
  sed -i -e "2aDEJATOOL = $tool" $tool/Makefile.am
  sed -i -e "s/^DEJATOOL = .*/DEJATOOL = $tool/" $tool/Makefile.in
done
touch */configure
# Touch the .info files so that they are newer then the .texi files and
# hence do not need to be rebuilt.  This eliminates the need for makeinfo.
# The -print is there just to confirm that the command is working.
%if %{without docs}
  find . -name *.info -print -exec touch {} \;
%endif

%ifarch %{power64}
%define _target_platform %{_arch}-%{_vendor}-%{_host_os}
%endif

#----------------------------------------------------------------------------

%build
echo target is %{binutils_target}

%ifarch %{power64}
export CFLAGS="$RPM_OPT_FLAGS -Wno-error"
%else
export CFLAGS="$RPM_OPT_FLAGS"
%endif

CARGS=

case %{binutils_target} in i?86*|sparc*|ppc*|s390*|sh*|arm*|aarch64*)
  CARGS="$CARGS --enable-64-bit-bfd"
  ;;
esac

case %{binutils_target} in ia64*)
  CARGS="$CARGS --enable-targets=i386-linux"
  ;;
esac

case %{binutils_target} in ppc*|ppc64*)
  CARGS="$CARGS --enable-targets=spu"
  ;;
esac

case %{binutils_target} in ppc64-*)
  CARGS="$CARGS --enable-targets=powerpc64le-linux"
  ;;
esac

case %{binutils_target} in ppc64le*)
    CARGS="$CARGS --enable-targets=powerpc-linux"
    ;;
esac

case %{binutils_target} in x86_64*|i?86*|arm*|aarch64*)
  CARGS="$CARGS --enable-targets=x86_64-pep"
  ;;
esac

%if %{default_relro}
  CARGS="$CARGS --enable-relro=yes"
%else
  CARGS="$CARGS --enable-relro=no"
%endif

%if 0%{?_with_debug:1}
CFLAGS="$CFLAGS -O0 -ggdb2 -Wno-error -D_FORTIFY_SOURCE=0"
%define enable_shared 0
%endif

# BZ 1541027 - include the linker flags from redhat-rpm-config as well.
export LDFLAGS=$RPM_LD_FLAGS

# We could optimize the cross builds size by --enable-shared but the produced
# binaries may be less convenient in the embedded environment.
%configure \
  --quiet \
  --build=%{_target_platform} --host=%{_target_platform} \
  --target=%{binutils_target} \
%ifarch %gold_arches
%if "%{build_gold}" == "both"
  --enable-gold=default --enable-ld \
%else
  --enable-gold \
%endif
%endif
%if %{isnative}
  --with-sysroot=/ \
%else
  --enable-targets=%{_host} \
  --with-sysroot=%{_prefix}/%{binutils_target}/sys-root \
  --program-prefix=%{cross} \
%endif
%if %{enable_shared}
  --enable-shared \
%else
  --disable-shared \
%endif
%if %{enable_deterministic_archives}
  --enable-deterministic-archives \
%else
  --enable-deterministic-archives=no \
%endif
%if %{enable_lto}
  --enable-lto \
%endif
%if %{default_compress_debug}
  --enable-compressed-debug-sections=all \
%else
  --enable-compressed-debug-sections=none \
%endif
  $CARGS \
  --enable-plugins \
  --with-bugurl=http://bugzilla.redhat.com/bugzilla/

%if %{with docs}
make %{_smp_mflags} tooldir=%{_prefix} all
make %{_smp_mflags} tooldir=%{_prefix} info
%else
make %{_smp_mflags} tooldir=%{_prefix} MAKEINFO=true all
%endif

# Do not use %%check as it is run after %%install where libbfd.so is rebuild
# with -fvisibility=hidden no longer being usable in its shared form.
%if %{without testsuite}
echo ====================TESTSUITE DISABLED=========================
%else
make -k check < /dev/null || :
echo ====================TESTING=========================
cat {gas/testsuite/gas,ld/ld,binutils/binutils}.sum
echo ====================TESTING END=====================
for file in {gas/testsuite/gas,ld/ld,binutils/binutils}.{sum,log}
do
  ln $file binutils-%{_target_platform}-$(basename $file) || :
done
tar cjf binutils-%{_target_platform}.tar.bz2 binutils-%{_target_platform}-*.{sum,log}
uuencode binutils-%{_target_platform}.tar.bz2 binutils-%{_target_platform}.tar.bz2
rm -f binutils-%{_target_platform}.tar.bz2 binutils-%{_target_platform}-*.{sum,log}
%endif

#----------------------------------------------------------------------------

%install
rm -rf %{buildroot}
%if %{with docs}
%make_install DESTDIR=%{buildroot}
%else
%make_install DESTDIR=%{buildroot} MAKEINFO=true
%endif

%if %{isnative}
%if %{with docs}
make prefix=%{buildroot}%{_prefix} infodir=%{buildroot}%{_infodir} install-info
%endif

# Rebuild libiberty.a with -fPIC.
# Future: Remove it together with its header file, projects should bundle it.
make -C libiberty clean
make CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C libiberty

# Rebuild libbfd.a with -fPIC.
# Without the hidden visibility the 3rd party shared libraries would export
# the bfd non-stable ABI.
make -C bfd clean
make CFLAGS="-g -fPIC $RPM_OPT_FLAGS -fvisibility=hidden" -C bfd

# Rebuild libopcodes.a with -fPIC.
make -C opcodes clean
make CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C opcodes

install -m 644 bfd/libbfd.a %{buildroot}%{_libdir}
install -m 644 libiberty/libiberty.a %{buildroot}%{_libdir}
install -m 644 include/libiberty.h %{buildroot}%{_prefix}/include
install -m 644 opcodes/libopcodes.a %{buildroot}%{_libdir}
# Remove Windows/Novell only man pages
rm -f %{buildroot}%{_mandir}/man1/{dlltool,nlmconv,windres,windmc}*
%if %{without docs}
rm -f %{buildroot}%{_mandir}/man1/{addr2line,ar,as,c++filt,elfedit,gprof,ld,nm,objcopy,objdump,ranlib,readelf,size,strings,strip}*
rm -f %{buildroot}%{_infodir}/{as,bfd,binutils,gprof,ld}*
%endif

%if %{enable_shared}
chmod +x %{buildroot}%{_libdir}/lib*.so*
%endif

# Prevent programs from linking against libbfd and libopcodes
# dynamically, as they are change far too often.
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.so

# Remove libtool files, which reference the .so libs
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.la

# Sanity check --enable-64-bit-bfd really works.
grep '^#define BFD_ARCH_SIZE 64$' %{buildroot}%{_prefix}/include/bfd.h
# Fix multilib conflicts of generated values by __WORDSIZE-based expressions.
%ifarch %{ix86} x86_64 ppc %{power64} s390 s390x sh3 sh4 sparc sparc64 arm
sed -i -e '/^#include "ansidecl.h"/{p;s~^.*$~#include <bits/wordsize.h>~;}' \
    -e 's/^#define BFD_DEFAULT_TARGET_SIZE \(32\|64\) *$/#define BFD_DEFAULT_TARGET_SIZE __WORDSIZE/' \
    -e 's/^#define BFD_HOST_64BIT_LONG [01] *$/#define BFD_HOST_64BIT_LONG (__WORDSIZE == 64)/' \
    -e 's/^#define BFD_HOST_64_BIT \(long \)\?long *$/#if __WORDSIZE == 32\
#define BFD_HOST_64_BIT long long\
#else\
#define BFD_HOST_64_BIT long\
#endif/' \
    -e 's/^#define BFD_HOST_U_64_BIT unsigned \(long \)\?long *$/#define BFD_HOST_U_64_BIT unsigned BFD_HOST_64_BIT/' \
    %{buildroot}%{_prefix}/include/bfd.h
%endif
touch -r bfd/bfd-in2.h %{buildroot}%{_prefix}/include/bfd.h

# Generate .so linker scripts for dependencies; imported from glibc/Makerules:

# This fragment of linker script gives the OUTPUT_FORMAT statement
# for the configuration we are building.
OUTPUT_FORMAT="\
/* Ensure this .so library will not be used by a link for a different format
   on a multi-architecture system.  */
$(gcc $CFLAGS $LDFLAGS -shared -x c /dev/null -o /dev/null -Wl,--verbose -v 2>&1 | sed -n -f "%{SOURCE2}")"

tee %{buildroot}%{_libdir}/libbfd.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

/* The libz dependency is unexpected by legacy build scripts.  */
/* The libdl dependency is for plugin support.  (BZ 889134)  */
INPUT ( %{_libdir}/libbfd.a -liberty -lz -ldl )
EOH

tee %{buildroot}%{_libdir}/libopcodes.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

INPUT ( %{_libdir}/libopcodes.a -lbfd )
EOH

%else # !isnative
# For cross-binutils we drop the documentation.
rm -rf %{buildroot}%{_infodir}
# We keep these as one can have native + cross binutils of different versions.
#rm -rf {buildroot}{_prefix}/share/locale
#rm -rf {buildroot}{_mandir}
rm -rf %{buildroot}%{_libdir}/libiberty.a
%endif # !isnative

# This one comes from gcc
rm -f %{buildroot}%{_infodir}/dir
rm -rf %{buildroot}%{_prefix}/%{binutils_target}

%find_lang %{?cross}binutils
%find_lang %{?cross}opcodes
%find_lang %{?cross}bfd
%find_lang %{?cross}gas
%find_lang %{?cross}gprof
cat %{?cross}opcodes.lang >> %{?cross}binutils.lang
cat %{?cross}bfd.lang >> %{?cross}binutils.lang
cat %{?cross}gas.lang >> %{?cross}binutils.lang
cat %{?cross}gprof.lang >> %{?cross}binutils.lang

if [ -x ld/ld-new ]; then
  %find_lang %{?cross}ld
  cat %{?cross}ld.lang >> %{?cross}binutils.lang
fi
if [ -x gold/ld-new ]; then
  %find_lang %{?cross}gold
  cat %{?cross}gold.lang >> %{?cross}binutils.lang
fi

#----------------------------------------------------------------------------

%clean
rm -rf %{buildroot}

#----------------------------------------------------------------------------

%post
%if "%{build_gold}" == "both"
%__rm -f %{_bindir}/%{?cross}ld
%{_sbindir}/alternatives --install %{_bindir}/%{?cross}ld %{?cross}ld \
  %{_bindir}/%{?cross}ld.bfd %{ld_bfd_priority}
%{_sbindir}/alternatives --install %{_bindir}/%{?cross}ld %{?cross}ld \
  %{_bindir}/%{?cross}ld.gold %{ld_gold_priority}
%{_sbindir}/alternatives --auto %{?cross}ld
%endif # both ld.gold and ld.bfd

%if %{isnative}
/sbin/ldconfig

%if %{with docs}
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/as.info.gz
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/binutils.info.gz
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/gprof.info.gz
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/ld.info.gz
%endif # with docs
%endif # isnative

exit 0

#----------------------------------------------------------------------------

%preun
%if "%{build_gold}" == "both"
if [ $1 = 0 ]; then
  %{_sbindir}/alternatives --remove %{?cross}ld %{_bindir}/%{?cross}ld.bfd
  %{_sbindir}/alternatives --remove %{?cross}ld %{_bindir}/%{?cross}ld.gold
fi
%endif # both ld.gold and ld.bfd

%if %{isnative}
if [ $1 = 0 ]; then
  if [ -e %{_infodir}/binutils.info.gz ]
  then
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/as.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/binutils.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/gprof.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/ld.info.gz
  fi
fi
%endif # isnative

exit 0

#----------------------------------------------------------------------------

%if %{isnative}
%postun
/sbin/ldconfig
  if [ -e %{_infodir}/binutils.info.gz ]
  then
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/as.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/binutils.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/gprof.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/ld.info.gz
  fi
%endif # isnative

#----------------------------------------------------------------------------

%files -f %{?cross}binutils.lang
%defattr(-,root,root,-)
%doc COPYING COPYING3 COPYING3.LIB COPYING.LIB
%doc README
%{_bindir}/%{?cross}[!l]*

%if "%{build_gold}" == "both"
%{_bindir}/%{?cross}ld.*
%ghost %{_bindir}/%{?cross}ld
%else
%{_bindir}/%{?cross}ld*
%endif # both ld.gold and ld.bfd

%if %{with docs}
%{_mandir}/man1/*
%{_infodir}/as.info.gz
%{_infodir}/binutils.info.gz
%{_infodir}/gprof.info.gz
%{_infodir}/ld.info.gz
%endif # with docs

%if %{enable_shared}
%{_libdir}/lib*.so
%exclude %{_libdir}/libbfd.so
%exclude %{_libdir}/libopcodes.so
%endif # enable_shared

%if %{isnative}

%if %{with docs}
%{_infodir}/[^b]*info*
%{_infodir}/binutils*info*
%endif # with docs

%files devel
%defattr(-,root,root,-)
%{_prefix}/include/*
%{_libdir}/lib*.a
%{_libdir}/libbfd.so
%{_libdir}/libopcodes.so

%if %{with docs}
%{_infodir}/bfd*info*
%endif # with docs

%endif # isnative

#----------------------------------------------------------------------------
%changelog
* 19 April 2018 Initial el6 backport from fc29 2.30-12

