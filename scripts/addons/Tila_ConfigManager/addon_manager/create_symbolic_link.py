import sys
import argparse
import os
import logging,  time, tempfile

def get_log_file():

    log_file = 'TilaConfig_' + time.strftime(f"%Y%m%d") + ".log"
    log_file = os.path.join(tempfile.gettempdir(), log_file)

    return log_file

class CreateSymbolicLink():
    def __init__(self, argv=''):
        self.log = logging
        self.parse_argsv(argv[argv.index("--") + 1:])
    
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

    def create_symbolic_link(self):
        for f in self.file_to_link:
            self.log.info(f"Linking {f[0]} -> {f[1]}")
            os.symlink(f[0], f[1], target_is_directory=f[2])
        
if __name__ == '__main__':
    log_file = get_log_file()
    timeformat = '%m/%d/%Y %I:%M:%S %p'
    f = '%(asctime)s - %(levelname)s : {} :    %(message)s'.format("TilaConfig")
    logging.basicConfig(filename=log_file, level=logging.DEBUG, datefmt=timeformat, filemode='w', format=f)

    CSL = CreateSymbolicLink(sys.argv)
    CSL.create_symbolic_link()
