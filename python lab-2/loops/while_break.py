i = 1
while i < 6:
  print(i)
  if i == 3:
    break
  i += 1



while True:
    x = int(input())
    if x == 0:
        break
    print(x)



secret = 7

while True:
    x = int(input())
    if x == secret:
        print("Correct")
        break
    print("Try again")



total = 0

while True:
    x = int(input())
    if x < 0:
        break
    total += x

print(total)



while True:
    s = input()
    if s == "stop":
        break
    print(s)