#!/usr/bin/python
# -*- encoding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
#
# Conjunto de funciones útiles para realizar ingeniería reversa de relojes.
#
# Requiere BeautifulSoup y numpy
#
# Para realizar testing usar server.py
#

from BeautifulSoup import BeautifulStoneSoup
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import time, calendar
from numpy import *
import Image
import binascii
import struct
import pylab


def readpackets(inputfile):
    xml = open(inputfile)
    soup = BeautifulStoneSoup(xml)
    bindata = []

    for packet in soup.pdml.findAll('packet'):
        ip_src, frame_no, input_data = None, None, None
        # Get FRAME info
        for data in packet.findAll('proto', attrs={"name" : "frame"}):
            for d in data.findAll('field', attrs={'name': 'frame.number'}):
                frame_no = d['show']
            for d in data.findAll('field', attrs={'name': 'frame.time'}):
                frame_time = d['show']
        # Get IP info
        for data in packet.findAll('proto', attrs={"name" : "ip"}):
            for d in data.findAll('field', attrs={'name': 'ip.src'}):
                ip_src = d['show']
            for d in data.findAll('field', attrs={'name': 'ip.dst'}):
                ip_dst = d['show']
        # Get DATA
        for data in packet.findAll('proto', attrs={"name" : "fake-field-wrapper"}):
            input_data = data.field['value']
        bindata.append((ip_src, frame_no, frame_time, input_data != None and binascii.unhexlify(input_data)))
    return bindata

def accept_response(data, src):
    accept = {}
    key = None
    cerotime = 0
    s = []
    for (ip_src, frame_no, frame_time, input_data) in data:
        if isinstance(input_data, bool): continue
        ftime = time.strptime(frame_time[:21], "%b %d, %Y %H:%M:%S")
        #print time.strftime("%d/%m/%Y %H:%M:%S +0000", ftime)
        s.append(struct.unpack('<HIH',input_data[:8])[1])
        #frame_time = calendar.timegm() + float(frame_time[21:])
        #print frame_time, frame_time - cerotime
        cerotime = frame_time
        if ip_src == src:
            key = input_data
            accept[key] = []
        else:
            if key != None:
                accept[key].append(input_data)
    print repr(s)
    return accept

def test001():
    values01 = [64535, 1888520095, 1888520994, 1888498205, 1888501649, 1888549530, 1888488825, 1888520092, 1888513910, 1888520086, 1888520804, 1888522090, 1888521086, 1888520089, 1888522075, 1888490607,
                11912, 76867, 182364, 205151, 314031, 339632, 415884, 466069, 531555, 601066, 659126, 742818, 811015, 915812, 970693, 1006054, 1098653, 1155544, 1204586, 1249806, 1338614, 1382111, 1456999, 1525188, 1636231, 1665255, 1731637, 1792349, 1837456, 1916281, 2031056, 2063636, 2117260, 2190960, 2231952, 2302239, 2385942, 2455262, 2528200, 2566329, 2636964, 2710641, 2809480, 2833773, 2900872, 2986016, 3035176, 3118603, 3179857, 3235185, 3325764, 3396000, 3432297, 3523186, 3542453, 3618630, 3673134, 3775304, 3805337, 3912994, 3980359, 4011906, 4117263, 4158912, 4223876, 4306755, 4347971, 4401299, 4516096, 4530329, 4639957, 4678295, 4762974, 4806614, 4876436, 4916607, 4995143, 5100816, 5128006, 5214416, 5264912, 5360250, 5383444, 5461807, 5539611, 5607174, 5671205, 5757032, 5809084, 5880371, 5952658, 5998773, 6031686, 1897694988, 1888529454, 1888515116, 1888522072, 1888513398, 13102, 119222, 160824, 247815, 267922, 387328, 455915, 404021266 ]
    values02 = [64535, 6223825, 6224724, 6201935, 6205379, 6187725, 6192555, 6223822, 6217640, 6223816, 6224534, 6225820, 6224816, 6223819, 6225805, 6216537,
                34112, 76867, 182364, 205151, 314031, 339632, 415884, 466069, 531555, 601066, 659126, 742818, 811015, 915812, 970693, 1006054, 1098653, 1155544, 1204586, 1249806, 1338614, 1382111, 1456999, 1525188, 1636231, 1665255, 1731637, 1792349, 1837456, 1916281, 2031056, 2063636, 2117260, 2190960, 2231952, 2302239, 2385942, 2455262, 2528200, 2566329, 2636964, 2710641, 2809480, 2833773, 2900872, 2986016, 3035176, 3118603, 3179857, 3235185, 3325764, 3396000, 3432297, 3523186, 3542453, 3618630, 3673134, 3775304, 3805337, 3912994, 3980359, 4011906, 4117263, 4158912, 4223876, 4306755, 4347971, 4401299, 4516096, 4530329, 4635290, 442817988, 6167649, 6218846, 6225802, 6217156, 13130, 119222, 160824, 247815, 267922, 388392, 402186286, 6224531, 6225815, 6224812, 6223814, 6224812, 6223813]
    values03 = [64535, 38270440, 38271339, 38248550, 38251994, 38234340, 38239170, 38270437, 38264255, 38270431, 38271149, 38272435, 38271431, 38270434, 38272420, 38263152,
                34112, 76867, 182364, 205151, 314031, 339632, 415884, 466069, 531555, 601066, 659126, 742818, 811015, 915812, 970693, 1006054, 1098653, 1155544, 1204586, 1249806, 1338614, 1382111, 1456999, 1525188, 1636231, 1665255, 1731637, 1792349, 1837456, 1916281, 2031056, 2063636, 2117260, 2190960, 2231952, 2302239, 2385942, 2455262, 2528200, 2566329, 2636964, 2710641, 2809480, 2833773, 2900872, 2986016, 3035176, 3118603, 3179857, 3235185, 3325764, 3396000, 3432297, 3523186, 3542453, 3618630, 3673134, 3775304, 3805337, 3912994, 3980359, 4011906, 4117263, 4158912, 4223876, 4306755, 4347971, 4401299, 4516096, 4530329, 4635290, 442817988, 38214264, 38265461, 38272417, 38263771, 13130, 119222, 160824, 247815, 267922, 388392, 402186286, 38271146, 38272430, 38271427, 38270429, 38271427, 38270428]

    print len(values01), len(values02), len(values03)
    return values01, values02, values03



