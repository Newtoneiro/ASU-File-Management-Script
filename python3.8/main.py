import sys
import os
import argparse

from config import Config
from file_manager import FileManager


def check_path(path):
    """
    Checks if path exists.
    """
    if not os.path.exists(path=path):
        print(f"==| Path {path} does not exist. |==")
        exit(-1)
    return path


def get_arguments():
    """
    Provide and check command line arguments.
    """
    parser = argparse.ArgumentParser(prog='main',
                                     description='What the program does')
    parser.add_argument('-d',
                        '--destination',
                        required=True)
    parser.add_argument('-s',
                        '--source',
                        nargs='+',
                        required=True)
    parser.add_argument('-b',
                        '--batchmode',
                        action='store_true')

    args = parser.parse_args()

    destination_dir = check_path(args.destination)
    source_dirs = [check_path(path=path) for path in args.source]

    return destination_dir, source_dirs, args.batchmode


if __name__ == "__main__":
    destination, source, batchmode = get_arguments()
    config = Config(destination, source, batchmode)
    file_manager = FileManager(destination=destination,
                               source=source,
                               config=config)
    file_manager.start()
