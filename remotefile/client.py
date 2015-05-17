from remotefile.runner import Runner
import logging, os, sys

def parse_args():
    from argparse import ArgumentParser

    usage = 'Usage: {} script [arguments ...] [-v] [--help]'.format(os.path.basename(__file__))
    argparser = ArgumentParser(usage=usage)
    argparser.add_argument('script', type=str, help='Path for Python script (available in S3|local)')
    argparser.add_argument('arguments', type=str, nargs='*', help='Arguments to pass to script')
    argparser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    argparser.set_defaults(verbose=False)
    return argparser.parse_args()

def main():
    args = parse_args()

    if args.verbose: logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    runner = Runner(args.script)
    runner.exec_script(*args.arguments)
