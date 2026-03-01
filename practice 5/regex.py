import re


# 1. 'a' followed by zero or more 'b'
pattern1 = r"ab*"
test1 = ["a", "ab", "abb", "ac", "b"]
print("1:", [x for x in test1 if re.fullmatch(pattern1, x)])


# 2. 'a' followed by two to three 'b'
pattern2 = r"ab{2,3}"
test2 = ["ab", "abb", "abbb", "abbbb"]
print("2:", [x for x in test2 if re.fullmatch(pattern2, x)])


# 3. lowercase letters joined with underscore
pattern3 = r"\b[a-z]+_[a-z]+\b"
text3 = "hello_world test_string Bad_Test one_more_example"
print("3:", re.findall(pattern3, text3))


# 4. one uppercase followed by lowercase letters
pattern4 = r"\b[A-Z][a-z]+\b"
text4 = "Hello world USA Test A Abc"
print("4:", re.findall(pattern4, text4))


# 5. 'a' followed by anything, ending in 'b'
pattern5 = r"a.*b"
test5 = ["ab", "acb", "a123b", "a-b", "ba", "a"]
print("5:", [x for x in test5 if re.fullmatch(pattern5, x)])


# 6. replace space, comma, dot with colon
text6 = "Hello, world. This is a test"
result6 = re.sub(r"[ ,\.]", ":", text6)
print("6:", result6)


# 7. snake_case to camelCase
def snake_to_camel(s):
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])

print("7:", snake_to_camel("my_variable_name"))


# 8. split string at uppercase letters
text8 = "SplitAtUpperCase"
result8 = re.split(r"(?=[A-Z])", text8)
result8 = [x for x in result8 if x]
print("8:", result8)


# 9. insert spaces between words starting with capital letters
text9 = "HelloWorldAgain"
result9 = re.sub(r"(?<!^)(?=[A-Z])", " ", text9)
print("9:", result9)


# 10. camelCase to snake_case
def camel_to_snake(s):
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()

print("10:", camel_to_snake("camelCaseString"))
print("10:", camel_to_snake("PascalCaseString"))