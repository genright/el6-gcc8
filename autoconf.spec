# Enable Emacs support
%bcond_with autoconf_enables_emacs
# Run extended test
%bcond_without autoconf_enables_optional_test

Summary:    A GNU tool for automatically configuring source code
Name:       autoconf
Version:    2.69
Release:    27%{?dist}
License:    GPLv2+ and GFDL
Source0:    http://ftpmirror.gnu.org/autoconf/autoconf-%{version}.tar.xz
Source1:    config.site
Source2:    autoconf-init.el
URL:        http://www.gnu.org/software/autoconf/

Patch1:     autoconf-2.69-perl-5.22-autoscan.patch

BuildArch:  noarch


# run "make check" by default
%bcond_with check

# m4 >= 1.4.6 is required, >= 1.4.14 is recommended:
BuildRequires:      m4 >= 1.4.10
Requires:           m4 >= 1.4.10
%if %{with autoconf_enables_emacs}
Requires:           emacs-filesystem
BuildRequires:      emacs
%endif
# the filtering macros are currently in /etc/rpm/macros.perl:
BuildRequires:      perl-generators
#BuildRequires:      perl-macros
BuildRequires:      perl(Data::Dumper)
# from f19, Text::ParseWords is not the part of 'perl' package
BuildRequires:      perl(Text::ParseWords)

# %%configure replaces config.guess/config.sub for us, which confuses autoconf
# build system and it produces empty man pages for those scripts if help2man is
# not installed
BuildRequires:      help2man

%if %{with check}
%if %{with autoconf_enables_optional_test}
# For extended testsuite coverage
BuildRequires:      gcc-gfortran
%if 0%{?fedora} >= 15
BuildRequires:      erlang
%endif
%endif
%endif

Requires(post):     /sbin/install-info
Requires(preun):    /sbin/install-info

# filter out bogus perl(Autom4te*) dependencies
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}^perl\\(Autom4te::
%global __provides_exclude %{?__provides_exclude:%__provides_exclude|}^perl\\(Autom4te::

%description
GNU's Autoconf is a tool for configuring source code and Makefiles.
Using Autoconf, programmers can create portable and configurable
packages, since the person building the package is allowed to
specify various configuration options.

You should install Autoconf if you are developing software and
would like to create shell scripts that configure your source code
packages. If you are installing Autoconf, you will also need to
install the GNU m4 package.

Note that the Autoconf package is not required for the end-user who
may be configuring software with an Autoconf-generated script;
Autoconf is only required for the generation of the scripts, not
their use.


%prep
%autosetup -p1

%build
%if %{with autoconf_enables_emacs}
export EMACS=%{_bindir}/emacs
%else
export EMACS=%{_bindir}/false
%endif
%configure \
    %{?with_autoconf_enables_emacs:--with-lispdir=%{_emacs_sitelispdir}/autoconf}
make %{?_smp_mflags}


%check
%if %{with check}
# make check # TESTSUITEFLAGS='1-198 200-' # will disable nr. 199.
# make check TESTSUITEFLAGS="-k \!erlang"
make check %{?_smp_mflags}
%endif


%install
make install %{?_smp_mflags} DESTDIR=%{buildroot}
mkdir -p %{buildroot}/share
install -m 0644 %{SOURCE1} %{buildroot}%{_datadir}

%if %{with autoconf_enables_emacs}
# Create file to activate Emacs modes as required
mkdir -p %{buildroot}%{_emacs_sitestartdir}
install -p -m 0644 %{SOURCE2} %{buildroot}%{_emacs_sitestartdir}
%endif


%post
/sbin/install-info %{_infodir}/autoconf.info %{_infodir}/dir || :

%preun
if [ "$1" = 0 ]; then
    /sbin/install-info --del %{_infodir}/autoconf.info %{_infodir}/dir || :
fi


%files
%doc COPYING*
%{_bindir}/*
%{_infodir}/autoconf.info*
# don't include standards.info, because it comes from binutils...
%exclude %{_infodir}/standards*
# don't include info's TOP directory
%exclude %{_infodir}/dir
%{_datadir}/autoconf/
%{_datadir}/config.site
%if %{with autoconf_enables_emacs}
%{_datadir}/emacs/site-lisp/*
%endif
%{_mandir}/man1/*
%doc AUTHORS ChangeLog NEWS README THANKS TODO


%changelog
* 19 April 2018 Initial el6 backport from fc28 2.69-27
