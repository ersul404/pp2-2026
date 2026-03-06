# Example 1
names = ["Ali", "John", "Sara"]

for i, name in enumerate(names):
    print(i, name)


# Example 2
for i, name in enumerate(names, start=1):
    print(i, name)


# Example 3
scores = [80, 90, 85]

for name, score in zip(names, scores):
    print(name, score)


# Example 4
combined = list(zip(names, scores))
print(combined)


# Example 5
ages = [18, 19, 20]

for name, score, age in zip(names, scores, ages):
    print(name, score, age)