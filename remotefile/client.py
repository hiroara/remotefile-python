import logging, os, sys

def parse_args():
    from argparse import ArgumentParser

    usage = 'Usage: {} script [--arguments <arguments string>] [--use-cache] [--verbose] [--server] [--port <number>] [--region <name>] [--help]'.format(os.path.basename(__file__))
    argparser = ArgumentParser(usage=usage)
    argparser.add_argument('script', type=str, help='Path for Python script (available in S3|local)')
    argparser.add_argument('-a', '--arguments', type=str, help='Arguments to pass to script')
    argparser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    argparser.add_argument('-r region', '--region', type=str, help='AWS Region')
    argparser.add_argument('-i', '--interpreter', help='Use Python Interpreter', action='store_true')
    argparser.add_argument('--use-cache', help='Flag to use local cache file.', action='store_true')
    argparser.set_defaults(arguments='', verbose=False, port=8000, use_cache=False, interpreter=False)
    return argparser.parse_args()

def main():
    args = parse_args()

    if args.verbose: logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    from remotefile.runner import Runner
    runner = Runner(args.script, cache_dir='/tmp/src', region_name=args.region)
    if args.interpreter:
        runner.interpreter(force=(not args.use_cache))
    else:
        runner.exec_script(*args.arguments.split(' '), force=(not args.use_cache))
