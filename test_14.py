import modelMaker as d
from itertools import *

arr = d.get_combinations_name('weights_b25_150_', [1], 30)
print(arr)
print(len(arr))

arr = []
for i in range(1, 101):
    arr.append(i)
result = []
count = 0
for i in combinations(arr, 2):
    if (i[0]<31 or i[1]<31):
        print(i)
        count +=1
    result.append(i)

print(len(result))
print(count)
print(len(result)-count)
