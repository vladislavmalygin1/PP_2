numbers = [1, 2, 3, 4, 5, 6]
names = ["Alice", "Bob", "Charlie"]
squared = list(map(lambda x: x**2, numbers))
indexed_names = [f"{i}: {name}" for i, name in enumerate(names)]

# zip(): Pair two lists together
# If lists are uneven, it stops at the shortest one
paired = list(zip(names, squared)) 


print(f"Enumerate: {indexed_names}\nZip: {paired}")