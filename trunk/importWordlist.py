#! usr/bin/env python

import sys
from cPickle import dump, load

def pckle(filename = 'wordlists',lists=[]):
  pickleout = open(filename,'w+b')
  for arg in lists:
    f = open(arg,'rU')
    list = []
    for line in f:
      list.append(line.strip())
    dump(list,pickleout,-1)
    f.close()
  pickleout.close()

def unpckle(filename = 'wordlists'):
  f = open(filename,'rb')
  wordlists = []
  while True:
    try:
      wordlists.append(load(f))
    except EOFError:
      break
  return wordlists

if __name__ == "__main__":
  pckle(lists=['10000.txt','BE.txt','2000.txt','censor.txt'])
  lists = unpckle()
  for list in lists:
    print len(list)
    print list[0]
    print list[1]
    print list[2]
    print list[-1]
