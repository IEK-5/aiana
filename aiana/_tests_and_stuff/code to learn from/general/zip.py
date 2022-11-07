# #
foo = (range(101))
bar = reversed(foo)

for letter, number in zip(foo, bar):
    print(letter, '->', number)
