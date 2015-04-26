#! /usr/bin/env python3
"""
A simple script to update the OVH DynHost entry with the current external IP of this machine.
"""

import argparse
import ipgetter
import requests

def main():

	domain = ''
	myip = ipgetter.myip()
	user=''
	password=''
	
	parser = argparse.ArgumentParser(description='Set the OVH DynHost entry to the specified IP address.')

	args = parser.parse_args()

	queryArguments = {'system':'dyndns', 'hostname':domain, 'myip':myip}
	response = requests.get("https://www.ovh.com/nic/update", params=queryArguments, auth=(user, password))
	if response.status_code == requests.codes.ok:
		pass
	else:
		pass

if __name__ == '__main__':
	main()
