import math

a = int(input())
b = int(input())

area = (a * b**2) / (4 * math.tan(math.pi / a))

print(f"Input number of sides: {a}")
print(f"Input the length of a side: {b}")
print(f"The area of the polygon is: {area:.0f}")