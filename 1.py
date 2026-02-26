def f(a):
    s=0
    for i in a:
        if i%2==0:
            s+=1
    return s
a=[1,2,3,4]
print(f(a))