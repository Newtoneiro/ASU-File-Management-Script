import os
import shutil

from checks import CheckDuplicateContent, CheckDuplicateName, CheckEmpty, \
    CheckName, CheckPermissions, CheckTemporary


class FileManager:
    """
    This class is responsible for all file-related actions
    """
    def __init__(self, destination, source, config):
        self._destination = destination
        self._source = source
        self._config = config
        self._checkers = [CheckDuplicateContent(config),
                          CheckDuplicateName(config),
                          CheckEmpty(config),
                          CheckName(config),
                          CheckPermissions(config),
                          CheckTemporary(config)]

    def _check_file(self, path):
        """
        Checks the file and returns True if the file can be copied
        """
        can_be_copied = True
        for checker in self._checkers:
            checker_result = checker.check(path)
            can_be_copied = can_be_copied and checker_result

        return can_be_copied

    def _bfs_dir_structure(self, path):
        """
        Allows to iterate through folder structure
        """
        for filename in os.listdir(path):
            new_path = os.path.join(path, filename)
            if os.path.isfile(new_path):
                if self._check_file(new_path):
                    self._copy_file(new_path)
            else:
                self._bfs_dir_structure(path=new_path)

    def _copy_file(self, path):
        """
        Copies file from source to path relative to destination folder
        """
        destination_path = self._destination
        for level in path.split(os.sep)[:-1]:
            destination_path = os.path.join(destination_path, level)
            if not os.path.exists(destination_path):
                os.mkdir(destination_path)

        shutil.copy(src=path, dst=destination_path)

    def start(self):
        """
        Starts the script
        """
        for path in self._source:
            self._bfs_dir_structure(path=path)
