import shutil
import os


# Example 1
shutil.move("sample.txt", "parent/sample.txt")


# Example 2
os.makedirs("destination", exist_ok=True)
shutil.move("parent/sample.txt", "destination/sample.txt")


# Example 3
shutil.copy("destination/sample.txt", "destination/sample_copy.txt")


# Example 4
files = os.listdir("destination")
txt_files = [f for f in files if f.endswith(".txt")]
print(txt_files)


# Example 5
os.rename("destination/sample_copy.txt", "destination/renamed.txt")