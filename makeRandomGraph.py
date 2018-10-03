#!/usr/bin/env python
import os, random

s = 10
n = 100
p = 2
o = 3

count = 0

def make1():
    f = open("graph","w")
    global count
    for i in range(n):
        nedges = random.randint(0,o*2)
        for j in range(1,nedges):
            count+=1
            f.write("%d %d %d\n" %(random.randint(1,s), random.randint(1,p), random.randint(1,s)))
class Edge:
    e = -1
    v = []
    def __init__(self, e, v):
        self.e = e
        self.v.append(v)
    def get(self):
        return self.v
count =0

g = {}

def make2():
    for line in open("graph"):
        st = line.strip().split(" ")
        s,p,o = int(st[0]),int(st[1]), int(st[2])
        if g.get(s):
            print " # %s, %s, %s " %(s,p,o) 
            if (g.get(s)):
                edge = n.get(s).get(p)
                edge.add(o)
            else:
                g.get(s)[e] = Edge(p,o)
        else:
            print " : %s, %s, %s " %(s,p,o) 
            g[s] = Edge(p,o)
            
        
        
make1()
make2()

print "count = %d " %count

