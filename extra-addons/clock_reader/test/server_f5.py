#!/usr/bin/python
# -*- encoding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
#
# Permite cargar una captura de un reloj tipo F5 y comportarse como tal.
#
import SocketServer
import research
import sys
import binascii
from struct import unpack
from operator import itemgetter

class ClockServer(SocketServer.UDPServer):
    def __init__(self, server_address, request_handler_class, data):
        SocketServer.UDPServer.__init__(self, server_address,
                                        request_handler_class)
        self.data = data

class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        accept_response = self.server.data
        data = self.request[0]
        socket = self.request[1]

        if data in accept_response:
            print "len:", len(accept_response[data])
            for d in accept_response[data]:
                if not isinstance(d, bool):
                    socket.sendto(d, self.client_address)
        else:
            (rcode, rtime, rsid, rserial) = unpack("<HHHH", data[:8])
            for i in accept_response.keys():
                (ecode, etime, esid, eserial) = unpack("<HHHH", i[:8])
                if ecode == rcode and eserial == rserial and rsid == esid:
                    print "Expected: %i, Recived: %i, DTime: %i" % (etime, rtime, etime-rtime)

            print "No accepted package:", binascii.hexlify(data)

if __name__ == "__main__":
    data = research.readpackets(sys.argv[1])
    accept_response = research.accept_response(data, '192.168.1.24')
    HOST, PORT = "localhost", 9999
    print "Listening in udp://%s:%i/" % (HOST, PORT)

    packetinfo = map(lambda x: ((x, binascii.hexlify(x), repr(x)) +
                                unpack("<HHHH", x[:8])), accept_response.keys())
    packetinfo.sort(key=itemgetter(-1))
    print '\n'.join(map(lambda x: "%-40s %-55s %5i %5i %5i %5i" % x[1:],
                        packetinfo))
    print
    print [ - unpack("<HHHH", accept_response[packetinfo[i-1][0]][0][:8])[1]
           + packetinfo[i][-2] for i in xrange(1, len(packetinfo)) ]

    server = ClockServer((HOST, PORT), MyUDPHandler, accept_response)
    server.serve_forever()

