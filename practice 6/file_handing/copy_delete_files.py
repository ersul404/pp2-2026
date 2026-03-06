import shutil
import os


# Example 1
shutil.copy("sample.txt", "copy_sample.txt")


# Example 2
os.makedirs("backup", exist_ok=True)
shutil.copy("sample.txt", "backup/sample.txt")


# Example 3
shutil.move("copy_sample.txt", "backup/copy_sample.txt")


# Example 4
if os.path.exists("backup/copy_sample.txt"):
    os.remove("backup/copy_sample.txt")


# Example 5
shutil.copytree("backup", "backup_copy", dirs_exist_ok=True)