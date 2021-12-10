#!/usr/bin/python3.9

import sys
import os
import site

site.addsitedir('/var/www/genkeycsr/.env/lib/python3.9/site-packages')

os.environ['GENKEYCSR_CONFIG_PATH'] = '/var/www/genkeycsr/config.py'

sys.path.insert(0, '/var/www/genkeycsr')

from gen_keycsr import app as application
