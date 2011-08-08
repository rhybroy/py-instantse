#encoding:utf-8
#author: troycheng
#email: frostmourn716@gmail.com

import struct
import socket
import sys
import json
from globaldef import config

HOST = config.get("pushserver_host")
PORT = int(config.get("pushserver_port"))

# The function used for client
def packMsg(message):
    msg_len = len(message)
    msg_fmt = "i%ds" % msg_len 
    msg = struct.pack(msg_fmt, msg_len, message)
    return msg

def send(message):
    msg = packMsg(message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.send(msg)
    response = sock.recv(1024)
    print "response: %s" %response
    sock.close()

if __name__ == "__main__":
    if 2 == len(sys.argv):
        title = sys.argv[1]
        msg_dict = {
                "title": title,
                "type": 1,
                "id": 1,
                "icon": "1231asfqwf2r1"
                }
        msg = json.dumps(msg_dict)
        send(msg)
    else:
        print "Usage: python %s 'input title'." % sys.argv[0]
