#! /usr/bin/env python3
"""
A simple script to update the OVH DynHost entry with the current external IP of this machine.
"""

import argparse
import ipgetter
import requests
import socket
import sys

def main():
	parser = argparse.ArgumentParser(prog='ovh_dynhost', description='Updates the OVH DynHost entry to the current IP address.')
	parser.add_argument('domain', help='The FQDN to be updated.')
	parser.add_argument('user', help='The user id that has access to update the FQDN.')
	parser.add_argument('password', help='The password for the user id.')
	parser.add_argument('-ip', help='Update to this ip address instead of the current external address.', default=ipgetter.myip(), metavar='x.x.x.x')
	args = parser.parse_args()
	
	domain = args.domain
	ip = args.ip
	user = args.user
	password = args.password
	
	if not check_dns(domain, ip):
		update_dns(domain, ip, user, password)
	else:
		sys.stdout.write("IP did not change.\n")

def check_dns(domain, ip):
	addr_info = socket.getaddrinfo(domain, 80)
	for i in range(len(addr_info)):
		if addr_info[i][4][0] == ip:
			return True
		
	return False

def update_dns(domain, ip, user, password):
	queryArguments = {'system':'dyndns', 'hostname':domain, 'myip':ip}
	response = requests.get("https://www.ovh.com/nic/update", params=queryArguments, auth=(user, password))
	if response.text.startswith('good ' + ip):
			sys.stdout.write("Update to " + ip + " successful.\n")
			sys.exit(0)
	elif response.status_code == requests.codes.get(401):
		# 401 Authentification failed
		sys.stderr.write("Authentification failed. User or password is wrong.\n")
		sys.exit(-2)
	elif response.status_code == requests.codes.get(403):
		# 403 Forbidden
		sys.stderr.write("Authentification is missing.\n")
		sys.exit(-3)
	
	sys.stderr.write("Update failed.\n")
	sys.exit(-1)

if __name__ == '__main__':
	main()
