def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2

c = int(input("First value: "))
d = int(input("Second value: "))
for val in squares(c, d):
    print(f"Yielded value: {val}")