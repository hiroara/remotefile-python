from remotefile.remote_file import RemoteFile

import logging, os, sys, shlex

class Runner(RemoteFile):
    def exec_script(self, *args):
        self.enable(force=True)
        cmd = self.__build_command(args)
        logging.info('Now invoking `{}`.'.format(cmd))
        exitcode = os.system(cmd)
        if exitcode == 0:
            logging.info('Command `{}` has been successfully completed.'.format(cmd))
        else:
            logging.info('Command `{}` has been completed with error code {}.'.format(cmd, exitcode))
            sys.exit(exitcode)

    def __build_command(self, args):
        return '/usr/bin/env python {} {}'.format(self.local_path, self.__build_args(args))

    def __build_args(self, args):
        return ' '.join([shlex.quote('{}'.format(arg)) for arg in args])
