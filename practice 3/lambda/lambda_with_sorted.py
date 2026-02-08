numbers = [5, 2, 8, 1, 3]

sorted_numbers = sorted(numbers, key=lambda x: x)
print(sorted_numbers)



words = ["banana", "apple", "cherry"]

sorted_by_length = sorted(words, key=lambda x: len(x))
print(sorted_by_length)



pairs = [(1, 3), (4, 1), (2, 2)]

sorted_by_second = sorted(pairs, key=lambda x: x[1])
print(sorted_by_second)



people = [{"name": "Alex", "age": 18}, {"name": "Bob", "age": 16}]

sorted_by_age = sorted(people, key=lambda x: x["age"])
print(sorted_by_age)


sorted_desc = sorted(numbers, key=lambda x: x, reverse=True)
print(sorted_desc)
