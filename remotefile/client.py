import logging, os, sys

def parse_args():
    from argparse import ArgumentParser

    usage = 'Usage: {} script [--arguments <arguments string>] [--verbose] [--server] [--port <number>] [--region <name>] [--help]'.format(os.path.basename(__file__))
    argparser = ArgumentParser(usage=usage)
    argparser.add_argument('script', type=str, help='Path for Python script (available in S3|local)')
    argparser.add_argument('-a', '--arguments', type=str, help='Arguments to pass to script')
    argparser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    argparser.add_argument('-r region', '--region', type=str, help='AWS Region')
    argparser.set_defaults(arguments='', verbose=False, port=8000)
    return argparser.parse_args()

def main():
    args = parse_args()

    if args.verbose: logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    from remotefile.runner import Runner
    Runner(args.script, cache_dir='/tmp/src', region_name=args.region).exec_script(*args.arguments.split(' '))