def tobyte(data):
    return [ eval('0x%s' % data[i:i+2]) for i in xrange(0,len(data),2) ]

def plothistogram(ips, bindata):
    for ip in ips:
        hist = [ 0 ] * 256
        stream = tobyte(bindata[ip])
        n, bins, patches = plt.hist(stream, 256, normed=1, facecolor='green', alpha=0.75)
        plt.show()

def dotplot(A, B):
    m = zeros((len(A), len(B)), dtype=int)
    for i, v in ndenumerate(m):
        if A[i[0]] == B[i[1]]:
            m[i] = 1
    return m

def align(A, B, match_score=10, mismatch_score=-10, gap_score=-1, gap='-',
          min_score=0, counts=100):
    """
    Alinea dos secuencias.

    >>> align("ABC", "ABC")
    [(['A', 'B', 'C'], ['A', 'B', 'C'], 30), (['A', 'B'], ['A', 'B'], 20)]

    >>> align("ABC", "AC")
    [(['A', 'B', 'C'], ['A', '-', 'C'], 19), (['A'], ['A'], 10)]

    >>> align("AGCACACA", "ACACACTA", match_score=2, mismatch_score=-1, gap_score=-1)
    [(['A', 'G', 'C', 'A', 'C', 'A', 'C', '-', 'A'], ['A', '-', 'C', 'A', 'C', 'A', 'C', 'T', 'A'], 12), (['A', 'G', 'C', 'A', 'C', 'A', 'C'], ['A', '-', 'C', 'A', 'C', 'A', 'C'], 11)]

    >>> align([10,20,30], [10,30], gap=-1)
    [([10, 20, 30], [10, -1, 30], 19), ([10], [10], 10)]

    """
    S = zeros((len(A)+1, len(B)+1), dtype=int) # Score matrix
    D = zeros((len(A)+1, len(B)+1), dtype=int) # Direction matrix
    d = array([[1,1],[0,1],[1,0]]) # Direction vectors
    # Generate score matrix
    for i, v in ndenumerate(S):
        if 0 in i: continue
        if A[i[0]-1] == B[i[1]-1]:
            S[i] = match_score
        else:
            S[i] = mismatch_score
        x = array([
            S[i] + S[tuple(i-d[0])],
            gap_score + S[tuple(i-d[1])],
            gap_score + S[tuple(i-d[2])]])
        di = argmax(x)
        S[i] = x[di]
        D[i] = di

    # Generate alignment sequences
    R = []
    for i in xrange(counts):
        # Select an start for a local align
        mp = unravel_index(S.argmax(), S.shape)

        # Is a valid alignment?
        if S[mp] <= min_score or A[mp[0]-1] != B[mp[1]-1]:
            continue

        # Generate align coordinates
        align=[]
        p = mp
        while S[p] > 0:
            align.append(p)
            p = tuple(p - d[D[p]])

        # Generate align string
        astr, bstr = [], []
        o = None
        for p in align:
            if o == None:
                pass
            else:
                if o[0] == p[0] and o[1] != p[1]:
                    astr.insert(0, gap)
                    bstr.insert(0, B[o[1]-1])
                elif o[0] != p[0] and o[1] == p[1]:
                    astr.insert(0, A[o[0]-1])
                    bstr.insert(0, gap)
                else:
                    astr.insert(0, A[o[0]-1])
                    bstr.insert(0, B[o[1]-1])
            o = p
        astr.insert(0, A[o[0]-1])
        bstr.insert(0, B[o[1]-1])

        R.append((astr, bstr, S[mp]))
        S[mp] = -10000

    return R

