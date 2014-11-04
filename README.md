podcastit
======

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
