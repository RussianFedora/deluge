%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:		deluge
Version:	0.4.1
Release:	6%{?dist}
Summary:	A Python BitTorrent client with support for UPnP and DHT
Group:		Applications/Editors
License:	GPL
URL:		http://deluge-torrent.org/           

Source0:	http://deluge-torrent.org/downloads/%{name}-%{version}.tar.gz
Source1:	%{name}.desktop
Source2:	COPYING

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch

BuildRequires:	desktop-file-utils

Requires:	/bin/sh
Requires:	pyxdg
Requires:	python-libtorrent >= 0.3.0-4
Requires:	gnome-python2-libegg
Requires:	pygtk2-libglade
Requires:	PyXML

%if 0%{?fedora} >= 6
Requires:	notify-python
%endif

%description
Deluge is a new BitTorrent client, created using Python and GTK+. It is
intended to bring a native, full-featured client to Linux GTK+ desktop
environments such as GNOME and XFCE. It supports features such as DHT
(Distributed Hash Tables) and UPnP (Universal Plug-n-Play) that allow one to
more easily share BitTorrent data even from behind a router with virtually
zero configuration of port-forwarding.


%prep
%setup -q


%build
## Nothing to build...


%install
rm -rf %{buildroot}
## Copy the necessary files...
install -p -m 0755 -d %{buildroot}%{python_sitelib}/%{name}/
install -p -m 0755 -t %{buildroot}%{python_sitelib}/%{name}/ *.py
cp -pr glade plugins pixmaps %{buildroot}%{python_sitelib}/%{name}/
install -p -D -m 0644 pixmaps/%{name}-256.png	\
	%{buildroot}%{_datadir}/pixmaps/%{name}.png 
install -p -m 0644 %{SOURCE2} ./COPYING

## ...Create the wrapper script...
echo -e '#!/bin/sh\ncd %{python_sitelib}/%{name} && exec python ./deluge.py' > %{name}-wrapper.sh 
install -D -m 0755 %{name}-wrapper.sh %{buildroot}%{_bindir}/%{name}

## ...then strip the unneeded shebang lines from the plugins...
for FILE in %{buildroot}/%{python_sitelib}/%{name}/plugins/*.py; do
	sed -i 1d ${FILE};
done  

## ...Then install the .desktop file.
desktop-file-install --vendor fedora	\
	--dir %{buildroot}%{_datadir}/applications	\
	%{SOURCE1}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
## No LICENSE or COPYING text available in the source tarball, though each
## source file has a header GPL comment block. I've submitted a bug report to
## the upstream developers about this; and they will include such a file in
## the next release of Deluge.
%doc COPYING
%{python_sitelib}/%{name}/
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/applications/fedora-%{name}.desktop
%{_bindir}/%{name}


%post
update-desktop-database &>/dev/null ||:


%postun
update-desktop-database &> /dev/null ||:


%changelog
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
