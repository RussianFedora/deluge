%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:		deluge
Version:	0.4.90.2
Release:	2%{?dist}
Summary:	A Python BitTorrent client with support for UPnP and DHT
Group:		Applications/Editors
License:	GPL
URL:		http://deluge-torrent.org/           

Source0:	http://deluge-torrent.org/downloads/%{name}-%{version}.tar.gz
Patch0:		%{name}-setup.py-build-against-system-libtorrent.patch
Patch1:		%{name}-64bit-python_long.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	desktop-file-utils
BuildRequires:	python-devel
BuildRequires:	rb_libtorrent-devel

Requires:	/bin/sh
Requires:	pyxdg
Requires:	rb_libtorrent
Requires:	pygtk2-libglade
Requires:	dbus-python

%description
Deluge is a new BitTorrent client, created using Python and GTK+. It is
intended to bring a native, full-featured client to Linux GTK+ desktop
environments such as GNOME and XFCE. It supports features such as DHT
(Distributed Hash Tables) and UPnP (Universal Plug-n-Play) that allow one to
more easily share BitTorrent data even from behind a router with virtually
zero configuration of port-forwarding.


%prep
%setup -q
%patch0 -b .use-system-libtorrent
%patch1 -b .64bit-python_long


%build
CFLAGS="%{optflags}" %{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
desktop-file-install --vendor fedora	\
	--dir %{buildroot}%{_datadir}/applications	\
	--copy-name-to-generic-name	\
	--add-mime-type=application/x-bittorrent	\
	--delete-original	\
	%{buildroot}%{_datadir}/applications/%{name}.desktop
## ...then strip the unneeded shebang lines from some of the plugins...
pushd %{buildroot}/%{python_sitearch}/%{name}/
	for FILE in delugegtk.py delugeplugins.py; do
		sed -i 1d ${FILE};
	done
popd 


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc LICENSE 
%{python_sitearch}/%{name}/
%{_datadir}/%{name}/
%{_datadir}/pixmaps/%{name}.xpm
%{_datadir}/applications/fedora-%{name}.desktop
%{_bindir}/%{name}


%post
update-desktop-database &>/dev/null ||:


%postun
update-desktop-database &> /dev/null ||:


%changelog
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
