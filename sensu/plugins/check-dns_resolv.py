#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import socket
import optparse


STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3


def main():
    parser = optparse.OptionParser()

    parser.add_option('-d', '--domain',
                      default="google.com",
                      type="str",
                      dest='domain',
                      help='Domain URL for testing dns resolution')

    parser.add_option('-a', '--altdomain',
                      default="bbc.com",
                      type="str",
                      dest='altdomain',
                      help='Domain URL for testing dns resolution')

    (options, args) = parser.parse_args()

    if not options.domain:
        parser.error('Please Specify a domain')

    if not options.altdomain:
        parser.error('Please Specify a domain')

    addr_a, addr_b = None, None

    try:
        addr_a = socket.gethostbyname(options.domain)
    except socket.gaierror:
        pass

    try:
        addr_b = socket.gethostbyname(options.altdomain)
    except socket.gaierror:
        pass

    if addr_a:
        print("Passed Address 1 OK")
        exit(STATE_OK)
    elif addr_b:
        print("Passed Address 2 OK")
        exit(STATE_OK)
    else:
        print("CRITICAL")
        exit(STATE_CRITICAL)


if __name__ == '__main__':
    main()
