class Person:
  def __init__(self, name):
    self.name = name

class Student(Person):
  def __init__(self, name, grade):
    super().__init__(name)
    self.grade = grade

s = Student("Alex", 11)
print(s.name, s.grade)



class Animal:
  def __init__(self):
    print("Animal created")

class Dog(Animal):
  def __init__(self):
    super().__init__()
    print("Dog created")

d = Dog()



class Car:
  def __init__(self, brand):
    self.brand = brand

class ElectricCar(Car):
  def __init__(self, brand, battery):
    super().__init__(brand)
    self.battery = battery

e = ElectricCar("Tesla", 100)
print(e.brand, e.battery)



class A:
  def say(self):
    print("Hello from A")

class B(A):
  def say(self):
    super().say()
    print("Hello from B")

b = B()
b.say()



class Teacher:
  def __init__(self, subject):
    self.subject = subject

class MathTeacher(Teacher):
  def __init__(self):
    super().__init__("Math")

t = MathTeacher()
print(t.subject)