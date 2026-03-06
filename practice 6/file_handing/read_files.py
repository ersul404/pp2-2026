# Example 1
with open("sample.txt", "r") as f:
    content = f.read()
    print(content)


# Example 2
with open("sample.txt", "r") as f:
    line = f.readline()
    print(line)


# Example 3
with open("sample.txt", "r") as f:
    lines = f.readlines()
    print(lines)


# Example 4
with open("sample.txt", "r") as f:
    for line in f:
        print(line.strip())


# Example 5
with open("sample.txt", "r") as f:
    text = f.read(10)
    print(text)