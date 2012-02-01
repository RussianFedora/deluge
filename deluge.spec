Name:		deluge
Version:	1.3.2
Release:	1.3%{?dist}.R

Summary:	A GTK+ BitTorrent client with support for DHT, UPnP, and PEX
Group:		Applications/Internet
License:	GPLv3 with exceptions
URL:		http://deluge-torrent.org/
Source0:	http://download.deluge-torrent.org/source/%{name}-%{version}.tar.lzma
## The scalable icon needs to be installed to the proper place.
Source1:	deluge-daemon-init
Patch0:		deluge-scalable-icon-dir.diff
Patch1:		deluge-1.3.2-libtorrent-force.patch
BuildArch:	noarch
BuildRequires:	desktop-file-utils
BuildRequires:	python-devel
BuildRequires:	python-setuptools
BuildRequires:	rb_libtorrent-python >= 0.14.9
## add Requires to make into Meta package
Requires:	%{name}-common = %{version}-%{release}
Requires:	%{name}-gtk = %{version}-%{release}
Requires:	%{name}-images = %{version}-%{release}
Requires:	%{name}-console = %{version}-%{release}
Requires:	%{name}-web = %{version}-%{release}
Requires:	%{name}-daemon = %{version}-%{release}
# removal of flags
Provides:	deluge-flags = %{version}-%{release}
Obsoletes:	deluge-flags < 1.3.1-3


%description
Deluge is a new BitTorrent client, created using Python and GTK+. It is
intended to bring a native, full-featured client to Linux GTK+ desktop
environments such as GNOME and XFCE. It supports features such as DHT
(Distributed Hash Tables), PEX (µTorrent-compatible Peer Exchange), and UPnP
(Universal Plug-n-Play) that allow one to more easily share BitTorrent data
even from behind a router with virtually zero configuration of port-forwarding.


%package common
Summary:	Files common to Deluge sub packages
Group:		Applications/Internet
License:	GPLv3 with exceptions
Requires:	python-setuptools
Requires:	pyOpenSSL
Requires:	python-chardet
Requires:	python-simplejson
Requires:	pyxdg
Requires:	rb_libtorrent-python >= 0.14.9
Requires:	python-twisted-web


%description common
Common files needed by the Deluge bittorrent client sub packages


%package gtk
Summary:	The gtk UI to Deluge
Group:		Applications/Internet
License:	GPLv3 with exceptions
Requires:	%{name}-common = %{version}-%{release}
Requires:	%{name}-images = %{version}-%{release}
Requires:	%{name}-daemon = %{version}-%{release}
Requires:	gnome-python2-gnome
## Required for the proper ownership of icon dirs.
Requires:	hicolor-icon-theme
Requires:	notify-python
Requires:	pygtk2-libglade


%description gtk
Deluge bittorent client GTK graphical user interface


%package images
Summary:	Image files for deluge
Group:		Applications/Internet
License:	GPLv3 with exceptions


%description images
Data files used by the GTK and web user interface for Deluge bittorent client


%package console
Summary:	CLI to Deluge
Group:		Applications/Internet
License:	GPLv3 with exceptions
Requires:	%{name}-common = %{version}-%{release}
Requires:	%{name}-daemon = %{version}-%{release}


%description console
Deluge bittorent client command line interface


%package web
Summary:	Web interface to Deluge
Group:		Applications/Internet
License:	GPLv3 with exceptions
Requires:	python-mako
Requires:	%{name}-common = %{version}-%{release}
Requires:	%{name}-images = %{version}-%{release}
Requires:	%{name}-daemon = %{version}-%{release}


%description web
Deluge bittorent client web interface


%package daemon
Summary:	The Deluge daemon
Group:		Applications/Internet
License:	GPLv3 with exceptions
Requires:	%{name}-common = %{version}-%{release}
Requires(pre):	shadow-utils
Requires(post):	chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts


%description daemon
Files for the Deluge daemon


%prep
%setup -q
%patch0 -p0 -b .fix-scalable-icon-dir
%patch1 -p0 -b .libtorrent


%build
CFLAGS="%{optflags}" %{__python} setup.py build


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_initddir}
install -m755 %{SOURCE1} %{buildroot}%{_initddir}/%{name}-daemon
mkdir -p %{buildroot}/var/lib/%{name}

