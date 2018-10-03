#!/usr/bin/env python

###
# Author: Lee Parnell Thompson
# Vesion: 1.0
# make benchmark data for the given data file
# Disclaimer: I use these scripts for my own use, 
#	so caveat progtor. (let the programmer beware)
###

import sys,os,getopt,re,random
import time

### Main program
f = open("test.bin" , "w")
start = time.clock();
lt = start
b = 0
for i in range(1,300000):
	t = time.clock()
	dif = t - lt
	if ( dif ) > 1:
		print str(t) + ":" + str( (b/dif) / 1000)
		lt = t
		b = 0
	ar = random.sample(xrange(1000),10)
	s = '\n'.join( [`a` for a in ar])
	b += len(s)
	f.write(s)


    cmdstr = "%s %s < %s > %s" %(qprog,index_name,qfile , result_file)
        print cmdstr        try:
            retcode = call(cmdstr , shell=True)
            if retcode < 0:
                print >>sys.stderr, "Child was terminated by signal", -retcode
            else:
                print >>sys.stderr, "Child returned", retcode
        except OSError, e:
            print >>sys.stderr, "Execution failed:", e
