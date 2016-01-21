#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import psycopg2
import sys
import time
import socket

con = None
query = '''SELECT count(*), case coalesce(assignee, 'unassigned')  when 'unassigned' then 'unassigned' when 'ID12007' then 'mb' else assignee end as assignee FROM
        jiraissue WHERE project = '10150' AND NOT issuestatus='6' AND NOT issuestatus='5' GROUP BY assignee'''

tsnow = int(time.time())
users = ['ajr', 'das', 'aw2', 'jw', 'ct2', 'ab2', 'mb', 'unassigned']
d = {}
carbon_server = '10.11.20.200'
carbon_port = 2003


def main():
    try:
        con = psycopg2.connect(database='jiradb', user='postgres')
        cur = con.cursor()
        cur.execute(query)
        tuplist = cur.fetchall()
        for (item) in tuplist:
            d[item[1]] = int(item[0])
        for user in users:
            if user not in d:
                d[user] = 0

    except psycopg2.DatabaseError, e:
        print('Error %s' % e)
        sys.exit(1)

    finally:
        if con:
            con.close()

    sock = socket.socket()
    sock.connect((carbon_server, carbon_port))
    for key, value in d.iteritems():
        content = "systems.tickets.jira.{k}.open {v} {t}\n".format(k=key, v=value, t=tsnow)
        sock.sendall(content)
    sock.close()


if __name__ == "__main__":
    main()
