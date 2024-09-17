from Cards import *
import time
a = [1, 2, 3, None]
# b = []
# b = a[:]
# a = []
b = [item for item in a]
print(len(b))

card = LogicalCard(5, Suits.SPADE)
print(type(card))
# print (b)

start = time.time()
time.sleep(1)
end = time.time()
print(end - start)

# a = (1,1)
# b = (2,2)
# c = a + b
# print(f"{a[Suits.CLUB.value]}")