from remotefile.remote_file import RemoteFile

import logging, os, sys, shlex, subprocess, signal

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Runner(RemoteFile):
    def exec_script(self, *args):
        self.enable(force=True)
        cmd = self.__build_command(args)
        logging.info('Now invoking `{}`.'.format(' '.join(cmd)))

        p = subprocess.Popen(cmd)
        delegate_signal = lambda signal, frame: p.send_signal(signal)
        signal.signal(signal.SIGINT, delegate_signal)
        signal.signal(signal.SIGTERM, delegate_signal)
        p.wait()

        if p.returncode == 0:
            logging.info('Command `{}` has been successfully completed.'.format(' '.join(cmd)))
        else:
            logging.info('Command `{}` has been completed with error code {}.'.format(' '.join(cmd), p.returncode))
            sys.exit(p.returncode)

    def __build_command(self, args):
        return list(filter(lambda s: len(s.strip()) > 0, ['/usr/bin/env', 'python', self.local_path] + list(args)))