def submain_loaddata(inputfile='../data/captura01.xml'):
    bindata = readpackets(inputfile)
    idxip = {}
    idxfn = {}
    for i in xrange(len(bindata)):
        src, fno, d = bindata[i]
        if not src in idxip:
            idxip[src] = []
        idxip[src].append(i)
        idxfn[int(fno)] = i
    return idxip, idxfn, bindata

def main_dotplot():
    """
    Generate dotplot
    """
    ips, bindata, frameno = submain_loaddata()
    R = R.T
    im = Image.fromarray(uint8(R*255))
    im.save('data.png')

def main_aligndata():
    """
    Aligning data capture data width orderer data.

    > >> main_aligndata()
    """
    ips, bindata = submain_loaddata()
    S = [ 32, 236, 239, 264, 23, 239, 154, 32, 26, 18 ]
    D = tobyte(bindata['192.168.1.201'])
    print align(S, D, gap=-1, counts=5)

def main_dump_frames():
    """
    Dump frames in a file

    >> > main_dump_frames()
    """
    ips, bindata = submain_loaddata()

    for key in bindata.keys():
        i = 0
        for data in bindata[key]:
            print "Source: ", key
            print "Frame: ", i
            print data
            print
            i = i + 1
        print "---------"

def dump_clock(frames, dump=''):
    dump += framedata[8:]

def process_frame(data, c = 1):
    print data[:24]
    for i in xrange(24, len(data), 16):
        bs = [ data[j:j+2] for j in xrange(i,i+16,2) ]
        reloj = None
        tarjeta = "%04i" % eval('0x%s%s' % (bs[1], bs[0]))
        machine = None
        code = eval("0x%s" % bs[2])
        verimode = (code & 0x08 and 'Fp') or '--'
        entSal = (code & 0x20 and 'Lv') or 'At'
        try:
            dateTime = time.localtime(eval('0x%s%s%s%s' % (bs[7], bs[6], bs[5], bs[4])) +
                          940388400)
        except:
            dateTime = time.localtime(0)
#
        print "%3i" % c, ':'.join(bs), \
                reloj, tarjeta, \
                machine, verimode, \
                entSal, time.strftime("%a, %d %b %Y %H:%M:%S +0000", dateTime)
        c = c + 1
    return c

def read_frame(src, bindata):
    for ipsrc, ipfno, data in bindata:
        if ipsrc == src:
            yield binascii.unhexlify(data)

def main_process():
  count = -1
  try:
    idxip, idxfno, bindata = submain_loaddata('../data/captura01.xml')
    bindata = filter(lambda (a,b,c): a != None, bindata)
    seq = []
    for ipsrc, ipfno, data in bindata[:count]:
        print ipsrc
        data = data and data != None and struct.unpack('<HHHH',data[:8])
        if data: seq.append(data[1])

    delta = [ seq[i+1] - seq[i] for i in xrange(1, len(seq)-3) ]
    print seq
    print delta
    #pylab.plot(seq[1:])
    pylab.plot(delta)

    idxip, idxfno, bindata = submain_loaddata('../data/captura02.xml')
    bindata = filter(lambda (a,b,c): a != None, bindata)
    seq = []
    for ipsrc, ipfno, data in bindata[:count]:
        print ipsrc
        data = data and data != None and struct.unpack('<HHHH',data[:8])
        if data: seq.append(data[1])

    delta = [ seq[i+1] - seq[i] for i in xrange(1, len(seq)-3) ]
    print seq
    print delta
    #pylab.plot(seq[1:])
    pylab.plot(delta)

    pylab.show()

  except:
    import pdb; pdb.set_trace()
    raise

def test_suite():
    import doctest
    return doctest.DocTestSuite()

if __name__ == "__main__":
    main_process()
    quit()

if __name__ == "__main__":
    import unittest
    runner = unittest.TextTestRunner()
    runner.run(test_suite())


