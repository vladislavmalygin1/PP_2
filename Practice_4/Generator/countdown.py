def countdown(n):
    while n >= 0:
        yield n
        n -= 1

a = int(input("Estimated time: "))
for count in countdown(a):
    print(count) 