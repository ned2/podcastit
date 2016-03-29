#!/usr/bin/env python3

"""podcastit.py
Author: Ned Letcher

A server side Python script to generate a bare-ones podcast feed from
arbitrary URLs

Usage:

This script runs as a serverside CGI script. To add a podcast to your
feed submit a HTTP POST or GET request to to the script with the
following form data:

url       -- Address of file to be added to the feed

feedname  -- Optional feedname. Defaults to 'podcast'.


The script will append a new entry in the file {feedname}.csv, which
is then used to generate an updated version of {feedname}.xml. Both
files are stored in the same directory the script by default.

"""

import json
import datetime
import dateutil
import cgi
import sys
import codecs
import os
import csv
import urllib.parse

from feedgen.feed import FeedGenerator

# Script Defaults

# name of feed
FEED_NAME = "podcastit"

# type of feed to generate. 'rss' is the other option
FEED_TYPE = 'atom'

# Location to store csv and xml files.  Change if you want to put
# files somewhere other than same directory of this script.
FEED_DIR = os.path.dirname(os.path.realpath(__file__))

server = os.environ["SERVER_NAME"]

# canonicaDl URL of the feed.  
FEED_ID = "http://{}/{}".format(server, FEED_NAME+'.py')

# URL of the image for the podcast
FEED_LOGO = "http://{}/{}".format(server, FEED_NAME+'.png')


class PodcastitError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def get_feed(csv_path, feed_type):
    """Writes a podcast feed based on a CSV file of URLS. 

    Parameters:
    urlfilepath -- path of CSV file containing date,url entries
    feedtype    -- type of feed, possible values: 'atom' or 'rss'

    """
    with open(csv_path, encoding='utf-8') as file:
        rows = [row for row in csv.reader(file)]

    fg = FeedGenerator()
    fg.title("Audio from the interwebs")
    fg.logo(FEED_LOGO)
    fg.id(FEED_ID)

    for row in rows:
        # for each row from CSV file, add a FeedEntry object to the
        # Feedgenerator
        date, url, title = row
        url_quoted = urllib.parse.quote(url, ':/')
        domain = urllib.parse.urlparse(url).netloc
        content = "This audio file from {} was added on {}.".format(domain, date) 
        fe = fg.add_entry()            
        fe.id(url)
        fe.title(title)
        fe.link({'href': url_quoted, 'rel' : 'enclosure'})
        fe.content(content)
        fe.published(date)

    if feed_type == 'atom':
        func = fg.atom_str
    else:
        func = fg.rss_str

    return func(pretty=True, encoding='UTF-8')


def main():
    # Need to tell server that it can print in UTF since it's not
    # attached to a terminal
    sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)

    form = cgi.FieldStorage()
    url = form.getfirst('url')
    feedname = form.getfirst('feedname', FEED_NAME)       
    csv_path = os.path.join(FEED_DIR, feedname + '.csv')
    content_type = 'xml'

    try:
        if url:
            # add the URL entry to the CSV file
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc

            if domain == "":
                raise PodcastitError("'{}' is not a valid URL".format(url))

            filename = parsed.path.split('/')[-1]
            title = form.getfirst('title', "'{}' from {}".format(filename, domain))
            date = datetime.datetime.now(dateutil.tz.tzutc())

            with open(csv_path, 'a', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow((date, url, title))

                content_type = 'json'
            content = json.dumps({'message' : 'successfully added URL'})
        else:
            feed_type = form.getfirst('feedtype', FEED_TYPE)
            if feed_type not in ('rss', 'atom'):
                raise PodcastitError("'{}' is not a valid feed type".format(feed_type))
            content = get_feed(csv_path, feed_type)
    except PodcastitError as e:
        content_type = 'json'
        content = json.dumps({'message' : e.msg})

    if content_type == 'xml':
        sys.stdout.write('Content-Type: application/xml; charset=utf-8\n\n')
        sys.stdout.write(str(content, 'utf8'))
    else:
        sys.stdout.write('Content-Type: application/json; charset=utf-8\n\n')
        sys.stdout.write(content)



if __name__ == "__main__":
    sys.exit(main())
