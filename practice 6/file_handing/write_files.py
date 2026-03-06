# Example 1
with open("sample.txt", "w") as f:
    f.write("Hello World\n")


# Example 2
with open("sample.txt", "w") as f:
    f.write("Line 1\n")
    f.write("Line 2\n")
    f.write("Line 3\n")


# Example 3
with open("sample.txt", "a") as f:
    f.write("New line added\n")


# Example 4
lines = ["Apple\n", "Banana\n", "Orange\n"]

with open("sample.txt", "w") as f:
    f.writelines(lines)


# Example 5
with open("new_file.txt", "x") as f:
    f.write("This file was created using x mode\n")