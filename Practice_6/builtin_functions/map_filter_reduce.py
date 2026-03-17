from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]
names = ["Alice", "Bob", "Charlie"]

squared = list(map(lambda x: x**2, numbers)) 


evens = list(filter(lambda x: x % 2 == 0, numbers)) 

total_sum = reduce(lambda x, y: x + y, numbers) # 21


indexed_names = [f"{i}: {name}" for i, name in enumerate(names)]


paired = list(zip(names, squared)) 

print(f"Squared: {squared}\nEvens: {evens}\nSum: {total_sum}")
print(f"Enumerate: {indexed_names}\nZip: {paired}")