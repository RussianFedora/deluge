%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:		deluge
Version:	0.5.8.3
Release:	1%{?dist}
Summary:	A GTK+ BitTorrent client with support for DHT, UPnP, and PEX
Group:		Applications/Internet
License:	GPLv2+
URL:		http://deluge-torrent.org/           

Source0:	http://download.deluge-torrent.org/tarball/%{version}/%{name}-%{version}.tar.gz
## Not used for now: Deluge builds against its own internal copy of
## rb_libtorrent. See below for more details. 
# Source1:	%{name}-fixed-setup.py

Patch1: 	%{name}-default-prefs-no-release-notifications.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	boost-devel
BuildRequires:	desktop-file-utils
BuildRequires:	libtool
BuildRequires:	openssl-devel
BuildRequires:	python-devel
## Not used for now: Deluge builds against its own internal copy of
## rb_libtorrent. See below for more details. 
# BuildRequires:	rb_libtorrent-devel

Requires:	/bin/sh
Requires:	dbus-python
Requires:	dbus-x11
## Required for the proper ownership of icon dirs.
Requires:	hicolor-icon-theme
Requires:	pygtk2-libglade
Requires:	pyOpenSSL
Requires:	pyxdg
## Deluge is now using its own internal copy of rb_libtorrent, which they have
## heavily modified. Patches were sent to the upstream rb_libtorrent devs,
## and Deluge frequently re-syncs with the upstream rb_libtorrent codebase.
## Their reason for this is that there is no rasterbar-libtorrent package in
## neither Debian nor its derivatives such as Ubuntu, so they do this to make
## make it simpler to package...on Debian. @_@
## However, as of this time, it does not build against a system copy of 0.12
## or a 0.13 nightly snapshot, so this is the only way to make this software
## functional. (See also: README.Packagers in the root of the source tarball.)
# Requires:	rb_libtorrent

## The python-libtorrent bindings were produced by the same upstream authors
## as Deluge, and Deluge 0.4.x is the only package that depended on it
## (according to repoquery). Thus, it is safe to make Deluge the upgrade path
## of the python-libtorrent package since it is no longer needed (or in fact,
## even developed) as of the 0.5 series. 
Obsoletes:	python-libtorrent < 0.5

%description
Deluge is a new BitTorrent client, created using Python and GTK+. It is
intended to bring a native, full-featured client to Linux GTK+ desktop
environments such as GNOME and XFCE. It supports features such as DHT
(Distributed Hash Tables), PEX (µTorrent-compatible Peer Exchange), and UPnP
(Universal Plug-n-Play) that allow one to more easily share BitTorrent data
even from behind a router with virtually zero configuration of port-forwarding.


%prep
%setup -qn "deluge-torrent-%{version}"
## Not building against system rb_libtorrent - see above.
# install -m 0755 %{SOURCE1} ./setup.py
%patch1 -b .default-prefs-no-release-notifications


%build
## FIXME: This should really use %%{?_smp_mflags} or similar for parallel
## compilations; but the build system on this doesn't support such flags at
## this time.
CFLAGS="%{optflags}" %{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
## Fix the Icon name in the .desktop file: it shouldn't contain an extension.
sed -i -e 's/Icon=deluge.png/Icon=deluge/' %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-install --vendor fedora			\
	--dir %{buildroot}%{_datadir}/applications	\
	--copy-name-to-generic-name			\
	--add-mime-type=application/x-bittorrent	\
	--delete-original				\
	--remove-category=Application			\
	%{buildroot}%{_datadir}/applications/%{name}.desktop
%find_lang %{name}


%clean
rm -rf %{buildroot}


%files -f %{name}.lang
%defattr(-,root,root,-)
%doc LICENSE 
%{python_sitearch}/%{name}/
%{python_sitearch}/%{name}-%{version}-py2.5.egg-info
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/fedora-%{name}.desktop
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/icons/hicolor/*/apps/%{name}.png


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
