import os


# Example 1
os.mkdir("test_dir")


# Example 2
os.makedirs("parent/child", exist_ok=True)


# Example 3
print(os.getcwd())


# Example 4
files = os.listdir(".")
print(files)


# Example 5
os.chdir("parent")
print("Now in:", os.getcwd())