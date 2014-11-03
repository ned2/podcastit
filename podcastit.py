#!/usr/bin/env python2

"""podcastit.py
Author: Ned Letcher

Script to build a podcast feed from arbitrary URLs found online.

Usage:

This script runs as a serverside CGI script. To add a podcast to your
feed submit a HTTP POST or GET request to URL where this script is run
from with the following form data:

url       -- Address of file to be added to the feed

feedname  -- Optional feedname. Defaults to 'podcast'.


The script will append a new entry in the file {feedname}.csv, which
is then used to generate an updated version of {feedname}.xml. Both
files are stored in the same directory the script is run from unless
the FEEDDIR constant is changed.

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


# name of feed
FEEDNAME = "podcast"

# type of feed to generate. 'rss' is the other option
FEEDTYPE = 'atom'

# Location to store csv and xml files.  Change if you want to put
# files somewhere other than same directory of this script.
FEEDDIR = os.path.dirname(os.path.realpath(__file__))


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
        rows = [row for row in csv.reader(file)]

    server = os.environ["SERVER_NAME"]
    feedid = "http://{0}/{1}".format(server, feedpath)
    fg = FeedGenerator()
    fg.title("Audio from the interwebs")
    fg.id(feedid)

    for row in rows:
        # for each row from CSV file, add a FeedEntry object to the
        # Feedgenerator
        date, url = row
        domain = urlparse(url).netloc
        title = "{0} -- {1}".format(domain, date)
        content = "This audio file from {0} was added on {1}.".format(domain, date) 
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
