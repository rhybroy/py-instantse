#encoding:utf-8
#author: TroyCheng
#email: frostmourn716@gmail.com

import socket
import threading
import SocketServer
import sys
import struct
import time
from globaldef import MSG_QUEUE, plog, config

# used for parsing request
INT_SIZE = struct.calcsize("i")

# Attributes for TCP server
HOST = config.get("pushserver_host")
PORT = int(config.get("pushserver_port"))
REQUEST_QUEUESIZE = config.get("pushserver_queue")
    
# define the response message
RESPONSE_OK = "ok"
RESPONSE_ERR = "error"

# define the request handler
class RequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # get the message length and then get the message
        try:
            msg_len, = struct.unpack("i", self.request.recv(INT_SIZE))
            msg_body, = struct.unpack("%ds" % msg_len, self.request.recv(msg_len))
        except Exception,e:
            plog.error("Exception caught when parsing request. [Excaption]: %s"\
                    % e)
            self.request.send(RESPONSE_ERR)

        # verification
        if msg_len != len(msg_body):
            plog.error("Incorrect message, body length != msg_len. [msg_len]: %d, [msg_body]: %s"\
                    % (msg_len, msg_body))
            self.request.send(RESPONSE_ERR)

        # push message into MSG_QUEUE
        MSG_QUEUE.put(msg_body)
        plog.info("Message enqueue. [msg]: %s" % msg_body)
        self.request.send(RESPONSE_OK)

class PushServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# define the push server instance
PUSH_SERVER= PushServer((HOST, PORT), RequestHandler)

# define the server operations
def start():
    PUSH_SERVER.request_queue_size = REQUEST_QUEUESIZE
    PUSH_SERVER.serve_forever()

def stop():
    PUSH_SERVER.shutdown()

def restart():
    stopPushServer()
    startPushServer()

if __name__ == "__main__":
    print "server start"
    start()
