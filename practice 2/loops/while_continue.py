i = 0
while i < 6:
  i += 1
  if i == 3:
    continue
  print(i)



while True:
    x = int(input())
    if x == 0:
        continue
    print(x)



x = int(input())

while x != 0:
    if x < 0:
        x = int(input())
        continue
    print(x)
    x = int(input())




i = 0

while i < 10:
    i += 1
    if i % 2 == 0:
        continue
    print(i)




while True:
    s = input()
    if s == "skip":
        continue
    if s == "stop":
        break
    print(s)