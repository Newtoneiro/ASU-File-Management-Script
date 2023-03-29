import sys
import os

from config import Config
from file_manager import FileManager


def check_path(path: str) -> str:
    """
    Checks if path exists.
    """
    if not os.path.exists(path=path):
        print(f"==| Path {path} does not exist. |==")
        exit(-1)
    return path


def get_arguments() -> tuple[str, list[str]]:
    """
    Provide and check command line arguments.
    """
    if len(sys.argv) < 2:
        print("== |No destination directory and source directories given. |==")
        sys.exit(-1)
    elif len(sys.argv) < 3:
        print("==| No source directories given. |==")
        sys.exit(-1)

    destination_dir = check_path(sys.argv[1])
    source_dirs = [check_path(path=path) for path in sys.argv[2:]]

    return destination_dir, source_dirs


if __name__ == "__main__":
    destination, source = get_arguments()
    config = Config()
    file_manager = FileManager(destination=destination,
                               source=source,
                               config=config)
    file_manager.start()
