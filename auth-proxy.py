#!/usr/bin/env python3

import configparser
import json
import sys
from argparse import ArgumentParser
from hmac import compare_digest
from crypt import crypt
import os
import logging
from subprocess import run
from uuid import uuid4

log = logging.getLogger('auth-proxy')
logging.basicConfig(level='DEBUG')

parser = ArgumentParser()
parser.add_argument('--auth-file', default=os.environ.get('RCLONE_AUTH_PROXY_USERS', '/config/users.conf'))
parser.add_argument('--backend-file', default=os.environ.get('RCLONE_AUTH_PROXY_BACKENDS', '/config/rclone.conf'))
parser.add_argument('--input-file', default='')
cli_args = parser.parse_args()

auth_file_path = cli_args.auth_file
backend_file_path = cli_args.backend_file
input_file_path = cli_args.input_file

def fail():
    print('{}')
    sys.exit(1)

auth_config = configparser.ConfigParser()
auth_config.read(auth_file_path)

if input_file_path:
    with open(input_file_path, 'r') as f:
        auth_request = json.load(f)
else:
    auth_request = json.load(sys.stdin)


req_user = auth_request.get('user', '')

if not req_user in auth_config:
    log.info(f'Fail - unknown username')
    fail()

user_config = auth_config[req_user]

tokens = []
req_public_key = auth_request.get('public_key', '')
if req_public_key:
    log.debug(f'Request public key is ' + req_public_key)
    req_token = req_public_key
    tokens = user_config.get('public_key', '').split()
else:
    req_pw = auth_request.get('pass', '')
    if req_pw:
        log.debug(f'Using password for auth')
        req_token = req_pw
        tokens = [user_config.get('pass', '')]

if not req_token:
    log.info('Fail - expected pass or public_key from rclone')
    fail()

if not tokens:
    log.info('Fail - user has no pass or public_key configured')
    fail()

match = False
for token in tokens:
    if compare_digest(req_token, token):
        match = True
        break
if not match:
    log.info('Fail - bad authentication')
    fail()

if not (backend_name := user_config.get('backend', '')):
    log.info(f'Fail - no backend specified')
    fail()

# Give rclone a chance to refresh any backend token, also checks the config
try:
    run(['rclone', '--config', backend_file_path, 'touch', '--no-create', f'{backend_name}:/{uuid4()}'], check=True)
except:
    fail()

backend_config = configparser.ConfigParser()
backend_config.read(backend_file_path)

backend = { k: v for k, v in backend_config[backend_name].items() }
if root := user_config.get('root', ''):
    backend['_root'] = root

print(json.dumps(backend))
