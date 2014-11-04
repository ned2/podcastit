#!/usr/bin/env python

"""bookmarklet.py

A script to generate the podcastit bookmarklet. When run will create
the file bookmarklet.txt using the contents of bookmarklet.js.

Usage: 

$python bookmarklet.py SCRIPT_URL

"""

import sys

JSFILE = 'bookmarklet.js'
TXTFILE = 'bookmarklet.txt'


def make_bookmarklet(script_loc):
    with open(JSFILE) as file:
        bookmarklet = ''.join([line.strip() for line in file])

    with open(TXTFILE, 'w') as file:
        file.write(bookmarklet % (script_loc))


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) < 1:
        sys.stderr.write("SCRIPT_URL argument missing\n")
        return 2

    make_bookmarklet(argv[0])


if __name__ == "__main__":
    sys.exit(main())

