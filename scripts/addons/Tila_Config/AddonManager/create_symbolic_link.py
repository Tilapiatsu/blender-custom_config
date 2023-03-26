import sys
import argparse
import os
from Logger import Logger


class CreateSymbolicLink():
	def __init__(self, argv=''):
		self.log = Logger('CreateSymbolicLink')
		self.parse_argsv(argv[argv.index("--") + 1:])
	
	def parse_argsv(self, argv):
		self.log.info(f'Parsing Args')
		parser = argparse.ArgumentParser(
			description='This command allow you to create symbolic link with admin rights')
		
		file_group = parser.add_argument_group('File')
		file_group.add_argument('-C', '--file_to_link', nargs='+',
										 help='Files to Link',
										 required=True)
		
		args = parser.parse_args(argv)
		files = []
		for f in args.file_to_link:
			files.append(eval(f))

		self.file_to_link = files

	def create_symbolic_link(self):
		for f in self.file_to_link:
			self.log.info(f'Linking {f[0]} to {f[1]} {f[2]}')
			os.symlink(f[0], f[1], target_is_directory=f[2])
		
if __name__ == '__main__':
	print('Create Symbolic Link')
	CSL = CreateSymbolicLink(sys.argv)
	CSL.create_symbolic_link()
