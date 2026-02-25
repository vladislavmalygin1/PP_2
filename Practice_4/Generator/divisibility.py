def divisible(n):
    for i in range(n + 1):
        if i % 12 == 0:
            yield i

a = int(input("Provide a number "))
for num in divisible(a):
    print(num, end=" ") 