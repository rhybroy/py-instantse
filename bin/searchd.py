# encoding:utf-8
# author: troycheng
# email: frostmourn716@gmail.com

import pushserver
import indexengine
import queryserver
import time
import sys
from multiprocessing import Process, Pool
from globaldef import slog, plog, ilog, MSG_QUEUE

# define the daemon process for push server, index engine and query server
push_server = Process(target=pushserver.start)
index_engine = Process(target=indexengine.start)
query_server = Process(target=queryserver.start)

def startSearchService():
    # start the push server
    push_server.start()
    message = "Push Server start in process: %d" % push_server.pid
    plog.info(message)
    print message

    # start the index engine
    index_engine.start()
    message = "Index engine start in process: %d" % index_engine.pid
    ilog.info(message)
    print message

    # start the query server
    query_server.start()
    message = "Query server start in process: %d" % query_server.pid
    slog.info(message)
    print message

if __name__ == "__main__":
    if 2 == len(sys.argv):
        if "start" == sys.argv[1]:
            startSearchService()
        else:
            print "Wrong parameter."
    else:
        print "Usage: %s start|stop" % sys.argv[0]

