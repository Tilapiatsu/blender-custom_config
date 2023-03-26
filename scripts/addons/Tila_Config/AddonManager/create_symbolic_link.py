import sys
import argparse
import os


class CreateSymbolicLink():
	def __init__(self, argv=''):
		self.parse_argsv(argv[argv.index("--") + 1:])
		# self.log = Logger(addon_name='Import Command', print=self.print_debug)
	
	def parse_argsv(self, argv):
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

		print(self.file_to_link)
	
	def create_symbolic_link(self):
		print('CA MARCHE')
	
		for f in self.file_to_link:
			os.symlink(f[0], f[1], target_is_directory=f[2])
		


if __name__ == '__main__':
	print('Create Symbolic Link')
	CSL = CreateSymbolicLink(sys.argv)
	CSL.create_symbolic_link()
