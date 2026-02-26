class Reverse:
    def __init__(self, data):
        self.data = data
        self.index = len(data)

    def __iter__(self):
        # An iterator must return itself
        return self

    def __next__(self):
        # Check if we have reached the start of the string
        if self.index == 0:
            raise StopIteration
        
        self.index = self.index - 1
        return self.data[self.index]

# Execution logic
try:
    user_input = input()
    rev_iter = Reverse(user_input)
    
    # We use end="" to print characters on the same line
    for char in rev_iter:
        print(char, end="")
    print() # Newline at the end
except EOFError:
    pass