fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    continue
  print(x)



for i in range(1, 11):
    if i % 2 == 0:
        continue
    print(i)



numbers = [3, -1, 5, -7, 2]

for x in numbers:
    if x < 0:
        continue
    print(x)




for _ in range(5):
    s = input()
    if s == "skip":
        continue
    print(s)




for i in range(1, 16):
    if i % 3 == 0:
        continue
    print(i)