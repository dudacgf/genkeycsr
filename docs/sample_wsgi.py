#!/usr/bin/python3

import sys
import os
import site

# python 3.6 (Redhat/CentOS 7)
#site.addsitedir('/srv/genkeycsr/.env/lib/python3.6/site-packages')
# python 3.9 (Ubuntu 20.04+, RedHat/CentOS/Rocky 8)
site.addsitedir('/srv/genkeycsr/.env/lib/python3.9/site-packages')

#
# if you want to change default config values, copy the sample_config.py file under docs/ 
# to the root of the environment and modify the options there
#
#
os.environ['GENKEYCSR_CONFIG_PATH'] = '/srv/genkeycsr/config.py'

sys.path.insert(0, '/srv/genkeycsr')

from gen_keycsr import app as application

application.config['ready'] = True
