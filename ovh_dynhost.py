#!/usr/bin/env python
"""
A simple script to update the OVH DynHost entry with the current external IP of this machine.
"""

import argparse
import socket
import sys

import dns.resolver
import requests



def myip():
    response = requests.get('https://httpbin.org/ip')
    response.raise_for_status()
    return response.json()["origin"]


def main():
    default_ip = myip()
    parser = argparse.ArgumentParser(prog='ovh_dynhost', description='Updates the OVH DynHost entry to the current IP address.')
    parser.add_argument('domain', help='The FQDN to be updated.')
    parser.add_argument('user', help='The user id that has access to update the FQDN.')
    parser.add_argument('password', help='The password for the user id.')
    parser.add_argument('-ip', help=f'Update to this ip address instead of the current external address (default {default_ip}).', default=default_ip, metavar='x.x.x.x')
    args = parser.parse_args()

    domain = args.domain
    ip = args.ip
    user = args.user
    password = args.password

    if not check_dns(domain, ip):
        update_dns(domain, ip, user, password)
    else:
        print("Not change detected. Not updating")


def check_dns(domain, ip):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["1.1.1.1"]
    answer = resolver.resolve(domain)
    return any(ip == ip_.address for ip_ in answer)


def update_dns(domain, ip, user, password):
    queryArguments = {'system':'dyndns', 'hostname':domain, 'myip':ip}
    response = requests.get("https://www.ovh.com/nic/update", params=queryArguments, auth=(user, password))

    if response.text.startswith('good ' + ip):
        print("Update to " + ip + " successful.")
        return

    if response.text.startswith('nochg ' + ip):
        print("IP did not change")
        return

    if response.status_code == requests.codes.get(401):
        # 401 Authentification failed
        sys.stderr.write("Authentification failed. User or password is wrong.\n")
        sys.exit(-2)

    if response.status_code == requests.codes.get(403):
        # 403 Forbidden
        sys.stderr.write("Authentification is missing.\n")
        sys.exit(-3)
    
    sys.stderr.write("Update failed.\n")
    sys.exit(-1)

if __name__ == '__main__':
    main()
