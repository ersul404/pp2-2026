fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)
  if x == "banana":
    break



fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    break
  print(x)



for i in range(1, 10):
    if i == 5:
        break
    print(i)



numbers = [3, 7, 2, 9, 5]

for x in numbers:
    if x == 9:
        print("Found")
        break




for _ in range(100):
    s = input()
    if s == "stop":
        break
    print(s)