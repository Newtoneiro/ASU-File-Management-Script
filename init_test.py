import os
import shutil

dirname = os.path.dirname(__file__)

MAIN_DIR = os.path.join(dirname, 'X')
SUB_DIR_1 = os.path.join(dirname, 'Y1')
SUB_DIR_1_SUB_DIR = os.path.join(SUB_DIR_1, 'y')
SUB_DIR_2 = os.path.join(dirname, 'Y2')
SUB_DIR_3 = os.path.join(dirname, 'Y3')


def write_file(path: str, filename: str, extension: str, file_content: str):
    """
    Write the contents to the file with given parameters.
    """
    with open(
         os.path.join(path, f"{filename}.{extension}"),
         mode="w",
         encoding="utf-8") as f:

        f.write(file_content)


def clean_contents(folder: str):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


if __name__ == "__main__":
    # Clean
    for folder in (MAIN_DIR, SUB_DIR_1, SUB_DIR_2, SUB_DIR_3):
        clean_contents(folder=folder)

    # Main Folder
    write_file(MAIN_DIR, 'single', 'txt', 'Hello!')

    # SUB_DIR_1 = Y1
    write_file(SUB_DIR_1, 'bad#n\'ame', 'bad', 'Bad Filename')
    write_file(SUB_DIR_1, 'temporary', 'tmp', 'temporary')
    write_file(SUB_DIR_1, 'empty', 'empty', '')
    write_file(SUB_DIR_1, '1', 'txt', 'Hello from y1 subfolder.')
    os.mkdir(SUB_DIR_1_SUB_DIR)
    write_file(SUB_DIR_1_SUB_DIR, 'same_content', 'txt', 'same content')
    write_file(SUB_DIR_1_SUB_DIR, 'bad\'name', 'bad', 'Bad Filename')

    # SUB_DIR_2 = Y2
    write_file(SUB_DIR_2, 'same_content_diff_name', 'txt', 'same content')
    write_file(SUB_DIR_2, '2', 'txt', 'Hello from y2 subfolder.')
    write_file(SUB_DIR_2, 'temporary', '~', 'temporary')
    write_file(SUB_DIR_2, 'executable', 'exe', 'exec file')

    # SUB_DIR_3 = Y3
    write_file(SUB_DIR_3, 'same_content', 'txt', 'same content')
    write_file(SUB_DIR_3, '3', 'txt', 'Hello from y3 subfolder.')
    write_file(SUB_DIR_3, 'bad\'name', 'bad', 'Bad Filename')
    write_file(SUB_DIR_3, 'bad_permissions', 'perm', 'Weird permissions')
