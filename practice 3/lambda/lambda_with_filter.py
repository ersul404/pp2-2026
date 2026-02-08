numbers = [1, 2, 3, 4, 5, 6]

evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)


greater_than_three = list(filter(lambda x: x > 3, numbers))
print(greater_than_three)


odd_numbers = list(filter(lambda x: x % 2 != 0, numbers))
print(odd_numbers)


positive = list(filter(lambda x: x > 0, [-2, -1, 0, 1, 2]))
print(positive)


short_words = list(filter(lambda x: len(x) < 4, ["cat", "elephant", "dog"]))
print(short_words)