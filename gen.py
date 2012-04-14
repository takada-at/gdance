#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import random
import re
import os.path
from optparse import OptionParser
import codecs
import sys

def randget(l):
    return l[random.randint(0, len(l)-1)]

def randdict(d):
    base = 0
    res  = None
    for k,v in d.iteritems():
        base += v
        if random.randint(0, base) <= v:
            res = k
    return res

class Generator(object):
    def __init__(self, leng=2):
        self.leng = leng
        self.conc_dict = dict()
        self.sequ_dict = dict()
        self.initnodes = None
        self.nodesize   = 0
        self.seqsize    = 0
    def gen(self):
        res   = []
        pastnodes = []
        for i in range(self.leng - 1):
            pastnodes.append(self.initnodes[i])
        nodeids = list(range(self.nodesize))
        while len(res) < self.seqsize:
            nodes  = [0.0] * self.nodesize
            poses = []
            for pos in range(self.nodesize):
                pasts = map(lambda x: x[pos], pastnodes)
                nodes[pos] = self.gen_chain(pasts, self.sequ_dict[pos])
            pastnodes = pastnodes[1:]
            pastnodes.append(nodes)
            res.append(nodes)
        return res
    def gen_chain(self, nodes, dic):
        ptr = dic
        for n in nodes:
            if not n in ptr:
                ptr = ptr[randget(ptr.keys())]
            else:
                ptr = ptr[n]
        return randdict(ptr)
    def calc(self, seqdata):
        size = len(seqdata)
        chain = self.leng
        self.nodesize = len(seqdata[0])
        self.seqsize  = len(seqdata)
        self.initnodes = seqdata[0:self.leng]
        for seqid in range(size - chain + 1):
            data = seqdata[seqid]
            for nodeid, node in enumerate(data):
                if not nodeid in self.sequ_dict:
                    self.sequ_dict[nodeid] = dict()
                dic = self.sequ_dict[nodeid]
                s0node = data[nodeid]
                s0key  = s0node[1]
                ptr = dic
                if not s0key in ptr: ptr[s0key] = dict()
                ptr = ptr[s0key]
                for offset in range(1, chain-1):
                    seqid1 = seqid + offset
                    s1node = seqdata[seqid1][nodeid]
                    s1key  = s1node[1]
                    if not s1key in ptr: ptr[s1key] = dict()
                    ptr    = ptr[s1key]
                seqid2 = seqid + chain - 1
                s2node = seqdata[seqid2][nodeid]
                s2key  = s2node[1]
                if not s2key in ptr: ptr[s2key] = 0
                ptr[s2key] += 1
    def calc_conc(self, datas):
        leng = self.cleng
        dic  = self.conc_dict
        for nodeid0 in range(self.nodesize):
            for nodeid1 in range(0, nodeid0):
                data0 = datas[nodeid0]
                data1 = datas[nodeid1]
                key   = (nodeid1, nodeid0)
                if not key in dic: dic[key] = dict()
                val0 = data0[1]
                val1 = data1[1]
                if not val1 in dic[key]: dic[key][val1] = dict()
                if not val0 in dic[key][val1]: dic[key][val1][val0] = 0
                dic[key][val1][val0] += 1

def fromfile(fname):
    f = open(fname, 'rU')
    contents = []
    reg = re.compile('^MOTION')
    state = 0
    cnt = 0
    frames = []
    for line in f:
        contents.append( line.rstrip() )
        if reg.match(line):
            state = 1
        else:
            if state==1: cnt += 1
            if cnt > 2:
                state = 2
                frames.append(map(float, line.split(' ')))
    f.close()
    seqdatas = []
    orgvdict = defaultdict(list)
    for seq in frames:
        nodes = []
        for nodeid, val in enumerate(seq):
            roundv = round(val, 1)
            orgvdict[roundv].append(val)
            nodes.append((nodeid, roundv, val))
        seqdatas.append(nodes)
    gen = Generator()
    gen.calc(seqdatas)
    nseqs = gen.gen()
    for seq in nseqs:
        nseq = []
        for val in seq:
            #nseq.append(str(val))
            nseq.append(str(randget(orgvdict[val])))
        contents.append(" ".join(nseq))
    return contents
def read(fname):
    f = open(fname, 'rU')
    contents = []
    reg = re.compile('^MOTION')
    state = 0
    cnt = 0
    frames = []
    for line in f:
        contents.append( line.rstrip() )
        if reg.match(line):
            state = 1
        else:
            if state==1: cnt += 1
            if cnt > 2:
                state = 2
                frames.append(map(float, line.split(' ')))
    f.close()
    seqdatas = []
    orgvdict = defaultdict(list)
    for seq in frames:
        nodes = []
        for nodeid, val in enumerate(seq):
            roundv = round(val, 0)
            orgvdict[roundv].append(val)
            nodes.append((nodeid, roundv, val))
        seqdatas.append(nodes)
    gen = Generator()
    gen.calc(seqdatas)
    return gen
def main():
    parser = OptionParser()
    (options, args) = parser.parse_args()
    lines = fromfile(args[0])
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    for line in lines:
        print line

if __name__ == '__main__':
    main()
    #pass
