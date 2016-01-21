#!/usr/bin/python
#
# Author: andrew.baldwin@realvnc.com
#
# Check the number of connections for a given postgres database.
# As a percentage of MAX_CONNECTIONS
#
# Specify -w warning percentage
#         -c critical percentage
#         -d database name
#         -u database user
#
# Released under the same terms as Sensu (the MIT license);
# see LICENSE for details.

import optparse
import psycopg2

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

def percentage(part, whole):
  return 100 * int(part)/int(whole)


def connect_database(dbname, dbuser):
    conn = psycopg2.connect('dbname={0} user={1} host=localhost'.format(dbname, dbuser))

    mcur = conn.cursor()
    mcur.execute("SHOW MAX_CONNECTIONS;")
    max_connections = mcur.fetchall()

    for m in max_connections:
        max_c = (m[0])

    ccur = conn.cursor()
    ccur.execute("SELECT count(*) FROM pg_stat_activity;")
    current_connections = ccur.fetchall()

    for m in current_connections:
        cur_c = (m[0])

    per_con = percentage(cur_c, max_c)
    return per_con


def main():
    parser = optparse.OptionParser()

    parser.add_option('-w', '--warning',
      default = None,
      type    = "int",
      dest    = 'warning',
      help    = 'Warning level percentage')

    parser.add_option('-c', '--critical',
      default = None,
      type    = "int",
      dest    = 'critical',
      help    = 'Critical level percentage',)

    parser.add_option('-d', '--database',
      default = None,
      dest    = 'dbname',
      help    = 'Database Name',)

    parser.add_option('-u', '--user',
      default = None,
      dest    = 'dbuser',
      help    = 'Database User Name',)

    (options, args) = parser.parse_args()

    if not options.dbname:
      parser.error('Please Specify a postgres database for connection')

    if not options.dbuser:
      parser.error('Please Specify a postgres user for connection')

    if not options.warning:
      parser.error('A Warning Level is required')

    if not options.critical:
      parser.error('A Critical Level is required')

    percentage_connection = connect_database(options.dbname, options.dbuser)

    if percentage_connection > options.critical:
        exit(STATE_CRITICAL)
    elif percentage_connection > options.warning:
        exit(STATE_WARNING)
    else:
        exit(STATE_OK)


if '__main__' == __name__:
  main()