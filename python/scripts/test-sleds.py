#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import re
import paramiko
import socket
import time
import optparse
import sys
import smtplib
import yaml


class Unbuffered(object):

    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)

sys.stdout = Unbuffered(sys.stdout)


class SshClient:
    TIMEOUT = 4

    def __init__(self, host, username, key=None, passphrase=None):
        self.username = username
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, username=username, timeout=self.TIMEOUT)

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def execute(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        b = stdout.readlines()
        for description in b:
            return(description)


class ManageIP:

    def __init__(self, ip):
        self.ip = ip.split('.')[0:4]

    def bmc_ip(self):
        self.bmc_ip = "{0}.{1}.{2}.{3}".format(self.ip[0], self.ip[1],
                                               0, self.ip[3])
        return self.bmc_ip

    def mgt_ip(self):
        self.mgt_ip = "{0}.{1}.{2}.{3}".format(self.ip[0], self.ip[1],
                                               1, self.ip[3])
        return self.mgt_ip

    def __getitem__(self, key):
        return self.ip[key]

    def __setitem__(self, key, value):
        self.ip[key] = value

    def generate_hosts(self, range_start, range_finish):
        self.hosts = []
        i = self.ip
        for a in range(range_start, range_finish):
            address = "{0}.{1}.{2}.{3}".format(i[0], i[1], i[2], a)
            self.hosts.append(address)
        return self.hosts


def optional_arg(arg_default):
    def func(option, opt_str, value, parser):
        if parser.rargs and not parser.rargs[0].startswith('-'):
            val = parser.rargs[0]
            parser.rargs.pop(0)
        else:
            val = arg_default
        setattr(parser.values, option.dest, val)
    return func


def main():

    print("Connecting to Management Server this may take some time.")

    bmc_hosts = []
    host_summary = {}
    boot_delay = 120
    shutdown_delay = 30

    try:
        mgt_pipe = SshClient(host=mgt, username=ssh_user)
    except socket.error, (msg):
        if mgt_pipe:
            print("Unable to connect {}".format(msg))
            sys.exit(1)
    except paramiko.AuthenticationException, (val, msg):
        if mgt_pipe:
            print("\n{} requires elevated privilages to run.\n".format(msg))
            sys.exit(1)

    for ip in ManageIP(mgt).generate_hosts(11, 13):
        i = ManageIP(ip)
        bmc_hosts.append(i.bmc_ip())

    if ssh_user == 'root':
        bmc_info = "/opt/dell/tools/bmc-info "
        bmc_power = "/opt/dell/tools/bmc-power "
    else:
        bmc_info = "sudo /opt/dell/tools/bmc-info "
        bmc_power = "sudo /opt/dell/tools/bmc-power "

    server_status = []
    d_results = {}
    powered_off = []

    for host in bmc_hosts:
        command = bmc_info + host
        server_status.append(mgt_pipe.execute(command))
    server_status = [x.encode('UTF8') for x in server_status]
    server_status = [s.lstrip() for s in server_status]

    for i, value in enumerate(server_status):
        server_status[i] = value.split(":")[0]

    for result in server_status:
        status = result.split("power")[1].strip()
        ip = result.split(" ")[0]
        d_results[ip] = status

    for k, value in d_results.iteritems():
        if value == 'off':
            powered_off.append(k)

    message = """
Total Hosts: {lb}
Found {to} powered off. Estimating run time for tests at {ttc} mins.
Starting test on powered off sleds.
""".format(lb=len(bmc_hosts), to=len(powered_off), ttc=len(powered_off) * 3)

    print(message)

    location = mgt_pipe.execute('hostname')

    for server in powered_off:
        b = ManageIP(server).bmc_ip()
        m = ManageIP(server).mgt_ip()
        print("Testing: {s}, waiting {bd} seconds for boot.".format(s=b,
              bd=boot_delay))
        mgt_pipe.execute('{c} {i} on'.format(c=bmc_power, i=b))
        time.sleep(boot_delay)

        try:
            sled = SshClient(host=m, username=ssh_user)
        except socket.error, (msg):
            if m:
                print("Unable to connect connection {}".format(msg))
                sys.exit(1)

        hostname = sled.execute('hostname')
        if hostname is not None:
            host_summary[m] = ['ssh connection succeeded']
        else:
            host_summary[m] = ['ssh connection failed']
        print("Test completed for {server}, attempting graceful shutdown."
              .format(server=m))
        sled.execute('sudo /sbin/shutdown -h now')
        time.sleep(shutdown_delay)
        sled_status = mgt_pipe.execute("{c} {i} status".format(c=bmc_power,
                                       i=b)).split(' ')[3].strip()

        if sled_status == 'on':
            print("Sled failed to shutdown cleanly, powering off.")
            mgt_pipe.execute("{c} {i} off".format(c=bmc_power, i=b))
            time.sleep(shutdown_delay)

        sled_status = mgt_pipe.execute("{c}{i} status".format(c=bmc_power,
                                       i=b)).split(' ')[3].strip()
        host_summary[m].append("current power status {}".format(sled_status))
        sled.close()

    print("Tests Completed.")
    for key in host_summary:
        print("Results for {}".format(key))
        for items in host_summary.get(key):
            print("".ljust(2) + items)

    sender = 'donotreply@realvnc.com'
    receivers = ['systems@realvnc.com']
    hosts = str(yaml.dump(host_summary))
    message = """From: TestSleds <{user}@{host}>
To: Systems <systems.realvnc.com>
Subject: Results of Sled Tests from {location}

{results}

This is a test e-mail message.
            """.format(sender=sender, receivers=receivers, results=hosts,
                       host=socket.gethostname().split('.')[0], user=ssh_user,
                       ip=mgt, location=location)

    if send_mail is True:
        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, receivers, message)
            print("Successfully sent email")
        except SMTPException:
            print("Error: unable to send email")


if __name__ == '__main__':
    parser = optparse.OptionParser('usage: %prog -u SSH_USER -s SERVER_IP')

    parser.add_option('-u', '--user',
                      default=None,
                      type="str",
                      dest='user',
                      help='Enter the SSH user for connection with sleds.')

    parser.add_option('-s', '--server',
                      default=None,
                      type="str",
                      dest='ip',
                      help='Eneter IP of management server.')

    parser.add_option('-e', '--email',
                      action='callback',
                      callback=optional_arg('empty'),
                      dest='send_mail',
                      help='send email yes / no')

    (options, args) = parser.parse_args()

    if options.send_mail is not None:
        send_mail = True
    else:
        send_mail = False

    if not options.user:
        parser.error('Please specify -u SSH_USER\n')

    if not options.ip:
        parser.error('Please specify -s MANAGEMENT_SERVER_IP\n')

    mgt = options.ip
    ssh_user = options.user

    main()
