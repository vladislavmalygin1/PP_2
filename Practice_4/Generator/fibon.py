def fibonacci_generator(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


user_input = input()
if user_input:
    n = int(user_input)
    result = ",".join(map(str, fibonacci_generator(n)))
    print(result)
