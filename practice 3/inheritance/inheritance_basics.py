class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

#Use the Person class to create an object, and then execute the printname method:

x = Person("John", "Doe")
x.printname()



class Animal:
  def speak(self):
    print("Animal makes a sound")

class Dog(Animal):
  pass

d = Dog()
d.speak()



class Person:
  def walk(self):
    print("Person is walking")

class Student(Person):
  pass

s = Student()
s.walk()



class Vehicle:
  def move(self):
    print("Vehicle moves")

class Bike(Vehicle):
  pass

b = Bike()
b.move()



class Shape:
  def info(self):
    print("This is a shape")

class Circle(Shape):
  pass

c = Circle()
c.info()