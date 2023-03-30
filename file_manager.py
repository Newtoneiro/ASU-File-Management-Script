import os
import shutil
import filecmp

from config import Config
from checks import CheckDuplicateContent


class FileManager:
    """
    This class is responsible for all file-related actions
    """
    def __init__(self, destination: str, source: list[str], config: Config):
        self._destination = destination
        self._source = source
        self._config = config

    def _log_action(self, what: str, path: str, action: str):
        print(f"> {what:<15}: {path:<40} | {action:<30}")

    def _check_file(self, path: str) -> bool:
        """
        Checks the file and returns True if the file can be copied
        """
        # # Check if the file content is duplicate
        # is_duplicate, duplicate_path = self._check_duplicate_content(
        #     file_path=path, cur_src_path=self._destination)
        # if is_duplicate:
        #     self._log_action('Duplicate', path, 'Keeping the oldest.')
        #     is_older = os.path.getctime(path) > os.path.getctime(
        #                                                    duplicate_path)
        #     if is_older:
        #         os.remove(duplicate_path)
        #     return is_older

        check = CheckDuplicateContent()
        action = check.check(path, self._destination)
        if action:
            return True

        # Check if file is empty
        if self._check_empty(file_path=path):
            self._log_action('Empty', path, 'Removing.')
            return False

        # Check if file is temporary
        if self._check_temporary(file_path=path):
            self._log_action('Temporary', path, 'Removing.')
            return False

        # Check if file name is duplicate
        is_duplicate, duplicate_path = self._check_duplicate_name(
            path=path, cur_src_path=self._destination)
        if is_duplicate:
            self._log_action('Same name', path, 'Keeping the newer.')
            is_newer = os.path.getctime(path) > \
                os.path.getctime(duplicate_path)
            if is_newer:
                os.remove(duplicate_path)
            return is_newer

        # Check if file has unusual permissions
        if self._check_permissions(path=path):
            self._log_action('Permissions', path, 'Changing to default.')
            os.chmod(path, self._config.get_oct_permissions(
                self._config.default_permission))

        # Check if the file name contains bad characters
        is_bad, new_path = self._check_name(file_path=path)
        if is_bad:
            self._log_action('Bad name', path, 'Replacing bad chars.')
            os.rename(path, new_path)
            self._copy_file(new_path)
            os.rename(new_path, path)
            return False

        return True

    def _check_duplicate_content(self, file_path: str,
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
                return self._check_duplicate_content(file_path=file_path,
                                                     cur_src_path=new_path)
        return False, ''

    def _check_empty(self, file_path: str) -> bool:
        """
        Returns True if the file is empty.
        """
        return os.stat(file_path).st_size == 0

    def _check_temporary(self, file_path: str) -> bool:
        """
        Returns True if the file is temporary.
        """
        return any([file_path.endswith(ext)
                    for ext in self._config.temporary_extensions])

    def _check_duplicate_name(self, path: str,
                              cur_src_path: str) -> tuple[bool, str]:
        """
        Returns True if the file name already exists in destination.
        """
        file_name = path.split(os.sep)[-1]
        for filename in os.listdir(cur_src_path):
            new_path = os.path.join(cur_src_path, filename)
            if os.path.isfile(new_path):
                if file_name == filename:
                    return True, new_path
            else:
                return self._check_duplicate_name(path=file_name,
                                                  cur_src_path=new_path)
        return False, ''

    def _check_permissions(self, path: str) -> bool:
        """
        Returns True if the file has unusual permissions defined in config
        """
        st = os.stat(path)
        file_perms = f"{oct(st.st_mode)[-3:]}"
        if file_perms in [str(self._config.get_oct_permissions(perm))
                          for perm in self._config.unusual_permissions]:
            return True
        return False

    def _check_name(self, file_path: str) -> tuple[bool, str]:
        """
        Returns True if the file has unusual permissions defined in config
        """
        file_name = file_path.split(os.sep)[-1]
        if any([bad_char in file_name for
                bad_char in self._config.dangerous_characters]):

            new_file_name = file_name
            for bad_char in self._config.dangerous_characters:
                new_file_name = new_file_name.replace(
                    bad_char,
                    self._config.default_character)

            new_file_path = file_path.replace(file_name, new_file_name)

            return True, new_file_path

        return False, ''

    def _bfs_dir_structure(self, path: str):
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

    def _copy_file(self, path: str):
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
