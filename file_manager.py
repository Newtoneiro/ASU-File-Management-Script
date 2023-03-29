import os
import shutil
import filecmp

from config import Config


class FileManager:
    """
    This class is responsible for all file-related actions
    """
    def __init__(self, destination: str, source: list[str], config: Config):
        self._destination = destination
        self._source = source
        self._config = config

    def log_action(self, what: str, path: str, action: str):
        print(f"> {what:<15}: {path:<40} | {action:<30}")

    def check_file(self, path: str) -> bool:
        """
        Checks the file and returns True if the file can be copied
        """
        # Check if the file content is duplicate
        is_duplicate, duplicate_path = self.check_duplicate_content(
            file_path=path, cur_src_path=self._destination)
        if is_duplicate:
            self.log_action('Duplicate', path, 'Keeping the oldest.')
            is_older = os.path.getctime(path) > os.path.getctime(
                                                           duplicate_path)
            if is_older:
                os.remove(duplicate_path)
            return is_older

        # Check if file is empty
        if self.check_empty(file_path=path):
            self.log_action('Empty', path, 'Removing.')
            return False

        # Check if file is temporary
        if self.check_temporary(file_path=path):
            self.log_action('Temporary', path, 'Removing.')
            return False

        # Check if file name is duplicate
        is_duplicate, duplicate_path = self.check_duplicate_name(
            file_name=path.split('\\')[-1], cur_src_path=self._destination)
        if is_duplicate:
            self.log_action('Same name', path, 'Keeping the newer.')
            is_newer = os.path.getctime(path) < os.path.getctime(
                                                           duplicate_path)
            if is_newer:
                os.remove(duplicate_path)
            return is_newer

        return True

    def check_duplicate_content(self, file_path: str,
                                cur_src_path: str) -> bool:
        """
        Returns True if the file already exists in destination dir.
        """
        for filename in os.listdir(cur_src_path):
            new_path = os.path.join(cur_src_path, filename)
            if os.path.isfile(new_path):
                if filecmp.cmp(new_path, file_path):
                    return True, new_path
            else:
                return self.check_duplicate_content(file_path=file_path,
                                                    cur_src_path=new_path)
        return False, ''

    def check_empty(self, file_path: str) -> bool:
        """
        Returns True if the file is empty.
        """
        return os.stat(file_path).st_size == 0

    def check_temporary(self, file_path: str) -> bool:
        """
        Returns True if the file is temporary.
        """
        return any([file_path.endswith(ext)
                    for ext in self._config.temporary_extensions])

    def check_duplicate_name(self, file_name: str,
                             cur_src_path: str) -> bool:
        """
        Returns True if the file name already exists in destination.
        """
        for filename in os.listdir(cur_src_path):
            new_path = os.path.join(cur_src_path, filename)
            if os.path.isfile(new_path):
                if file_name == filename:
                    return True, new_path
            else:
                return self.check_duplicate_name(file_name=file_name,
                                                 cur_src_path=new_path)
        return False, ''

    def bfs_dir_structure(self, path: str):
        """
        Allows to iterate through folder structure
        """
        for filename in os.listdir(path):
            new_path = os.path.join(path, filename)
            if os.path.isfile(new_path):
                if self.check_file(new_path):
                    self.copy_file(new_path)
            else:
                self.bfs_dir_structure(path=new_path)

    def start(self):
        """
        Starts the script
        """
        for path in self._source:
            self.bfs_dir_structure(path=path)

    def copy_file(self, path: str):
        """
        Copies file from source to path relative to destination folder
        """
        destination_path = self._destination
        for level in path.split('\\')[:-1]:
            destination_path = os.path.join(destination_path, level)
            if not os.path.exists(destination_path):
                os.mkdir(destination_path)

        shutil.copy(src=path, dst=destination_path)
