%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

## Since we're using a system copy of rb_libtorrent, we need to ensure that it
## is a very recent version for proper API matching.
%define	min_rblibtorrent_ver	0.14.1

Name:		deluge
Version:	1.1.2
Release:	2%{?dist}
Summary:	A GTK+ BitTorrent client with support for DHT, UPnP, and PEX
Group:		Applications/Internet
License:	GPLv2+
URL:		http://deluge-torrent.org/           

Source0:	http://download.deluge-torrent.org/source/%{version}/%{name}-%{version}.tar.bz2

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch

BuildRequires:	boost-devel
BuildRequires:	desktop-file-utils
BuildRequires:	libtool
BuildRequires:	openssl-devel
BuildRequires:	python-devel
BuildRequires:	python-setuptools
## The build script checks for the libtorrent module and skips compiling the
## in-tarball one if this is found.
BuildRequires:	rb_libtorrent-python >= %{min_rblibtorrent_ver}

Requires:	/bin/sh
Requires:	dbus-python
Requires:	dbus-x11
## Required for the proper ownership of icon dirs.
Requires:	hicolor-icon-theme
Requires:	pygtk2-libglade
Requires:	pyOpenSSL
Requires:	python-setuptools
Requires:	pyxdg
Requires:	rb_libtorrent-python >= %{min_rblibtorrent_ver}

%description
Deluge is a new BitTorrent client, created using Python and GTK+. It is
intended to bring a native, full-featured client to Linux GTK+ desktop
environments such as GNOME and XFCE. It supports features such as DHT
(Distributed Hash Tables), PEX (µTorrent-compatible Peer Exchange), and UPnP
(Universal Plug-n-Play) that allow one to more easily share BitTorrent data
even from behind a router with virtually zero configuration of port-forwarding.


%prep
%setup -qn "%{name}-%{version}"


%build
## FIXME: This should really use %%{?_smp_mflags} or similar for parallel
## compilations; but the build system on this doesn't support such flags at
## this time.
CFLAGS="%{optflags}" %{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
desktop-file-install --vendor fedora			\
	--dir %{buildroot}%{_datadir}/applications	\
	--copy-name-to-generic-name			\
	--add-mime-type=application/x-bittorrent	\
	--delete-original				\
	--remove-category=Application			\
	%{buildroot}%{_datadir}/applications/%{name}.desktop
## Remove the country flags. This is a FEDORA-SPECIFIC change.
## TODO: Perhaps instead of removing the flags entirely, we can replace that
##       single column of pixbuf renderers with text renderers that show the
##       country/locale code of the peer.
## Fedora bug: https://bugzilla.redhat.com/show_bug.cgi?id=479265
pushd %{buildroot}%{python_sitelib}/%{name}
	## FIXME: Now that we're not showing the flags and whatnot, do we
	##        still need the GeoIP data (GeoIP.dat) too?
	rm -rf data/pixmaps/flags/
popd 

## NOTE: The lang files should REEEAALLLY be in a standard place such as
##       /usr/share/locale or similar. It'd make things so much nicer for
##       the packaging. :O
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
	> %{name}.filelist
## We've got the .mo files now; but we need the rest of the files in those
## dirs. We can't just glob in the %%files, as that would add duplicate
## entries for the .mo files which we've already marked with appropriate
## %%lang-fu. 
	find ./%{python_sitelib}/deluge -not -iname '%{name}.mo' -type f \
		| sed 's:^\./::' >> %{name}.filelist
	find ./%{python_sitelib}/deluge -not -iname '%{name}.mo' -type d \
		| sed 's:^\./:%%dir :' >> %{name}.filelist	
## Now we move that list back to our sources, so that '%%files -f' can find it
## properly.
popd && mv %{buildroot}/%{name}.filelist .


%clean
rm -rf %{buildroot}


%files -f %{name}.filelist
%defattr(-,root,root,-)
%doc ChangeLog
%{python_sitelib}/%{name}-%{version}-py?.?.egg-info/
%{_bindir}/%{name}
%{_bindir}/%{name}d
%{_datadir}/applications/fedora-%{name}.desktop
%{_datadir}/pixmaps/%{name}.*
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/icons/scalable/
%{_mandir}/man?/%{name}*


%post
update-desktop-database &>/dev/null ||:
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
	%{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor ||:
fi


%postun
update-desktop-database &> /dev/null ||:
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
	%{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor ||:
fi


%changelog
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
