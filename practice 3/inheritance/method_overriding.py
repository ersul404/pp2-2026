class Animal:
  def speak(self):
    print("Animal sound")

class Dog(Animal):
  def speak(self):
    print("Bark")

d = Dog()
d.speak()



class Person:
  def role(self):
    print("Person")

class Student(Person):
  def role(self):
    print("Student")

s = Student()
s.role()



class Shape:
  def area(self):
    print("Unknown area")

class Square(Shape):
  def area(self):
    print(4 * 4)

sq = Square()
sq.area()



class Device:
  def turn_on(self):
    print("Device on")

class Laptop(Device):
  def turn_on(self):
    print("Laptop on")

l = Laptop()
l.turn_on()



class Game:
  def start(self):
    print("Game started")

class OnlineGame(Game):
  def start(self):
    print("Online game started")

g = OnlineGame()
g.start()