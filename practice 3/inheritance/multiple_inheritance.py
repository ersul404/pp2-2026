class A:
  def hello(self):
    print("Hello from A")

class B:
  def hi(self):
    print("Hi from B")

class C(A, B):
  pass

c = C()
c.hello()
c.hi()



class Fly:
  def fly(self):
    print("Flying")

class Swim:
  def swim(self):
    print("Swimming")

class Duck(Fly, Swim):
  pass

d = Duck()
d.fly()
d.swim()



class Engine:
  def start(self):
    print("Engine started")

class Radio:
  def play(self):
    print("Music playing")

class Car(Engine, Radio):
  pass

c = Car()
c.start()
c.play()



class Writer:
  def write(self):
    print("Writing")

class Reader:
  def read(self):
    print("Reading")

class Person(Writer, Reader):
  pass

p = Person()
p.write()
p.read()



class Camera:
  def take_photo(self):
    print("Photo taken")

class Phone:
  def call(self):
    print("Calling")

class Smartphone(Camera, Phone):
  pass

s = Smartphone()
s.take_photo()
s.call()