import sys
import os

from config import Config


def bfs_dir_structure(path: str, files_dict: dict[str, dict[str, int]]):
    for filename in os.listdir(path):
        new_path = os.path.join(path, filename)
        if os.path.isfile(new_path):
            files_dict[new_path] = {'O'}
        else:
            bfs_dir_structure(path=new_path, files_dict=files_dict)


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
