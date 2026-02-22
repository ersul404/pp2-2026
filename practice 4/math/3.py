import math

n = int(input("Input number of sides: "))
a = float(input("Input the length of a side: "))

area = (n * a * a) / (4 * math.tan(math.pi / n))

print("The area of the polygon is:", round(area))