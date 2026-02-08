x = lambda a : a + 10
print(x(5))



x = lambda a, b : a * b
print(x(5, 6))



x = lambda a, b, c : a + b + c
print(x(5, 6, 2))



greet = lambda name: "Hello " + name
print(greet("Alex"))



max_two = lambda a, b: a if a > b else b
print(max_two(7, 3))