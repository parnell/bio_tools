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

## Make unix pipe commands work w/o errors
import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# # Get input from standard unix pipes if it exists
# if not sys.stdin.isatty():
#	  for line in sys.stdin.readlines():
#		  print line
#	  # print sys.stdin.readline()

def usage(out):
	print >> out, "Usage: "
	print >> out, "	 -n <int> : default entire dataset"
	print >> out, "	 -% <float> : default 0.9, aka 90% build, 10% query"
	print >> out, "	 -t <datatype> : default vector"
	print >> out, "		   legal options: vector fasta"
	print >> out, "Example:"
	print >> out, "	 ./make_benchmark.py -n 100 /location/of/some/data"


########## PROGRAM VARIABLES ########
n = sys.maxint
p = 0.9
t = "vector"

PT_BEGIN_FASTA = re.compile("^>")

build_points = {} #which build points to use
query_points = {} #which query points to use
nb = 0 # Number of Build Points
nq = 0 # Number of query points

######### COMMAND LINE ARGUMENTS ##########
try:
	opts, args = getopt.gnu_getopt(sys.argv[1:], "hn:t:%:", )
	for o, a in opts:
		if o in ("-h", "--help"):
			usage(sys.stdout)
			sys.exit()
		elif o == "-n": n = int(a)
		elif o == "-%": 
			p = float(a)
			if p <= 0 or p >= 1:
				print >> sys.stderr, "-% must be within (0,1)"
				usage(sys.stdout)
				sys.exit(1)
		elif o == "-t": t = a
except getopt.GetoptError, err:
	print >> sys.stderr, err
	usage(sys.stderr)
	sys.exit(2)

if (len(sys.argv) - len(opts) <= 1):
	usage(sys.stderr)
	sys.exit(1)
try:
	os.path.exists(sys.argv[-1])
except IOError:
	print >> sys.stderr, "No File Exists: " + sys.argv[-1]		   

#### PROGRAM VARIALBES PART 2 #######
infile = sys.argv[-1]

basename = os.path.basename(infile)
dirname = os.path.dirname(infile)
if dirname != "": dirname += "/"

## Vector Class
class Vector:
	def __init__(self, points):
		self.points = points

	def __str__(self):
		return ' '.join( self.points)

## Sequence Class
class Sequence:
	def __init__(self):
		self.id = ""
		self.seq = ""

	def __str__(self):
		return self.id + "\n" + self.seq.rstrip('/n')

def generateRandItems(points_found):
	global query_points, build_points, nb,nq
	
	size = min(points_found,n)
	nb = int(size * p)
	nq = size - nb

	build_points = random.sample(range(points_found),  size)

	query_points = build_points[0:nq]
	build_points = build_points[nq:]


def shouldPrint(c,data):
	global query_points, build_points
	return c in query_points or c in build_points
	
def printIt(c, data):
	global query_points, build_points
	if c in build_points:
		bf.write(data.__str__() + "\n");
	elif c in query_points:
		qf.write(data.__str__() + "\n");

def parseFasta(infile):
	sequence = None
	line_count = 0
	fasta_count = 0

	### Find the number of fasta points

	for line in open(infile):
		if re.match(PT_BEGIN_FASTA,line):
			fasta_count +=1
	generateRandItems(fasta_count)

	### Sample from the points
	fasta_count = -1
	should_print = False
	for line in open(infile):
		line_count += 1
		## Match the id or sequence
		if PT_BEGIN_FASTA.match(line):
			if should_print:
				printIt(fasta_count, sequence)
			fasta_count += 1
			should_print = shouldPrint(fasta_count,sequence)
			# print "%d  %d" %(fasta_count,should_print)
			if should_print:
				sequence = Sequence()
				sequence.id = line.strip()
		elif should_print:
			sequence.seq += line.strip()
	if sequence and should_print:
		printIt(fasta_count, sequence)

def parseVector(infile):
	line_count = -1
	for line in open(infile):
		line_count +=1
		if line_count > n: 
			break
		if line_count == 0:
			dim, npoints, o = line.split()
			generateRandItems(int(npoints))
			npoints = min (int(npoints),n)
			bf.write("%s %d %s\n" %(dim, nb, o))
			qf.write("%s %d %s\n" %(dim, nq, o))
			# print "here %s %d %f %d" %(npoints, n, p, k)
		else:
			printIt(line_count -1, Vector(line.split()))

### Main program
qf = open(dirname + "query_" + basename , "w")
bf = open(dirname + "build_" + basename , "w")

## Try to be a little smart and try to determine file type beforehand
for line in open(infile):
	if PT_BEGIN_FASTA.match(line): t = "fasta"
	break

if t == "vector":
	parseVector(infile)
elif t == "fasta":
	parseFasta(infile)
qf.close()
bf.close()
### Print stats and info
print "build file: %d points : %s" %(len(build_points), dirname + "build_" + basename)
print "query file: %d points : %s" %(len(query_points),dirname + "query_" + basename)
