import os
import shutil
import filecmp


class CheckMethod:
    """
    Base abstract class for easier checker developement
    """
    def __init__(self,
                 config,
                 method_name,
                 default_action_str=''):
        """
        Inits with config and method name
        """
        self._config = config
        self._method_name = method_name
        self._default_action = default_action_str

    def check(self, path):
        """
        Main method, calls do_check virtual function and calls action
        if required.
        """
        result, action_path, add = self._do_check(path,
                                                  self._config.destination)
        if result:
            user_choice = 2 if self._config.batchmode else \
                self._ask_for_input(file_path=path,
                                    conflict_path=action_path,
                                    additional_log=add)
            if user_choice < 0:
                exit(0)
            elif user_choice == 0:
                return False
            elif user_choice == 1:
                return True
            else:
                return self._action(path, action_path)
        return True

    def _do_check(self, path, destination_path):
        """
        Performs check and returns True if action is required and provides
        action path as second tuple element
        """
        raise NotImplementedError()

    def _action(self, path, action_path):
        """
        Performs action and returns true if <path> file can be
        safely copied to destination folder
        """
        raise NotImplementedError()

    def _copy_file(self, path):
        """
        Copies file from source to path relative to destination folder
        """
        destination_path = self._config.destination
        for level in path.split(os.sep)[:-1]:
            destination_path = os.path.join(destination_path, level)
            if not os.path.exists(destination_path):
                os.mkdir(destination_path)

        shutil.copy(src=path, dst=destination_path)

    def _log_action(self, path, additional=""):
        """
        Logs file that didn't pass check
        """
        print(f"> {self._method_name:<20}: {path:<50}"
              + f" | DEFAULT: {self._default_action} {additional}")

    def _ask_for_input(self, file_path, conflict_path, additional_log=""):
        """
        Ask user for input for provided action
        [no - N, yes - Y, default - D, quit - Q].
        """
        CHOICES = {'y': 1, 'n': 0, 'd': 2, 'q': -1}

        conflictprompt = file_path if not conflict_path \
            else f"{file_path} with {conflict_path}"
        self._log_action(conflictprompt, additional_log)

        choice = input('Copy? >(N)o (Y)es (D)efault behaviour (Q)uit \n$')\
            .lower()
        while choice not in CHOICES.keys():
            choice = input('Copy? >(N)o (Y)es (D)efault behaviour (Q)uit \n$')
        return CHOICES[choice]


class CheckDuplicateContent(CheckMethod):
    """
    Check if file has it's duplicate in the destination folder.
    """
    def __init__(self, config):
        super().__init__(config, 'Duplicate content', 'Keeping the oldest.')

    def _do_check(self, path, destination_path):
        """
        Requires action if
        the file already exists in destination dir.
        """
        for filename in os.listdir(destination_path):
            new_path = os.path.join(destination_path, filename)
            if os.path.isfile(new_path):
                if filecmp.cmp(new_path, path):
                    older = path if os.path.getctime(path) > \
                        os.path.getctime(new_path) else new_path
                    return True, new_path, f"(Older file: {older})"
            else:
                is_duplicate, new_path, additional = self._do_check(path,
                                                                    new_path)
                if is_duplicate:
                    return is_duplicate, new_path, additional
        return False, '', ''

    def _action(self, path, action_path):
        """
        DEFAULT: Keeps the oldest of the two files.
        """
        is_older = os.path.getctime(path) > \
            os.path.getctime(action_path)
        if is_older:
            os.remove(action_path)
        return is_older


class CheckEmpty(CheckMethod):
    """
    Check if file is empty
    """
    def __init__(self, config):
        super().__init__(config, "Empty file", 'Don\'t copy.')

    def _do_check(self, path, destination_path):
        """
        Requires action if the file is empty
        """
        return os.stat(path).st_size == 0, '', ''

    def _action(self, path, action_path):
        """
        DEFAULT: Don't copy empty files
        """
        return False


class CheckTemporary(CheckMethod):
    """
    Check if file is a temporary file
    """
    def __init__(self, config):
        super().__init__(config, "TMP file", "Don\'t copy.")

    def _do_check(self, path, destination_path):
        """
        Requires action if the file is temporary
        """
        return any([path.endswith(ext)
                    for ext in self._config.temporary_extensions]), '', ''

    def _action(self, path, action_path):
        """
        DEFAULT: Don't copy tmp files
        """
        return False


class CheckDuplicateName(CheckMethod):
    """
    Check if destination folder already contains file with the same name
    """
    def __init__(self, config):
        super().__init__(config, "Duplicate name", 'Keeping the newest.')

    def _do_check(self, path, destination_path):
        """
        Requires action if the file with the same name
        already exists in destination.
        """
        file_name = path.split(os.sep)[-1]
        for filename in os.listdir(destination_path):
            new_path = os.path.join(destination_path, filename)
            if os.path.isfile(new_path):
                if file_name == filename:
                    newer = path if os.path.getctime(path) > \
                        os.path.getctime(new_path) else new_path
                    return True, new_path, f"(Newer file: {newer})"
            else:
                is_duplicate, new_path, additional = self._do_check(path,
                                                                    new_path)
                if is_duplicate:
                    return is_duplicate, new_path, additional
        return False, '', ''

    def _action(self, path, action_path):
        """
        DEFAULT: Keeps the newest of the two files.
        """
        is_newer = os.path.getctime(path) > \
            os.path.getctime(action_path)
        if is_newer:
            os.remove(action_path)
        return is_newer


class CheckPermissions(CheckMethod):
    """
    Check if file has unusual permissions
    """
    def __init__(self, config):
        super().__init__(config, "Bad Permissions", 'Change to default.')

    def _do_check(self, path, destination_path):
        """
        Requires action if the file has unusual permissions defined in config
        """
        st = os.stat(path)
        file_perms = f"{oct(st.st_mode)[-3:]}"
        if file_perms in [str(self._config.get_oct_permissions(perm))
                          for perm in self._config.unusual_permissions]:
            return True, '', ''
        return False, '', ''

    def _action(self, path, action_path):
        """
        DEFAULT: Change to default
        """
        os.chmod(path, self._config.get_oct_permissions(
                 self._config.default_permission))
        return True


class CheckName(CheckMethod):
    """
    Check if file has dangerous characters in name
    """
    def __init__(self, config):
        super().__init__(config, "Bad name", 'Replace bad chars.')

    def _do_check(self, path, destination_path):
        """
        Requires action if the file has unusual permissions defined in config
        """
        file_name = path.split(os.sep)[-1]
        if any([bad_char in file_name for
                bad_char in self._config.dangerous_characters]):

            new_file_name = file_name
            for bad_char in self._config.dangerous_characters:
                new_file_name = new_file_name.replace(
                    bad_char,
                    self._config.default_character)

            new_file_path = path.replace(file_name, new_file_name)

            return True, new_file_path, ''

        return False, '', ''

    def _action(self, path, action_path):
        """
        DEFAULT: Change to default name
        """
        os.rename(path, action_path)
        super()._copy_file(action_path)
        os.rename(action_path, path)
        return False
