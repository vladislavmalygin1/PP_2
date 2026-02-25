def generator(n):
    for i in range(n):
        yield i ** 2


for sq in generator(5):
    print(sq)  