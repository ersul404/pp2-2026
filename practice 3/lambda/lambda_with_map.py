numbers = [1, 2, 3, 4, 5]

squares = list(map(lambda x: x * x, numbers))
print(squares)


plus_one = list(map(lambda x: x + 1, numbers))
print(plus_one)


to_string = list(map(lambda x: str(x), numbers))
print(to_string)


double = list(map(lambda x: x * 2, numbers))
print(double)


is_even = list(map(lambda x: x % 2 == 0, numbers))
print(is_even)