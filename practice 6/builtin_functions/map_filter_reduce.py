from functools import reduce


# Example 1
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x*x, numbers))
print(squares)


# Example 2
numbers = [1, 2, 3]
strings = list(map(str, numbers))
print(strings)


# Example 3
numbers = [1,2,3,4,5,6]
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)


# Example 4
greater = list(filter(lambda x: x > 3, numbers))
print(greater)


# Example 5
total = reduce(lambda a,b: a+b, numbers)
print(total)