%global api_version 1.16

# run "make check" by default
%bcond_with check
# Run optional test
%bcond_with automake_enables_optional_test

# remove once %%configure is used instead of ./configure
%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

Summary:    A GNU tool for automatically creating Makefiles
Name:       automake
Version:    %{api_version}.1
Release:    1%{?dist}

# docs ~> GFDL, sources ~> GPLv2+, mkinstalldirs ~> PD and install-sh ~> MIT
License:    GPLv2+ and GFDL and Public Domain and MIT

Group:      Development/Tools
Source:     ftp://ftp.gnu.org/gnu/automake/automake-%{version}.tar.xz
Source2:    http://git.savannah.gnu.org/cgit/config.git/plain/config.sub
Source3:    http://git.savannah.gnu.org/cgit/config.git/plain/config.guess

# Keep those patches in 'git format-patch' format (with docs).


%if %{with check} && !%{without automake_enables_optional_test}
Patch0:     automake-1.15-disable-vala-tests.patch
%endif

URL:        http://www.gnu.org/software/automake/
Requires:   autoconf >= 2.65

# requirements not detected automatically (#919810)
Requires:   perl(Thread::Queue)
Requires:   perl(threads)

BuildRequires:  autoconf >= 2.65
BuildRequires:  coreutils
BuildRequires:  findutils
BuildRequires:  help2man
BuildRequires:  make
BuildRequires:  perl-generators
#BuildRequires:  perl-interpreter
BuildRequires:  perl(Thread::Queue)
BuildRequires:  perl(threads)

Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
BuildArch:  noarch

# for better tests coverage:
%if %{with check}
%if %{with automake_enables_optional_test}
BuildRequires: automake libtool gettext-devel flex bison texinfo-tex texlive-dvips
BuildRequires: java-devel-openjdk gcc-gfortran
BuildRequires: dejagnu expect emacs imake python-docutils vala
BuildRequires: cscope ncompress sharutils
BuildRequires: gcc-objc gcc-objc++
%if !0%{?rhel:1}
BuildRequires: python-virtualenv lzip
%endif
%endif
%endif



# remove bogus Automake perl dependencies and provides
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}^perl\\(Automake::
%global __provides_exclude %{?__provides_exclude:%__provides_exclude|}^perl\\(Automake::

%description
Automake is a tool for automatically generating `Makefile.in'
files compliant with the GNU Coding Standards.

You should install Automake if you are developing software and would
like to use its ability to automatically generate GNU standard
Makefiles.

%prep
%autosetup -p1
%if %{with check} && %{with automake_enables_optional_test}
autoreconf -iv
%endif

file=`find -name config.sub | head -1`
cp %{SOURCE2} $file
file=`find -name config.guess | head -1`
cp %{SOURCE3} $file

# Fedora only to add ppc64p7 (Power7 optimized) arch:
perl -pi -e "s/ppc64-\*/ppc64-\* \| ppc64p7-\*/" lib/config.sub

%build
# disable replacing config.guess and config.sub from redhat-rpm-config
%global _configure_gnuconfig_hack 0
%configure
make %{?_smp_mflags}
cp m4/acdir/README README.aclocal
cp contrib/multilib/README README.multilib

%install
make install DESTDIR=%{buildroot}

%check
# %%global TESTS_FLAGS t/preproc-errmsg t/preproc-basics
%if %{with check}
make -k %{?_smp_mflags} check %{?TESTS_FLAGS: TESTS="%{TESTS_FLAGS}"} \
    || ( cat ./test-suite.log && false )
%endif

%post
/sbin/install-info %{_infodir}/automake.info.gz %{_infodir}/dir || :

%preun
if [ $1 = 0 ]; then
    /sbin/install-info --delete %{_infodir}/automake.info.gz %{_infodir}/dir || :
fi

%files
%doc AUTHORS README THANKS NEWS README.aclocal README.multilib COPYING*
%exclude /usr/share/doc/automake/amhello-1.0.tar.gz
%exclude %{_infodir}/dir
%exclude %{_datadir}/aclocal
%{_bindir}/*
%{_infodir}/*.info*
%{_datadir}/automake-%{api_version}
%{_datadir}/aclocal-%{api_version}
%{_mandir}/man1/*

%changelog
* 19 April 2018 Initial el6 backport from fc29 1.16.1-1
