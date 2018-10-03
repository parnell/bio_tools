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
	print >> out, "Usage: ./convert_format.py [options] infile"
	print >> out, "  Valid Options are"
	print >> out, "     -h : show help"
	print >> out, "Example: ./convert_format.py > outfile.msf"

try:
	opts, args = getopt.gnu_getopt(sys.argv[1:],
		"h?tn", ("help","id=","input-format=","filter="))
except getopt.GetoptError, exc:
	print >> sys.stderr, exc.msg
	usage(sys.stderr)
	sys.exit(2)

if (len(sys.argv) - len(opts) <= 1):
	usage(sys.stderr)
	sys.exit(2)
try:
	os.path.exists(sys.argv[-1])
except IOError:
	print >> sys.stderr, "No File Exists: " + sys.argv[-1]         

# Program Variable
infile = sys.argv[-1]
PT_FASTA_FORMAT = re.compile("^>")
PT_STOCKHOLM_FORMAT = re.compile("STOCKHOLM")
PT_RNAFORESTER_FORMAT = re.compile("\*\*\* Scoring parameters")
PT_MSF_FORMAT = re.compile("!!.._MULTIPLE_ALIGNMENT")
PT_BLANK = re.compile("^\s*$")
PT_STCK_COMMENT = re.compile("^\s*(#|/)")
PT_STCK_SEQ = re.compile("^([\w\.\/\-]+)\s*([^\s]+)")
PT_BEGIN_FASTA = re.compile("^>")

PT_FORESTER_SCORE = re.compile("^Score: ([\d.]+)")
PT_FORESTER_MEMBERS = re.compile("^Members: (\d+)")
PT_FORESTER_FASTA = re.compile("^>(.*)")

PT_MSF_NAME = re.compile("\s*Name:\s*([^\s]+)")
PT_MSF_SEQUENCE = re.compile("^\s*([^\s]+)\s+(.*)$")

PT_FOLDALIGN_SEQUENCE = re.compile("([^\s]+)\s+([^\s\(\)\.]+)")
PT_FOLDALIGN_COMMENT = re.compile("^\s*#")

sequence = None
match = False
line_count =0
sequences = {}
FMT_FASTA = 1
FMT_STOCKHOLM = 2
FMT_MSF = 3
FMT_RNAFORESTER = 4
FMT_FOLDALIGN = 5

input_format = None

change_name = True
output_type = FMT_MSF
filter = False

filter_sequences = {}

######### COMMAND LINE ARGUMENTS ##########
for o, a in opts:
	if o in ("-h", "--help","-?"):
		usage(sys.stdout)
		sys.exit()
	elif o == "--input-format":
		if a == "foldalign":
			input_format = FMT_FOLDALIGN
	elif o == "--filter":
		filter = True


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
		if show_seq: string += self.seq.rstrip('/n')
		return string

	def getLength(self):
		return len(self.seq.replace('\n','').strip())

def parseFoldalign(infile):
	sequences = {}
	line_count = 0
	for line in open(infile):
		line_count += 1
		if re.match(PT_FOLDALIGN_COMMENT,line): 
			continue
		elif re.match(PT_FOLDALIGN_SEQUENCE,line):
			m = re.match(PT_FOLDALIGN_SEQUENCE,line)
			key = m.group(1).replace('.','_').replace('/','_')
			## There is always an alignment then secondary structure
			## so skip the secondary structure
			if key in sequences: continue
			sequences[key] = m.group(2)
	return sequences

def parseRNAForester(infile):
	# try:
	sequences = {}
	line_count = 0
	score = 0.0 ## Max scoring cluster
	members = 0
	max_member_count = 0
	max_cluster_score = 0
	seqs = {}
	for line in open(infile):
		line_count += 1
		if re.match(PT_FORESTER_SCORE, line):
			if (len(seqs) > max_member_count) or (len(seqs) == max_member_count and score > max_cluster_score):
				# print "members=%d  score=%d" %(len(seqs), score)
				max_member_count = len(seqs)
				max_cluster_score = score
			m = re.match(PT_FORESTER_SCORE, line)
			score = float(m.group(1))
			seqs = {}
		elif re.match(PT_FORESTER_FASTA, line):
			m = re.match(PT_FORESTER_FASTA, line)
			seqs[m.group(1)] = True
	line_count = 0
	in_right_cluster = False
	newfasta = None
	for line in open(infile):
		line_count += 1
		if newfasta:
			sequences[newfasta] = line.rstrip()
			newfasta = False
			continue
		if re.match(PT_FORESTER_SCORE, line):
			if in_right_cluster: ## we already got the cluster we need
				break
			m = re.match(PT_FORESTER_SCORE, line)
			if float(m.group(1)) == max_cluster_score:
				in_right_cluster = True
		elif re.match(PT_FORESTER_FASTA, line) and in_right_cluster:
			m = re.match(PT_FORESTER_FASTA, line)
			newfasta = m.group(1)
			sequences[newfasta] = ""
	# except:
	# 	print >> sys.stderr, "Failure at line %d \n" %(line_count)
	return sequences

