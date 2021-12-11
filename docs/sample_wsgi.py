#!/usr/bin/python3.9

import sys
import os
import site

site.addsitedir('/var/www/genkeycsr/.env/lib/python3.9/site-packages')

# if you want to change default config values, copy the sample_config.py file under docs/ 
# to the root of the environment and modify the options there
#
# you can also change the location of this file and adjust bellow
#
os.environ['GENKEYCSR_CONFIG_PATH'] = '/var/www/genkeycsr/config.py'

sys.path.insert(0, '/var/www/genkeycsr')

from gen_keycsr import app as application

application.config['ready'] = True
