#!/usr/bin/env python2

"""podcastit.py

Script to build a podcast feed from arbitrary URLs found online.


"""

import cgitb
cgitb.enable(logdir='/tmp')

import json
import datetime
import dateutil
import cgi
import sys
import os
import csv

from urlparse import urlparse 
from feedgen.feed import FeedGenerator


FEEDNAME = "podcast"
FEEDTYPE = 'atom'


class PodcastitError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def add_url(url, date, urlspath):
    with open(urlspath, 'a') as file:
        writer = csv.writer(file)
        writer.writerow((date, url))


def update_feed(urlfilepath, feedpath):
    with open(urlfilepath) as file:
        reader = csv.reader(file)
        rows = [row for row in reader]

    server = os.environ["SERVER_NAME"]
    feedid = "http://{}/{}".format(server, feedpath)
    fg = FeedGenerator()
    fg.title("Audio from the interwebs")
    fg.id(feedid)

    for row in rows:
        date, url = row
        domain = urlparse(url).netloc
        title = "{} -- {}".format(domain, date)
        content = "This audio file from {} was added on {}.".format(domain, date) 

        fe = fg.add_entry()            
        fe.id(url)
        fe.title(title)
        fe.link({'href': url, 'rel' : 'enclosure'})
        fe.content(content)
        fe.published(date)
    
    if FEEDTYPE == 'atom':
        fg.atom_file(feedpath)
    else:
        fg.rss_file(feedpath)
        

def add_entry(form):
    success = True
    try:
        url = form.getfirst('url')
        if url is None:
            raise PodcastitError("No URL was specified")
            
        feedname = form.getfirst('feedname', FEEDNAME)       
        urlfilename = feedname + '.csv'
        feedfilename = feedname + '.xml' 
        now = datetime.datetime.now(dateutil.tz.tzutc())
        add_url(url, now, urlfilename)
        update_feed(urlfilename, feedfilename)
        message = "URL was added to feed"
    except PodcastitError as e:
        success = False
        message = e.msg

    message = "URL successfully added to feed"
    result = {'status'  : success,
              'message' : message }
    return json.dumps(result)


def main():
    form = cgi.FieldStorage()
    result = add_entry(form)
    print 'Content-Type: application/json; charset=utf-8\n\n' 
    print result


if __name__ == "__main__":
    sys.exit(main())
