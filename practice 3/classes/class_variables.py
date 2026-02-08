class Person:
  species = "Human"

  def __init__(self, name):
    self.name = name

p1 = Person("Emil")
p2 = Person("Anna")

print(p1.species)
print(p2.species)



class Student:
  count = 0

  def __init__(self, name):
    self.name = name
    Student.count += 1

s1 = Student("Alex")
s2 = Student("Bob")

print(Student.count)



class Car:
  wheels = 4

  def __init__(self, brand):
    self.brand = brand

c1 = Car("BMW")
c2 = Car("Audi")

print(c1.wheels)
print(c2.wheels)



class School:
  school_name = "High School"

  def __init__(self, student):
    self.student = student

s1 = School("Tom")
print(School.school_name)

School.school_name = "New School"
print(s1.school_name)



class Game:
  level = 1

g1 = Game()
g2 = Game()

g1.level = 5

print(g1.level)
print(g2.level)
print(Game.level)