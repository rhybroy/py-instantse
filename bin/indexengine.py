#encoding:utf-8
#author: troycheng
#email: frostmourn716@gmail.com

import xapian
import sys
import json
import time
import threading
from mmseg.search import seg_txt_2_dict
from globaldef import config, ilog, MSG_QUEUE

# get the xapian config
MASTER_DB_PATH = config.getXapian("master_db")
try:
    MASTER_DB = xapian.WritableDatabase(MASTER_DB_PATH, xapian.DB_CREATE_OR_OPEN)
except Exception,e:
    ilog.critical("Open xapian master db failed. [exception]: %s" % e)
    sys.exit(1)

# get the query interval for MSG_QUEUE
COMMIT_INTERVAL = int(config.getXapian("commit_interval"))

# define index function
# msg should be json format:
# {
#   "title": title, user name, label name etc.
#   "type": item tyoe
#   "id": item id
#   "icon"(optional): icon id, if exists, or do not set it
# }
def index(msg):
    # create document
    doc = xapian.Document()
    doc.set_data(msg)

    # index msg title
    msg_dict = json.loads(msg)
    msg_title = msg_dict.get("title")
    for word, value in seg_txt_2_dict(msg_title.encode("utf-8")).iteritems():
        doc.add_term(word, value)

    # add document to xapian database
    MASTER_DB.add_document(doc)

# commit xapian database  operations
def commit():
    while True:
        MASTER_DB.commit()
        ilog.info("Message index queries commit.")
        time.sleep(COMMIT_INTERVAL)

# define the index engine start function
def start():
    commitor = threading.Thread(target=commit)
    commitor.start()
    while True:
        try:
            msg = MSG_QUEUE.get()
            index(msg)
            ilog.info("Message index query submit. [msg]: %s" % msg)
        except Exception,e:
            if msg:
                ilog.error("Message discard because of exception.[msg]: %s" % msg) 
            ilog.error("Exception caught when submit index query.[Exception]: %s"\
                    % e)
