# Copyright (c) 2006 Zach Tibbitts ('zachtib') <zach@collegegeek.org>
# Heavily modified by Peter Gordon ('codergeek42') <peter@thecodergeek.com>:
# (1) Forcibly build against a system copy of libtorrent (Rasterbar's);
# (2) Don't let the build script hardcode the RPM buildroot install path in the
#  installed files.
# (3) Use proper CFLAGS (e.g., don't strip any)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.

import platform, os, os.path, glob
from distutils.core import setup, Extension
from distutils import sysconfig
import shutil
from distutils import cmd
from distutils.command.install import install as _install
from distutils.command.install_data import install_data as _install_data
from distutils.command.build import build as _build
import msgfmt

pythonVersion = platform.python_version()[0:3]

NAME		= "deluge"
FULLNAME	= "Deluge BitTorrent Client"
VERSION		= "0.5.0"
AUTHOR		= "Zach Tibbitts, Alon Zakai"
EMAIL		= "zach@collegegeek.org, kripkensteiner@gmail.com"
DESCRIPTION	= "A bittorrent client written in PyGTK"
URL		= "http://deluge-torrent.org"
LICENSE		= "GPLv2"

additions = ['-DNDEBUG', '-O2']

if pythonVersion == '2.5':
	cv_opt = sysconfig.get_config_vars()["CFLAGS"]
	for addition in additions:
		cv_opt = cv_opt + " " + addition
	sysconfig.get_config_vars()["CFLAGS"] = ' '.join(cv_opt.split())
else:
	cv_opt = sysconfig.get_config_vars()["OPT"]
	for addition in additions:
		cv_opt = cv_opt + " " + addition
	sysconfig.get_config_vars()["OPT"] = ' '.join(cv_opt.split())


deluge_core = Extension('deluge_core',
	include_dirs = [sysconfig.get_python_inc(), '/usr/include', '/usr/include/libtorrent'],
	libraries = ['boost_filesystem', 'torrent'],
	extra_compile_args = ["-Wno-missing-braces"],
	sources = ['src/deluge_core.cpp'])



class build_trans(cmd.Command):
	description = 'Compile .po files into .mo files'
	
	def initialize_options(self):
		pass

	def finalize_options(self):		
		pass

	def run(self):
		po_dir = os.path.join(os.path.dirname(__file__), 'po')
		for path, names, filenames in os.walk(po_dir):
			for f in filenames:
				if f.endswith('.po'):
					lang = f[:len(f) - 3]
					src = os.path.join(path, f)
					dest_path = os.path.join('build', 'locale', lang, 'LC_MESSAGES')
					dest = os.path.join(dest_path, 'deluge.mo')
					if not os.path.exists(dest_path):
						os.makedirs(dest_path)
					if not os.path.exists(dest):
						print 'Compiling %s' % src
						msgfmt.make(src, dest)
					else:
						src_mtime = os.stat(src)[8]
						dest_mtime = os.stat(dest)[8]
						if src_mtime > dest_mtime:
							print 'Compiling %s' % src
							msgfmt.make(src, dest)

class build(_build):
	sub_commands = _build.sub_commands + [('build_trans', None)]
	def run(self):
		_build.run(self)

class install_data(_install_data):
	def run(self):
		for lang in os.listdir('build/locale/'):
			lang_dir = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
			lang_file = os.path.join('build', 'locale', lang, 'LC_MESSAGES', 'deluge.mo')
			self.data_files.append( (lang_dir, [lang_file]) )
		_install_data.run(self)



cmdclass = {
	'build': build,
	'build_trans': build_trans,
	'install_data': install_data,
}

data = [('share/deluge/glade',  glob.glob('glade/*.glade')),
        ('share/deluge/pixmaps', glob.glob('pixmaps/*.png')),
        ('share/applications' , ['deluge.desktop']),
        ('share/pixmaps' , ['deluge.xpm'])]

for plugin in glob.glob('plugins/*'):
	data.append( ('share/deluge/' + plugin, glob.glob(plugin + '/*')) )

setup(name=NAME, fullname=FULLNAME, version=VERSION,
	author=AUTHOR, author_email=EMAIL, description=DESCRIPTION,
	url=URL, license=LICENSE,
	scripts=["scripts/deluge"],
	packages=['deluge'],
	package_dir = {'deluge': 'src'},
	data_files=data,
	ext_package='deluge',
	ext_modules=[deluge_core],
	cmdclass=cmdclass
	)