def parseMSF(infile):
	sequences = {}
	line_count = 0
	for line in open(infile):
		if re.match(PT_MSF_NAME, line):
			m = re.match(PT_MSF_NAME, line)
			key = m.group(1).replace('.','_').replace('/','_')
			# print m.group(1)
			sequences[key] = ""
		elif re.match(PT_MSF_SEQUENCE, line):
			m = re.match(PT_MSF_SEQUENCE, line)
			key = m.group(1).replace('.','_').replace('/','_')
			if not key in sequences: continue
			# print ">>> %s %s" %(m.group(1), m.group(2))
			sequences[key] += m.group(2).replace(' ','')
	return sequences

def parseStockHolm(infile):
	sequences = {}
	try:
		line_count = 0
		for line in open(infile):
			# print line,
			line_count += 1
			## Match the id or sequence
			if re.match(PT_STCK_COMMENT,line): 
				# print "comment %s" %line, 
				pass
			elif re.match(PT_BLANK,line): 
				# print "blank %s" %line, 
				pass
			elif re.match(PT_STCK_SEQ,line): 
				m = re.match(PT_STCK_SEQ,line)
				# print "seq con",
				# print "%s %s" %(m.group(1), m.group(2))
				k = m.group(1)
				### change name from Rfam to other Rfam name
				if change_name : k = k.replace('/','_').replace('.','_')
				if k not in sequences: sequences[k] = m.group(2)
				else : sequences[k] += m.group(2)
	except AttributeError:
		print >> sys.stderr, "Failure at line %d \n" %(line_count)
	return sequences

## Main program
def findFmt(infile):
	format = None
	line_count = 0
	# print infile
	try:
		for line in open(infile):
			line_count += 1
			if line_count > 3: break
			if re.search(PT_FASTA_FORMAT,line):
				format = FMT_FASTA
				break
			elif re.search(PT_STOCKHOLM_FORMAT,line): 
				format = FMT_STOCKHOLM
				break
			elif re.search(PT_RNAFORESTER_FORMAT,line):
				format = FMT_RNAFORESTER
				break
			elif re.search(PT_MSF_FORMAT,line):
				format = FMT_MSF
				break
	except AttributeError:
		print >> sys.stderr, "Failure at line %d in %s.\nIs the file in fasta format?" %(line_count, infile)
	return format

def getSequences(infile):
	global input_format
	if input_format: format = input_format
	else : format = findFmt(infile)
	if format == FMT_STOCKHOLM :
		# print "STOCKHOLM Format"
		return parseStockHolm(infile)
	elif format == FMT_RNAFORESTER :
		# print "RNAForester Format"
		return parseRNAForester(infile)
	elif format == FMT_MSF :
		# print "RNAForester Format"
		return parseMSF(infile)
	elif format == FMT_FOLDALIGN:
		return parseFoldalign(infile)
	else:
		sys.stderr.write("no formats found\n")
		sys.exit(1)

osequences = getSequences(infile)
if filter:
	filter_sequences = getSequences(a)
	for key in osequences.keys():
		if filter_sequences.has_key(key):
			sequences[key] = osequences[key]
else :
	sequences = osequences

if len(sequences) == 0:
	sys.stderr.write("No sequences found\n")
	sys.exit(1)

##print out results
if output_type == FMT_MSF:
	print "!!NA_MULTIPLE_ALIGNMENT"
	print "%s  MSF: 207  Type: N  December 21, 2009 22:12  Check: 0  .." %(infile)
	largest_key = 0
	for k, v in sequences.iteritems():
		print " Name: %s    Len:    %d  Check: 0  Weight: 1.00" %(k,len(v))
		if len(k) > largest_key: largest_key = len(k)
	print "\n//\n\n"

	start_i = 0
	while (len(v) > start_i + 10):
		for k, v in sequences.iteritems():
			print "%s" %k,
			for i in range(1, largest_key + 5 -len(k)): sys.stdout.write(" "),
			i = start_i
			while start_i + 50 >= i + 10:
				print "%s " %v[i:i+10],
				i += 10
			print
		print 
		start_i += 50
		