%{__python} setup.py install -O1 --skip-build --root %{buildroot}

desktop-file-install --vendor el6 \
    --dir %{buildroot}%{_datadir}/applications \
    --copy-name-to-generic-name \
    --add-mime-type=application/x-bittorrent \
    --delete-original \
    --remove-category=Application \
    %{buildroot}%{_datadir}/applications/%{name}.desktop

## NOTE: The lang files should REEEAALLLY be in a standard place such as
## /usr/share/locale or similar. It'd make things so much nicer for
## the packaging. :O
## A bit of sed magic to mark the translation files with %%lang, taken from
## find-lang.sh (part of the rpm-build package) and tweaked somewhat. We
## cannot (unfortunately) call find-lang directly since it's not on a
## "$PREFIX/share/locale/"-ish directory tree.

pushd %{buildroot}
    find -type f -o -type l \
        | sed '
            s:%{buildroot}%{python_sitelib}::
            s:^\.::
            s:\(.*/deluge/i18n/\)\([^/_]\+\)\(.*\.mo$\):%lang(\2) \1\2\3:
            s:^\([^%].*\)::
            s:%lang(C) ::
            /^$/d' \
    > %{name}.lang

## Now we move that list back to our sources, so that '%%files -f' can find it
## properly.
popd && mv %{buildroot}/%{name}.lang .

#fix non exec script errors in two files
for lib in "%{buildroot}%{python_sitelib}/%{name}/ui/web/gen_gettext.py" "%{buildroot}%{python_sitelib}/%{name}/ui/Win32IconImagePlugin.py" ; do
 sed '/\/usr\/bin/d' $lib > $lib.new &&
 touch -r $lib $lib.new &&
 mv $lib.new $lib
done

#Removing unneeded .order files.
rm -f %{buildroot}%{python_sitelib}/%{name}/ui/web/js/deluge-all/.order
rm -f %{buildroot}%{python_sitelib}/%{name}/ui/web/js/deluge-all/add/.order
rm -f %{buildroot}%{python_sitelib}/%{name}/ui/web/js/deluge-all/data/.order
rm -f %{buildroot}%{python_sitelib}/%{name}/ui/web/js/deluge-all/.build
rm -f ${buildroot}%{python_sitelib}/%{name}/ui/web/js/deluge-all/.build_data


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)


%files common -f %{name}.lang
%defattr(-,root,root,-)
%doc ChangeLog LICENSE README
%{python_sitelib}/%{name}-%{version}-py?.?.egg-info/
%dir %{python_sitelib}/%{name}
%{python_sitelib}/%{name}/*.py*
%{python_sitelib}/%{name}/plugins
%{python_sitelib}/%{name}/core
%dir %{python_sitelib}/%{name}/ui
%{python_sitelib}/%{name}/ui/*.py*
# includes %%name.pot too
%dir %{python_sitelib}/%{name}/i18n
%dir %{python_sitelib}/%{name}/i18n/*
%dir %{python_sitelib}/%{name}/i18n/*/LC_MESSAGES


