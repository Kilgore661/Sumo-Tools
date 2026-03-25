import inspect
import os
import argparse

def app_dir():
    # Get the frame of the caller
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])

    if module is None or not hasattr(module, '__file__'):
        # Fallback to current working directory
        return os.getcwd()

    # Absolute path to the caller module's directory
    return os.path.dirname(os.path.abspath(module.__file__))

def parse_args(args=None):
    if args:
        args = args[1:]

    arg_parser = argparse.ArgumentParser(description="Decode command line arguments.")

    # Define the possible arguments
    arg_parser.add_argument('num', nargs='?', type=int, help='A single number')
    arg_parser.add_argument('-s', '--start', type=int, help='Start number')
    arg_parser.add_argument('-e', '--end', type=int, help='End number')

    args = arg_parser.parse_args(args)

    # Validate the arguments based on the conditions
    if args.num is not None:
        if args.start is not None or args.end is not None:
            arg_parser.error("If <num> is provided, -s and -e cannot be used.")
        return {'num': args.num}
    elif args.start is not None and args.end is not None:
        if args.start > args.end:
            arg_parser.error("Start number must be less than or equal to end number.")
        return {'start': args.start, 'end': args.end}
    elif args.start is not None:
        return {'start': args.start}
    elif args.end is not None:
        return {'end': args.end}
    else:
        return { 'start': 1958, 'end': 2026 }

