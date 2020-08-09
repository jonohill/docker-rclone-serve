#!/usr/bin/env python3

from ruamel.yaml import YAML
import json
import sys
from argparse import ArgumentParser
from hmac import compare_digest
from crypt import crypt
import os
import logging

log = logging.getLogger('auth-proxy')
logging.basicConfig(level='DEBUG')

parser = ArgumentParser()
parser.add_argument('--auth-file', default='')
parser.add_argument('--input-file', default='')
cli_args = parser.parse_args()

auth_file_path = cli_args.auth_file or os.environ.get('RCLONE_AUTH_PROXY_CONF', '/config/users.yaml')
input_file_path = cli_args.input_file

def fail():
    print('{}')
    sys.exit(1)

yaml = YAML()
try:
    with open(auth_file_path, 'r') as f:
        auth_config = yaml.load(f)
except:
    log.error("Couldn't load auth-proxy config file")
    fail()

if input_file_path:
    with open(input_file_path, 'r') as f:
        auth_request = json.load(f)
else:
    auth_request = json.load(sys.stdin)


req_user = auth_request.get('user', '')
if len(req_user) < 1 or req_user[0] == '_':
    log.info(f'Fail - username starts with _')
    fail()

user_config = auth_config.get(req_user, False)
if not user_config:
    log.info(f'Fail - unknown username')
    fail()

def succeed():
    print(json.dumps(user_config.get('backend', {})))
    sys.exit(0)

req_public_key = auth_request.get('public_key', '')
log.debug(f'Request public key is ' + req_public_key)
if req_public_key:
    public_key = user_config.get('public_key', '')
    if compare_digest(req_public_key, public_key):
        log.info(f'Success - public key matches for {req_user}')
        succeed()
else:
    req_pw = auth_request.get('pass', '')
    if req_pw:
        pw = user_config.get('pass', '')
        if compare_digest(req_pw, pw):
            log.info(f'Success - password matches for {req_user}')
            succeed()

log.info('Fail - bad authentication')
fail()