%files images
%defattr(-,root,root,-)
# only pixmaps dir is in data so I own it all
%{python_sitelib}/%{name}/data
# if someone decides to only install images
%dir %{python_sitelib}/%{name}
%{_datadir}/icons/hicolor/*/apps/%{name}.*
%{_datadir}/pixmaps/%{name}.*


%files gtk
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_bindir}/%{name}-gtk
%{_datadir}/applications/el6-%{name}.desktop
%{python_sitelib}/%{name}/ui/gtkui
%{_mandir}/man?/%{name}-gtk*
%{_mandir}/man?/%{name}.1*


%files console
%defattr(-,root,root,-)
%{_bindir}/%{name}-console
%{python_sitelib}/%{name}/ui/console
%{_mandir}/man?/%{name}-console*


%files web
%defattr(-,root,root,-)
%{_bindir}/%{name}-web
%{python_sitelib}/%{name}/ui/web
%{_mandir}/man?/%{name}-web*


%files daemon
%defattr(-,root,root,-)
%{_bindir}/%{name}d
%{_initddir}/%{name}-daemon
%attr(-,%{name}, %{name})/var/lib/%{name}/
%{_mandir}/man?/%{name}d*


%pre daemon
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
useradd -r -g %{name} -d /var/lib/%{name} -s /sbin/nologin \
        -c "deluge daemon account" %{name}
exit 0


%post daemon
/sbin/chkconfig --add %{name}-daemon


%post gtk
update-desktop-database &> /dev/null || :


%post images
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :


%preun daemon
if [ $1 = 0 ] ; then
    /sbin/service %{name}-daemon stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}-daemon
fi


%postun daemon
if [ "$1" -ge "1" ] ; then
    /sbin/service %{name}-daemon condrestart >/dev/null 2>&1 || :
fi


%postun gtk
update-desktop-database &> /dev/null || :


%postun images
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi


%posttrans images
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%changelog
* Tue Jan 31 2012 Arkady L. Shane <ashejn@russianfedora.ru> - 1.3.2-1.3.R
- rebuilt

* Sun Jun 26 2011 LTN Packager <packager-el6rpms@LinuxTECH.NET> - 1.3.2-1.3
- imported from Fedora
- cleaned up spec-file
- added missing 'clean' section
- added patch to make deluge use external rb_libtorrent

* Mon May 30 2011 Justin Noah <justinnoah@gmail.com> - 1.3.2-1
- Update to latest upstream release
- http://dev.deluge-torrent.org/wiki/ReleaseNotes/1.3.2
- Dropped unnecessary patch concerning deluge.dektop categories
- Remove hidden files created by webui buid and compression

* Mon Mar 28 2011 Rahul Sundaram <sundaram@fedoraproject.org> - 1.3.1-5
- Add init script for the deluge daemon. Resolves rhbz#537387
- Rewrite package descriptions to be better

* Fri Feb 11 2011 Rahul Sundaram <sundaram@fedoraproject.org> - 1.3.1-4
- Build split up packages

* Mon Jan 17 2011 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1.3.1-3
- correct posttrans snippet

* Mon Jan 10 2011 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1.3.1-3
- Updated as per https://bugzilla.redhat.com/show_bug.cgi?id=603906#c24

* Tue Dec 28 2010 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1.3.1-2
- Correct scripts
- Correct directory ownership
- add desktop file patch

* Mon Dec 27 2010 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1.3.1-1
- update to latest upstream release
- Moved icon update scriptlets to -images
- Moved python-mako requires to -web

* Fri Oct 29 2010 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1.3.0-3
- correct License and check file ownerships
- updated icon cache scriplet

* Thu Oct 28 2010 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1.3.0-2
- Split into sub packages #603906

* Wed Oct 13 2010 Peter Gordon <peter@thecodergeek.com> - 1.3.0-1
- Update to new upstream release (1.3.0).
- Add P2P to the .desktop file Categories list.
- Resolves: #615984 (.desktop menu entry has wrong/missing categories)

* Tue Jul 27 2010 Bill Nottingham <notting@redhat.com> - 1.3.0-0.3.rc1
- Rebuilt for boost-1.44

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 1.3.0-0.2.rc1
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Jul 20 2010 Peter Gordon <peter@thecodergeek.com> - 1.3.0-0.1.rc1
- Update to new upstream release candidate (1.3.0 RC1)

* Sun Mar 28 2010 Peter Gordon <peter@thecodergeek.com> - 1.2.3-1
- Update to new upstream bug-fix release (1.2.3).

* Sat Feb 27 2010 Peter Gordon <peter@thecodergeek.com> - 1.2.1-1
- Update to new upstream bug-fix release (1.2.1)
- Add python-mako dependency to fix WebUI startup crash. 
- Resolves: #568845 (missing dependency to python-mako)

* Sat Jan 16 2010 Peter Gordon <peter@thecodergeek.com> - 1.2.0-1
- Update to new upstream final release (1.2.0)

* Fri Jan 08 2010 Peter Gordon <peter@thecodergeek.com> - 1.2.0-0.4.rc5
- Update to new upstream release candidate (1.2.0 RC5)

* Wed Nov 25 2009 Peter Gordon <peter@thecodergeek.com> - 1.2.0-0.3.rc4
- Update to new upstream release candidate (1.2.0 RC4)

* Wed Nov 04 2009 Peter Gordon <peter@thecodergeek.com> - 1.2.0-0.2.rc3
- Update to new upstream release candidate (1.2.0 RC3)

* Sun Oct 11 2009 Peter Gordon <peter@thecodergeek.com> - 1.2.0-0.1.rc1
- Update to new upstream release candidate (1.2.0 RC1)
- Adds Twisted dependencies, and drops the D-Bus dependency.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.9-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 08 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.9-2
- Fixed rb_libtorrent-python dependency, so as not to use the
  %%min_rblibtorrent_ver macro any more (#510264).

* Wed Jun 17 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.9-1
- Update to new upstream bug-fix release (1.1.9).
- Do not hard-code minimum rb_libtorrent version. (We're only building against
  the system rb_libtorrent for Fedora 11+, which already has the necessary
  version.)

* Wed May 27 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.8-1
- Update to new upstream release (1.1.8) for bug-fixes and some translation
  updates. Adds dependency on chardet for fixing lots of bugs with torrents
  which are not encoded as UTF-8.
- Add back the flags, in an optional -flags subpackage as per the new Flags
  policy (Package_Maintainers_Flags_Policy on the wiki).
- Add LICENSE and README to installed documentation.

* Fri May 08 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.7-2
- Rebuild for the Boost 1.39.0 update.

* Sat May 02 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.7-1
- Update to new upstream bug-fix release (1.1.7).

* Mon Apr 06 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.6-1
- Update to new upstream bug-fix release (1.1.6)
- Fix GPL version, add OpenSSL exception to License.
- Remove libtool, openssl-devel, and boost-devel BuildRequires (were only
  necessary when building the in-tarball libtorrent copy).

* Mon Mar 16 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.5-1
- Update to new upstream bug-fix release (1.1.5)
- Remove FIXME comment about parallel-compilation. We're not building the
  in-tarball libtorrent copy anymore, so no compilation (other than the python
  bytecode) happens and we no longer need to worry about this.

* Tue Mar 10 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.4-2
- Fix the installed location of the scalable (SVG) icon (#483443).
  + scalable-icon-dir.diff

* Mon Mar 09 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.4-1
- Update to new upstream bug-fix release (1.1.4)

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Feb 15 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.3-1
- Update to new upstream bug-fix release (1.1.3)

* Sun Feb 01 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.2-2
- Fix scalable icon directory ownership (#483443).

* Sat Jan 31 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.2-1
- Update to new upstream bug-fix release (1.1.2)

* Sun Jan 25 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.1-1
- Update to new upstream bug-fix release (1.1.1)

* Sun Jan 11 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.0-1
- Update to new upstream release (1.1.0 Final - yay!)
- Drop the get_tracker_host patch (fixed upstream):
  - fix-get_tracker-host-if-no-tracker.patch
  
* Fri Jan 09 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.0-0.4.rc3
- Do not package the country flags data.
- Resolves: #479265 (country flags should not be used in Deluge)

* Wed Jan 07 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.0-0.3.rc3
- Add patch from upstream SVN to fix an error where torrents are not shown (or
  possibly shown in "Error" states) due to a bad inet_aton call:
  + fix-get_tracker-host-if-no-tracker.patch
- Resolves: #479097 (No torrent shown in menu); thanks to Mamoru Tasaka for
  the bug report.
- Fix day of previous %%changelog entry.

* Tue Jan 06 2009 Peter Gordon <peter@thecodergeek.com> - 1.1.0-0.2.rc3
- Update to new upstream release candidate (1.1.0 RC3)
- Build against the system rb_libtorrent instead of using the in-tarball copy
  (requires rb_libtorrent 0.14+), and adjust dependencies accordingly. Drop
  the hacked setup.py script formerly used to enable this (fixed upstream):
  - fixed-setup.py
- Make it a noarch package now that it's just python scripts and related
  data files (translations, images, etc.)

* Mon Dec 29 2008 Peter Gordon <peter@thecodergeek.com> - 1.1.0-0.1.rc2
- Update to new upstream release candidate (1.1.0 RC2)

* Thu Dec 18 2008 Petr Machata <pmachata@redhat.com> - 1.0.7-2
- Rebuild for new boost.

* Tue Dec 16 2008 Peter Gordon <peter@thecodergeek.com> - 1.0.7-1
- Update to new upstream bug-fix release (1.0.7)
- Remove CC-BY-SA license (the Tango WebUI images have been replaced by upstream).

* Mon Dec 01 2008 Peter Gordon <peter@thecodergeek.com> - 1.0.6-1
- Update to new upstream release (1.0.6)
- Adds Tango images to the WebUI data (CC-BY-SA) and some man pages.
- Properly mark translation files with %%lang.

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.0.5-3
- Fix locations for Python 2.6

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.0.5-2
- Rebuild for Python 2.6

* Thu Nov 13 2008 Peter Gordon <peter@thecodergeek.com> - 1.0.5-1
- Update to new upstream release (1.0.5)

* Fri Oct 31 2008 Peter Gordon <peter@thecodergeek.com> - 1.0.4-1
- Update to new upstream release (1.0.4). 

* Fri Oct 24 2008 Peter Gordon <peter@thecodergeek.com> - 1.0.3-1
- Update to new upstream release (1.0.3)

* Sun Oct 12 2008 Peter Gordon <peter@thecodergeek.com> - 1.0.2-1
- Update to new upstream release (1.0.2)
- Drop multithreaded boost compilation patch (fixed upstream, again).
  - mt-boost-fix.patch
  
* Sat Sep 27 2008 Peter Gordon <peter@thecodergeek.com> - 1.0.0-1
- Update to new upstream release (1.0.0 Final)
- Apply patch from Mamoru Tasaka to build against the multi-threaded Boost
  libraries once more:
  + mt-boost-fix.patch
- Resolves: #464151 (About 1.0.0 build failure)

* Tue Sep 16 2008 Peter Gordon <peter@thecodergeek.com> - 0.9.09-1
- Update to new upstream release candidate (1.0.0 RC9)
- Drop mt-boost patch (fixed upstream):
  - use-mt-boost.patch

* Sun Sep 07 2008 Peter Gordon <peter@thecodergeek.com> - 0.9.08-1
- Update to new upstream release candidate (1.0.0 RC8)
- Drop state_upgrade script from the documentation. (This is now handled
  automatically.)
- Fix version in previous %%changelog entry.

* Wed Aug 13 2008 Peter Gordon <peter@thecodergeek.com> - 0.9.07-1
- Update to new upstream release candidate (1.0.0 RC7)
- Drop desktop file icon name hack (fixed upstream).

* Wed Aug 13 2008 Peter Gordon <peter@thecodergeek.com> - 0.9.06-1
- Update to new upstream release candidate (1.0.0 RC6)
- Drop desktop file icon name hack (fixed upstream).

* Fri Aug 01 2008 Peter Gordon <peter@thecodergeek.com> - 0.9.04-1
- Update to new upstream release candidate (1.0.0 RC4)

* Wed Jul 23 2008 Peter Gordon <peter@thecodergeek.com> - 0.9.03-2
- Add setuptools runtime dependency, to fix "No module named pkg_resources"
  error messages.

* Mon Jul 21 2008 Peter Gordon <peter@thecodergeek.com> - 0.9.03-1
- Update to new upstream release candidate (1.0.0 RC3)
- Re-add the blocklist plugin, at upstream's suggestion. (The rewrite is
  complete.)

* Tue Jul 15 2008 Peter Gordon <peter@thecodergeek.com> - 0.9.02-1
- Update to new upstream release candidate (1.0.0 RC2)
- Force building against the multithreaded Boost libs.
  + use-mt-boost.patch
- Remove python-libtorrent Obsoletes. (It's been dead for 3 releases now; and
  is just clutter.)
- Remove the blocklist plugin, at upstream's recommendation.

* Tue Jun 24 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.9.3-1
- Update to new upstream release (0.5.9.3)

* Fri May 23 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.9.1-1
- Update to new upstream release (0.5.9.1)

* Fri May 02 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.9.0-1
- Update to new upstream release (0.5.9.0)
- Drop upstreamed default-preferences patch for disabling new version
  notifications:
  - default-prefs-no-release-notifications.patch

* Tue Apr 15 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.8.9-1
- Update to new upstream release (0.5.8.9)

* Wed Mar 26 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.8.7-1
- Update to new upstream release (0.5.8.7)

* Mon Mar 17 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.8.6-1
- Update to new upstream release (0.5.8.6)

* Fri Feb 29 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.8.5-1
- Update to new upstream release (0.5.8.5)

* Sat Feb 16 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.8.4-1
- Update to new upstream release (0.5.8.4)
- Rebuild for GCC 4.3

* Mon Jan 28 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.8.3-1
- Update to new upstream security fix release (0.5.8.3), which includes a fix
  for a potential remotely-exploitable stack overflow with a malformed
  bencoded message.

* Sat Jan 19 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.8.1-1
- Update to new upstream bugfix release (0.5.8.1)

* Wed Jan 09 2008 Peter Gordon <peter@thecodergeek.com> - 0.5.8-3
- Add runtime dependency on dbus-x11 for the dbus-launch utility. Fixes bug
  428106 (Missing BR dbus-x11).
- Bump release to 3 to maintain a proper F8->F9+ upgrade path.

* Mon Dec 31 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.8-1
- Update to new upstream release (0.5.8)
- Merge Mamoru Tasaka's no-release-notification patch into the default-prefs
  patch.
  
* Sat Dec 29 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 0.5.7.98-1
- Update to new upstream release candidate (0.5.8 RC2)

* Mon Dec 24 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 0.5.7.95-1
- Update to new upstream release candidate (0.5.8 RC1)
- Completely suppress updates notification (bug 299601, 426642)

* Sun Dec 09 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.7.1-2
- Add missing icon cache %%post and %%postun scriptlets.
- Add missing egg-info to the %%files list.

* Fri Dec 07 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.7.1-1
- Update to new upstream bug-fix release (0.5.7.1).
- Sort %%files list (aesthetic-only change).

* Wed Dec 05 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.7-3
- Fix previous %%changelog Version.
- Cleanup the installed .desktop file. Fixes bug 413101 (deluge fails to build
  in rawhide  bad .desktop file.)

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 0.5.7-2
- Rebuild for deps

* Tue Nov 24 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.7-1
- Update to new upstream release (0.5.7)

* Sat Nov 24 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.6.96-1
- Update to new upstream release candidate (0.5.7 RC2)
- Drop plugin error patch (fixed upstream):
  - plugin-not-found-OK.patch

* Sat Nov 24 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.6.95-1
- Update to new upstream release candidate (0.5.7 RC)
- Update Source0 url
- Add upstream patch to prevent dying if plugin in prefs.state is not found on
  the filesystem:
  + plugin-not-found-OK.patch

* Wed Oct 31 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.6.2-1
- Update to new upstream bug-fix release (0.5.6.2)

* Tue Oct 30 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.6.1-1
- Update to new upstream bug-fix release (0.5.6.1)
- Drop use-mt-boost build script patch (fixed upstream):
  - use-mt-boost.patch

* Sat Oct 27 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.6-1
- Update to new upstream release (0.5.6)

* Wed Oct 17 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.5.95-1
- Update to new upstream release candidate (0.5.6 RC1)

* Thu Sep 20 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.5-2
- Fix release on previous %%changelog entry.
- Disable the version update notifications by default:
  + default-prefs-no-release-notifications.patch
  (Resolves bug 299601: Deluge alerts of new versions)

* Wed Sep 12 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.5-1
- Update to new upstream release (0.5.5)

* Mon Sep 03 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.4.1.95-1
- Update to new upstream release candidate (0.5.5 RC1)

* Mon Aug 13 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.4.1-1
- Update to new upstream release (0.5.4.1)
- Build with new binutils to gain BuildID debugging goodness.

* Mon Aug 06 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.4-1
- Update to new upstream release (0.5.4)

* Fri Aug 03 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.3-2
- Update License tag (GPLv2+).
- Rebuild against new Boost libraries, adding a patch to build against the
  multi-threaded ("*-mt") libraries:
  + use-mt-boost.patch

* Wed Jul 25 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.3-1
- Update to new upstream release candidate (0.5.3)
- Drop %%ifarch invocations for 64-bit builds. The internal setup script now
  properly determines this and adds the AMD64 compiler definition if necessary.

* Fri Jul 20 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.2.90-1
- Update to new upstream release candidate (0.5.3 RC1)
- Drop stale persistence fix patch (applied upstream):
  - fix-persistence-upgrade-rhbz_247927.patch

* Wed Jul 11 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.2-2
- Add patch to fix the existence of stale persistence files by automatically
  updating the deluge.deluge module name to deluge.core, or removing them if
  empty (bug 247927):
  + fix-persistence-upgrade-rhbz_247927.patch

* Sun Jul 08 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.2-1
- Update to new upstream release (0.5.2)
- Update Summary and %%description to reflect new µTorrent-compatible Peer
  Exchange ("PEX") functionality.

* Thu Jun 07 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.0.90.2-2
- Update to new upstream release (0.5.1 Beta 2)

* Sun Apr 08 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.0-2
- Make Deluge the upgrade path of the now-orphaned python-libtorrent package.
  
* Mon Mar 12 2007 Peter Gordon <peter@thecodergeek.com> - 0.5.0-1
- Update to new upstream release (0.5.0).

* Mon Mar 12 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.99.2-1
- Update to new upstream release (0.5 RC2).
- Drop IndexError exception-handling fix (applied upstream):
  - delugegtk.py-fix-IndexError-exception-handling.patch
- Use the system libtool instead of the one from the sources to ensure
  that no unnecessary RPATH hacks are added to the final build. 

* Wed Mar 07 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.99.1-3
- Add a patch (submitted upstream) to properly catch a thrown IndexError in
  state message updates. This should resolve the bug wherein the UI stops
  updating its details and torrent listing.
  + delugegtk.py-fix-IndexError-exception-handling.patch
  
* Wed Mar 07 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.99.1-2
- Drop unneeded 64bit-python_long patch; as it seems to cause more trouble than
  it's worth. Instead, pass -DAMD64 as a compiler flag on 64-bit arches.
  - 64bit-python_long patch
  (This should fix the bug where, even though torrents are active, they are not
  shown in the GtkTreeView listing.)

* Tue Mar 06 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.99.1-1
- Update to new upstream release (0.5 RC1).
- Use rewritten setup.py instead of patching it so much, since it's easier to
  maintain across version upgrades and whatnot:
  + fixed-setup.py
- Remove the setup.py patches (no longer needed, since I'm packaging my own):
  - setup.py-dont-store-the-install-dir.patch
  - setup.py-build-against-system-libtorrent.patch

* Fri Mar 02 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.90.3-1
- Update to new upstream release (0.5 Beta 3).
- Add patch to fix storing of installation directory:
  + setup.py-dont-store-the-install-dir.patch
    (to be applied after setup.py-build-against-system-libtorrent.patch)

* Sun Feb 25 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.90.2-2
- Add patch to fix 64-bit python_long type.
  +  64bit-python_long.patch

* Sat Feb 24 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.90.2-1
- Update to new upstream release (0.5 Beta 2)
- Add patch to force building against system copy of rb_libtorrent:
  + setup.py-build-against-system-libtorrent.patch
- Remove python-libtorrent and a few other dependencies that are no longer
  used.

* Fri Feb 23 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.1-6
- Fix Source0 URL.

* Wed Feb 21 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.1-5 
- Make notify-python dependency conditional (FC6+ only)
- Strip the unneeded shebang lines from the plugin scripts, since they are not
  meant to be directly executed.

* Wed Feb 07 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.1-4
- Update .desktop file: Icon should not have the "-256" size suffix.
- Add Requires: notify-python
- Remove strict dependency on python 2.3+, since we're targetting FC5+
  only, which has 2.4+.

* Wed Jan 10 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.1-3
- Use install instead of the cp/find/chmod fiasco of earlier releases for
  clarity and proper permissions setting.
- Be more consistent about use of %%{name} and other macros in file naming as
  well as whitespace between sections.

* Sun Jan 07 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.1-2
- Bump python-libtorrent dependency to 0.3.0-4, which contains a fix for
  64-bit systems.

* Wed Jan 03 2007 Peter Gordon <peter@thecodergeek.com> - 0.4.1-1
- Initial packaging for Fedora Extras. 
