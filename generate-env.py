#!/usr/bin/env python3
from cryptography.fernet import Fernet
import base64
import os
import platform
import re
import subprocess
import sys

host = 'localhost'

if platform.system() == 'Darwin': # osx
    output = subprocess.check_output(["ifconfig", "en0"])
    host = re.match(r".*inet (.+?) ", str(output)).group(1)

KEY_LENGTH = 40

sys.stdout.write(f"export LEMUR_ENCRYPTION_KEYS={Fernet.generate_key().decode('utf-8')}\n")
sys.stdout.write(f"export LEMUR_TOKEN_SECRET={base64.b64encode(os.urandom(KEY_LENGTH)).decode('utf-8')}\n")
sys.stdout.write(f"export SECRET_KEY={base64.b64encode(os.urandom(KEY_LENGTH)).decode('utf-8')}\n")

sys.stdout.write(f"export SQLALCHEMY_DATABASE_URI=postgresql://lemur:lemur@{host}:5432/lemur\n")
sys.stdout.write(f"export REDIS_HOST={host}\n")
sys.stdout.write("export REDIS_PASSWORD=lemur\n")
sys.stdout.write("export POSTGRES_PASSWORD=lemur\n")

CONF_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lemur.conf.py")
sys.stdout.write(f"export LEMUR_CONF={CONF_PATH}")
