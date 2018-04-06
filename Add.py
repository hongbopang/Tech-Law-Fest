from operator import add
a=[1,2,3]
b=[2,3,4]
c=[3,4,5]
k=[]
for x in range(len(a)):
    k.append(a[x]+b[x]+c[x])

print(k)
