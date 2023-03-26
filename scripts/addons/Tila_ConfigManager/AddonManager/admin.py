"""Contains helpers to elevate the user rights under Windows"""
# https://github.com/0xLeon/py-elevate

from __future__ import absolute_import
from __future__ import unicode_literals

import ctypes
import sys

from builtins import str as text

__version__ = '0.0.0'


def elevate(args=None):
	"""Tries to rerun the current script with admin rights"""

	if not is_admin():
		if args is None:
			args = sys.argv

		runas(sys.executable, args)

		return False

	return True


def runas(executable, args=None):
	params = []

	if args is not None:
		for arg in args:
			if '"' in arg:
				arg = '"' + arg.replace('"', r'\"') + '"'
			elif ' ' in arg:
				arg = '"' + arg + '"'

			params.append(arg)
	
	params = text(' '.join(params))

	res = ctypes.windll.shell32.ShellExecuteW(None, "runas", text(executable), params, None, 1)

	if res <= 32:
		raise WindowsError("ShellExecute returned error code %d" % res)


def is_admin():
	"""Checks if the script is run with full admin rights"""

	return ctypes.windll.shell32.IsUserAnAdmin() == 1
