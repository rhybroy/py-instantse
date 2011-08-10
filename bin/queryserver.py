# encoding:utf-8
# authot: troycheng
# email: frostmourn716@gmail.com

import xapian
import mmseg
import json
import threading
import time
from mmseg.search import seg_title_search
from collections import defaultdict
from globaldef import slog, config
from gevent import wsgi, pool
from cgi import parse_qs, escape

# get the configuration
DB_PATH = config.getXapian("master_db")
QUERY_PAGESIZE = config.getXapian("query_pagesize")

# define search db 
SEARCH_DB = xapian.Database(DB_PATH)
SEARCH_ENQUIRE = xapian.Enquire(SEARCH_DB)

# refresh db 
def refreshDB(interval):
    while True:
        SEARCH_DB.reopen()
        slog.info("Refresh DB.")
        time.sleep(interval)

# define search function
def search(querystring, offset=0, pagesize=QUERY_PAGESIZE, enquire=SEARCH_ENQUIRE):
    # split querystring, get query
    query_list = []
    
    # parse query string
    items = defaultdict(int)
    for word in seg_title_search(querystring):
        items[word] += 1

    # get query
    for word, value in items.iteritems():
        query_item = xapian.Query(word, value)
        query_list.append(query_item)
    if 0 == len(query_list):
        return None
    elif len(query_list) != 1:
        query = xapian.Query(xapian.Query.OP_OR, query_list)
    else:
        query = query_list[0]

    # start to search
    enquire.set_query(query)
    matches = enquire.get_mset(offset, pagesize, None)
    return matches

# define the result format function
# format = {
#   "offset": the start postion,
#   "pagesize": page size,
#   "estimate": the estimate results number,
#   "size": the returned results numbrt,
#   "results": {
#       json_string,
#       json_string.
#       ...
#   }
# }
def getJson(matches, offset, pagesize):
    result_dict = {}
    result_dict['offset'] = offset
    result_dict['pagesize'] = pagesize
    result_dict['estimate'] = matches.get_matches_estimated()
    result_dict['size'] = matches.size()
    result_dict['results'] = []
    for m in matches:
        result_dict['results'].append(m.document.get_data())
    result = json.dumps(result_dict)
    return result

# define request handler for wsgi server
def queryapp(env, start_response):
    if env["PATH_INFO"] == '/':
        # get the parameters
        query_dict = parse_qs(env['QUERY_STRING'])
        query_string = query_dict.get('query',[''])[0]
        offset = query_dict.get('offset',[0])[0]
        pagesize = query_dict.get('psize',[QUERY_PAGESIZE])[0]
        if not query_string:
            slog.warning("400 Bad Request. Missing parameter.")
            start_response('400 Bad Request',[('Content-Type',\
                'text/plain')])
            return ['Bad Request! Missing Parameter']

        # escape to avoid script injection
        query_string = escape(query_string)
        offset = int(offset)
        pagesize = int(pagesize)

        # search and format
        matches = search(query_string, offset, pagesize)
        result = getJson(matches, offset, pagesize)
        slog.info("Finish. [query]: %s, [offset]: %d, [pagesize]: %d" %\
                (query_string, offset, pagesize))

        # return result
        start_response("200 OK",[('Content-Type', 'application/json'),\
                ('Content-Length',str(len(result)))])
        return [result]
    else:
        start_response('404 Not Found', [("Content-Type",'text/plain')])
        return ['Not Found']

# define the server process
def start():
    # start refresh thread 
    refresh_interval = int(config.get("refresh_interval"))
    refresh = threading.Thread(target=refreshDB, args=(refresh_interval,))
    refresh.start()

    # start the server
    host = config.get("queryserver_host")
    port = int(config.get("queryserver_port"))
    poolSize = int(config.get("queryserver_pool"))
    p = pool.Pool(poolSize)
    slog.info("Start query server on %s:%s with pool size %s" % (host, port, poolSize))
    wsgi.WSGIServer((host,port), queryapp, spawn=p).serve_forever()

if __name__ == "__main__":
    start()


