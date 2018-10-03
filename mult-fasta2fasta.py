#!/usr/bin/env python

###
# Author: Lee Parnell Thompson
# Vesion: 1.0
# find matching fasta sequences
# Disclaimer: I use these scripts for my own use, 
#	so caveat progtor, let the programmer beware
###

import sys,os,re,getopt
## Make unix pipe commands work w/o errors
import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def usage(out):
	print >> out, "Usage: ./fastagrep.py [options] GREP_PATTERN infile"
	print >> out, "  Valid Options are"
	print >> out, "     -h : show help"
	print >> out, "Example: ./fastagrep.py -n mydata.fasta > outfile.fasta"

try:
	opts, args = getopt.gnu_getopt(sys.argv[1:],
		"h?tn", ("help","id=","seq=","show-lengths"))
except getopt.GetoptError, exc:
	print >> sys.stderr, exc.msg
	usage(sys.stderr)
	sys.exit(2)

if (len(sys.argv) - len(opts) <= 2):
	usage(sys.stderr)
	sys.exit(2)
try:
	os.path.exists(sys.argv[-1])
except IOError:
	print >> sys.stderr, "No File Exists: " + sys.argv[-1]         

# Program Variable
infile = sys.argv[-1]
grep_str = sys.argv[-2]
match_id = 1
match_seq = 1
show_seq = True
show_lengths = False
show_line_number = False
PT_BEGIN_FASTA = re.compile("^>")
PT_GREP_STR = re.compile(grep_str)
sequence = None
match = False
line_count =0
sequences = []

######### COMMAND LINE ARGUMENTS ##########
for o, a in opts:
	if o in ("-h", "--help","-?"):
		usage(sys.stdout)
		sys.exit()
	elif o == "-t":
		show_seq = False

## Sequence Class
class Sequence:
	def __init__(self):
		self.seq = ""
		self.id = ""
		self.match_line = None;
		self.length = 0

	def __str__(self):
		string = ""
		if show_line_number: string += str(self.match_line) + ":"
		string += self.id
		seqstr = ""
		if show_seq: 
		    seqstr = self.seq.replace('\n','').replace('-','')
		i = 0
		while len(seqstr) > i + 80:
		    string += seqstr[i:i+80] + "\n"
		    i += 80
		string += seqstr[i:i+80] + "\n"
		return string

	def getLength(self):
		return len(self.seq.replace('\n','').strip())

## Main program
try:
	for line in open(infile):
		line_count += 1
		## Match the id or sequence
		if re.match(PT_BEGIN_FASTA,line):
			if match:
				sequences.append(sequence)
				match = False
			sequence = Sequence()
			sequence.id = line
			if match_id and re.search(PT_GREP_STR,line):
				sequence.match_line = line_count
				match = True
		else:
			if not match and match_seq and re.search(PT_GREP_STR,line):
				match = True
				sequence.match_line = line_count
			sequence.seq += line
	if sequence:
		sequences.append(sequence)
except AttributeError:
		print >> sys.stderr, "Failure at line %d in %s.\nIs the file in fasta format?" %(line_count, infile)
##print out results
for seq in sequences:
	if show_lengths: print "%d" %seq.getLength()
	else: print "%s" %seq,
