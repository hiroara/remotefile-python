from remotefile.remote_file import RemoteFile

import logging, os, sys, shlex, subprocess, signal

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Runner:
    def __init__(self, *args, use_cache=False, **kwargs):
        self.remote = RemoteFile.build(*args, **kwargs)
        self.use_cache = use_cache

    def exec_script(self, *args, force=None):
        if force is None: force = not self.use_cache
        self.remote.enable(force=force)
        cmd = self.__build_command(args)
        logging.info('Now invoking `{}`.'.format(' '.join(cmd)))

        self.__exec(cmd, env=self.__local_env())


    def interpreter(self, force=None):
        if force is None: force = not self.use_cache
        self.remote.enable(force=force)
        cmd = ['/usr/bin/env', 'python', ]
        logging.info('Now invoking `{}`.'.format(' '.join(cmd)))

        env = self.__local_env()
        src_path = os.path.dirname(self.remote.local_path)
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = env['PYTHONPATH'] + ':{}'.format(src_path)
        else:
            env['PYTHONPATH'] = src_path

        self.__exec(cmd, env=env)

    def __exec(self, command, **kwargs):
        p = subprocess.Popen(command, **kwargs)
        delegate_signal = lambda signal, frame: p.send_signal(signal)
        signal.signal(signal.SIGINT, delegate_signal)
        signal.signal(signal.SIGTERM, delegate_signal)
        p.wait()

        if p.returncode == 0:
            logging.info('Command `{}` has been successfully completed.'.format(' '.join(command)))
        else:
            logging.info('Command `{}` has been completed with error code {}.'.format(' '.join(command), p.returncode))
            sys.exit(p.returncode)

    def __build_command(self, args):
        return list(filter(lambda s: len(s.strip()) > 0, ['/usr/bin/env', 'python', self.remote.local_path] + list(args)))

    def __local_env(self):
        env = os.environ.copy()
        if self.use_cache: env['USE_CACHE'] = '1'
        return env
