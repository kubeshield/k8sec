#!/usr/bin/env python

import base64
import os
import requests
import socket
import sys
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

apiUrl = os.getenv('OSSEC_API_URL', 'https://appscode-ossec-server:55000')
ca_cert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'

auth_file = open('/var/ossec/api/ssl/basic-auth.csv', 'r')
user, password = auth_file.readline().rstrip().split(',', 1)
auth_file.close()

name = socket.gethostname()
ip = os.getenv('NODE_INTERNAL_IP', 'any')


def find_agent():
	ids = []
	r = requests.get(apiUrl + '/agents', auth=(user, password), verify=ca_cert)
	r.raise_for_status()
	js = r.json()
	if js['error'] == '0':
		for agent in js['response']:
			if agent['name'] == name or agent['ip'] == ip:
				log.info("Agent '%s' with ip '%s' has id '%s'", agent['name'], agent['ip'], agent['id'])
				ids.append(agent['id'])
	return ids

def delete_agents(ids):
	for id in ids:
		r = requests.delete(apiUrl + '/agents/' + id, auth=(user, password), verify=ca_cert)
		r.raise_for_status()
		js = r.json()
		if js['error'] == '0':
			log.info("Deleted agent with id '%s'", id)
		else:
			log.info("Failed to delete agent with id '%s'", id)
			sys.exit(1)

def add_agent():
	log.info("Adding agent '%s' with ip '%s'", name, ip)
	r = requests.post(apiUrl + '/agents', auth=(user, password), verify=ca_cert, data = {'name': name, 'ip' : ip})
	r.raise_for_status()
	js = r.json()
	return js['error'] == '0'

def get_key(id):
	r = requests.get(apiUrl + '/agents/' + id + '/key', auth=(user, password), verify=ca_cert)
	r.raise_for_status()
	js = r.json()
	if js['error'] == '0':
		log.info("Agent with id '%s' has key %s", id, js['response'])
		return js['response']
	return False

def main():
	ids = find_agent()
	if ids:
		delete_agents(ids)
	if add_agent():
		ids = find_agent()
		if not ids:
			sys.exit(1)
		key = get_key(ids[0])
		if not key:
			sys.exit(1)
		keys_file = open('/var/ossec/etc/client.keys', 'w')
		keys_file.write(base64.b64decode(key))
		keys_file.close()
		sys.exit(0)

if __name__ == '__main__':
    main()
