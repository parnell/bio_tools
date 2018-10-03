#!/usr/bin/env python

###
# Author: Lee Parnell Thompson
# Vesion: 1.0
# split fasta sequences into fragments of length k
# Disclaimer: I use these scripts for my own use,
#   so caveat progtor. (let the programmer beware)
###

import sys,os,getopt,re

## Make unix pipe commands work w/o errors
import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# # Get input from standard unix pipes if it exists
# if not sys.stdin.isatty():
#     for line in sys.stdin.readlines():
#         print line
#     # print sys.stdin.readline()

def usage(out):
    print >> out, "Usage: "
    print >> out, "  -k <digit> : default 5"
    print >> out, "  --no-dups : default False"
    print >> out, "Example:"
    print >> out, "  ./fragmentmaker.py -k 6 /location/of/some/sequences"


########## PROGRAM VARIABLES ########
infile = sys.argv[-1]
k = 5
PT_BEGIN_FASTA = re.compile("^>")
no_dups = False
uniqs = {}
######### COMMAND LINE ARGUMENTS ##########
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hk:", ("no-dups"))
    for o, a in opts:
        if o in ("-h", "--help"):
            usage(sys.stdout)
            sys.exit()
        elif o == "-k": k = int(a)
        elif o == "--no-dups": no_dups = True
except getopt.GetoptError as err:
    print(err, file=sys.stderr)
    usage(sys.stderr)
    sys.exit(2)

if (len(sys.argv) - len(opts) <= 1):
    usage(sys.stderr)
    sys.exit(1)
try:
    os.path.exists(sys.argv[-1])
except IOError:
    print("No File Exists: " + sys.argv[-1], file=sys.stderr)


## Sequence Class
class Sequence:
    def __init__(self):
        self.seq = ""
        self.id = ""
        self.match_line = None
        self.length = 0

    def __str__(self):
        string = ""
        string += self.id
        string += " : " + self.seq.rstrip('/n')
        return string

    def getLength(self):
        return len(self.seq.replace('\n','').strip())

def splitSequence(sequence):
    fragments = []
    nkmers = sequence.getLength() - k +1
    for i in range(0,nkmers):
        frag = sequence.seq[i:i+k]
        if no_dups:
            if frag in uniqs:
                # print "!!!!!!!!!!!!!!!!!!!!!!!!!!!" + frag
                continue
            uniqs[frag] = 1
        fragments.append(frag)
    return fragments

def printFragments(sequence,fragments):
    i = 0
    for frag in fragments:
        print (sequence.id + " : frag " + str(i))
        print (frag)
        i+=1
## Main program
sequence = None
line_count = 0
# try:
for line in open(infile):
    line_count += 1
    ## Match the id or sequence
    if re.match(PT_BEGIN_FASTA,line):
        if sequence:
            printFragments(sequence,splitSequence(sequence))
        sequence = Sequence()
        sequence.id = line.strip()
    else:
        sequence.seq += line.strip()
if sequence:
    printFragments(sequence,splitSequence(sequence))

# except AttributeError:
#     print >> sys.stderr, "Failure at line %d in %s.\nIs the file in fasta format?" %(line_count, infile)
