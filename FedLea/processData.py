import random
import json

f = open("zhengqi_train.txt", 'r')
t = f.read()
l = t.split('\n')[1:-1]
for i in range(len(l)):
    l[i] = list(map(float, l[i].split('\t')))
random.shuffle(l)

f1 = open("zhengqi_A.txt", 'w')
f1.write(json.dumps(l[:len(l)//2]))

f2 = open("zhengqi_B.txt", 'w')
f2.write(json.dumps(l[len(l)//2:]))
