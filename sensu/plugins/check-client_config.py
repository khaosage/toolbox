#!/usr/bin/python

# -*- coding: UTF-8 -*-

from __future__ import print_function
import json
import socket
import subprocess
import shlex

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3


class SensuService(object):

    def sensu_service(self, cmd):
        self.cmd = cmd
        command = "sudo service sensu-client {}".format(self.cmd)
        proc = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.stdin.close()
        return proc.stdout.read()


def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )


def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts=False):
    """
    Thanks to Mirec Miskuf
    http://stackoverflow.com/questions/956867/\
    how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python/\
    33571117#33571117
    """
    if isinstance(data, unicode):
        return data.encode('utf-8')
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    if isinstance(data, dict) and not ignore_dicts:
        return {_byteify(key, ignore_dicts=True): _byteify(value,
                ignore_dicts=True) for key, value in data.iteritems()}
    return data


def main():
    sensu_client_file = "/etc/sensu/conf.d/client.json"

    with open(sensu_client_file, 'r') as stream:
        stream_dict = json_load_byteified(stream)

    sensu_name = stream_dict.get('client').get('fqdn')
    if sensu_name:
            host_name = socket.getfqdn()
            if sensu_name == host_name:
                exit(STATE_OK)
            else:
                p = SensuService().sensu_service("stop")
                exit(STATE_WARNING)
    else:
        p = SensuService().sensu_service("stop")
        exit(STATE_WARNING)


if __name__ == '__main__':
    main()
