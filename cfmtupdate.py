#!/usr/bin/python

import requests
from config import * 
import sys
import json
import os

# from config: 
# - CFDOMAIN
# - CFTOKEN
# - CFEMAIL

# first check if DNS matches our current IP

# so first get the current IP:
current_ip = requests.get('https://ipv4.icanhazip.com').text.strip()
cfzoneid = requests.get(
        'https://api.cloudflare.com/client/v4/zones?name=' + CFDOMAIN,
        headers={
            'Content-Type': "application/json",
            "X-AUTH-KEY": CFTOKEN,
            "X-AUTH-EMAIL": CFEMAIL
        }
    ).json()['result'][0]['id']

cf_dns_zone = requests.get(
        'https://api.cloudflare.com/client/v4/zones/' + cfzoneid + '/dns_records?type=A&name=' + CFDOMAIN,
        headers={
            'Content-Type': "application/json",
            "X-AUTH-KEY": CFTOKEN,
            "X-AUTH-EMAIL": CFEMAIL
        }
    ).json()['result'][0]
dns_ip = cf_dns_zone['content']
dns_id = cf_dns_zone['id']

if current_ip == dns_ip:
    sys.exit(0)

print "IPs don't match"

print(requests.put('https://api.cloudflare.com/client/v4/zones/' + cfzoneid + '/dns_records/' + dns_id,
        headers={
            'Content-Type': "application/json",
            "X-AUTH-KEY": CFTOKEN,
            "X-AUTH-EMAIL": CFEMAIL
        },
        data=json.dumps({
            'type': "A",
            'name': CFDOMAIN,
            'content': current_ip
        })
    ).json())
 
 

# do the Mikrotik magic! 
os.system("ssh " + ROUTER_IP + ' \'/ip firewall nat set [find dst-address="' + dns_ip + '"] dst-address=' + current_ip + "'")
