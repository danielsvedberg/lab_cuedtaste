counter = 0
def test():
    global counter
    counter = counter + 1
    return "hii"

for i in range(4):
    print(test())
    print(counter)