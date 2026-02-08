print(bool(False))
print(bool(None))
print(bool(0))
print(bool(""))
print(bool(()))
print(bool([]))
print(bool({}))


class myclass():
  def __len__(self):
    return 0

myobj = myclass()
print(bool(myobj))



def myFunction() :
  return True

print(myFunction())



def myFunction() :
  return True

if myFunction():
  print("YES!")
else:
  print("NO!")



x = 200
print(isinstance(x, int))