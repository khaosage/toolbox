#!/usr/bin/env python

# Gather machine information from unix like machines.

import platform, os, sys, subprocess


def get_host():
    #hostname = os.uname()[1]
    hostname = platform.uname()[1]
    print hostname

def get_kernal():
    ost = platform.uname()[0]
    kernal = platform.uname()[2]
    print ost, kernal

def get_date():
    getdate = "date"
    getdate_arg = "+%d-%m-%Y"
    subprocess.call([getdate, getdate_arg])

def get_os():
    getos = "lsb_release"
    getos_arg = "-d"
    subprocess.call([getos, getos_arg]) 

def get_product_name():
    pname = "dmidecode"
    pname_arg = "-s"
    pname_opt = "system-product-name"
    proc = subprocess.Popen(([pname, pname_arg, pname_opt]), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.stdout.read()
    error = proc.stderr.read()
    if error:
        print "dmidecode is unavailable without sudo: ", error 
    else:
        print "Output:",  output

def get_uptime():
    up = "uptime"
    proc = subprocess.Popen(([up]), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.stdout.read()
    error = proc.stderr.read()
    print "Uptime: ",  output[12:-51]

def del_dups(seq):
    seen = {}
    pos = 0
    for item in seq:
        if item not in seen:
            seen[item] = True
            seq[pos] = item
            pos += 1
    del seq[pos:]

def get_users():
    cmd = "users"
    users = subprocess.Popen(([cmd]), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = users.stdout.read()
    error = users.stderr.read()
    ulist = output.split()
    del_dups(ulist)
    for i in ulist:
        print i

def get_mem():
    f = open("/proc/meminfo", "r")
    line = f.readline()
    print line

def get_df():
    diskspace = "df"
    diskspace_arg = "-h"
    print "Gathering diskspace information %s command:\n" % diskspace
    subprocess.call([diskspace, diskspace_arg])



def main():
    get_date()
    get_host()
    get_kernal()
    get_os()
    get_product_name()
    get_uptime()
    get_users()
    get_mem()
    get_df()

if __name__ == "__main__":
    main()

