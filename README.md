![GitHub](https://img.shields.io/github/license/dudacgf/genkeycsr)
[![CodeQL](https://github.com/dudacgf/genkeycsr/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/dudacgf/genkeycsr/actions/workflows/codeql-analysis.yml)
![Snyk](https://snyk-widget.herokuapp.com/badge/pip/dudacgf/genkeycsr/badge.svg)
![Lines of code](https://img.shields.io/tokei/lines/github/dudacgf/genkeycsr)
![Shields.io](https://img.shields.io/badge/%20Just%20-%20Relax%20-blue)

# Genkeycsr
Genkeycsr is a Python Flask micro webpage that helps generating private keys and certificate signing requests. It is intended to be used as a helper to in premises root CA structures that cannot be served by letsencrypt or other commercial certificate authorities. It offers an option to create a self-signed certificate along with the private key but you should not use self-signed certificates and so, this options is considered for emergency use only and therefore issues a certificate valid only for 10 days.

Genkeycsr is just a wrapper around the code found in the tutorial of [pica/cryptography](https://cryptography.io/en/latest/x509/tutorial/) and only adapts it to its use. 

It has been tested and run as a standalone site or under apache/wsgi in Ubuntu 20.04+, RedHat/Centos 7/8. But I believe it can be run under nginx or lighthttpd or any other http server that supports wsgi.

________________
## Installation
    Install python and pip and virtualenvironment
    Ubuntu
    # sudo apt-get install python3 python3-pip python3-virtualenv
    RedHat/CentOS 7
    # sudo yum install python3 python3-pip python3-venv
    Under RedHat/CentOS/Rocky 8 you may install python 3.9
    # sudo yum install python3 python3.9-pip python3.9-virtualenv

    Clone the repository
    # cd /srv
    # sudo git clone https://github.com/dudacgf/genkeycsr

    __su__ to root to create the python isolated environment
    # sudo su -l
    $ cd /srv/genkeycsr
    $ python3 -m venv .env
    $ . .env/bin/activate
    (.env) $ which pip3
    /srvp3 v/genkeycsr/.env/bin/pip3       _*[OK]*_
    (.env) $ pip3 install pip setuptools wheel build --upgrade
    (.env) $ pip3 install -r requirements.txt

    Now, test the site and point your browser to server:5000
    (.env) $ ./run.py

   ![Site Page Image](./docs/images/genkeycsr\_default_page.png)


    After the isolated environment is installed, you can run the page as a normal user:
    # cd /srv/genkeycsr
    # . .env/bin/activate
    # ./run.py

_________________
## Configuration

### Default Attributes

You can change the default attributes presented when the page is first loaded. There is a file docs/sample\_config.py that you can copy anywhere in your system and adapt it. Use it via GENKEYCSR\_CONFIG\_PATH environment variable:


~~~python
# private key size
GENKEYCSR_KEY_SIZE=2048 

# certificate attributes
GENKEYCSR_COUNTRY='GK'
GENKEYCSR_STATE='GenKey DC'
GENKEYCSR_LOCALITY=''
GENKEYCSR_ORGNAME='Genkey District Hall'
GENKEYCSR_COMMON_NAME='CHANGE-ME.genkey.gk'
GENKEYCSR_EMAIL='contact@genkey.gk'

# logo and favicon are relative to the static folder
GENKEYCSR_LOGO='images/keycsr_default_logo.jpg'
GENKEYCSR_FAVICON='images/keycsr_default_favicon.png'
~~~

Test your new configuration. E.g., if you put the config file in the root folder of your project:

    (.env) $ GENKEYCSR_CONFIG_PATH=$PWD/config.py ./run.py

### Default logo and favicon

You can change the default logo and default favicon via GENKEYCSR\_DEFAULT\_LOGO and GENKEYCSR\_DEFAULT\_FAVICON in the configuration file. Put your images under gen\_keycsr/static/images and use a path relative to /static to point them.

### How To Use It

Well, it's kind of obvious, really. You call the page, fill in all the fields and click the __Generate__ button. The Private Key and the certificate signing request will be presented in the boxes bellow the form. You can copy the key/csr or you can save them clicking on the icons. _you cannot copy to clipboard in any modern browser if not running under ssl (https://)_.

----------------
### Running under apache

#### Ubuntu 21.04+
    Install mod_wsgi for Python version 3
    # sudo apt-get install libapache2-mod-wsgi-py3

    Copy the sample configuration from the docs/ folder to apache
    # cd /srv/genkeycsr
    # sudo cp docs/genkeycsr.conf /etc/apache2/conf-available
    
    Adjust settings (paths, ports, ssl certificates etc)
    # sudo vi /etc/apache2/conf-available/genkeycsr.conf
    
    Enable the configurattion
    # sudo a2enconf genkeycsr
    
    Copy the file docs/sample_wsgi.conf as config.py and customize it
    # sudo cp docs/sample_wsgi.conf wsgi.conf
    # sudo vi wsgi.conf
    
    Reload apache
    # sudo systemctl reload apache2.service

#### RedHat/CentOS 7 || RedHat/CentOS/Rocky 8
    Install mod_wsgi for Python version 3
    # sudo yum install python3-mod_wsgi

    Copy the sample configuration from the docs/ folder to apache
    # cd /serv/genkeycsr
    # sudo cp docs/genkeycsr.conf /etc/httpd/conf.d
    
    Adjust settings (paths, ports, ssl certificates etc)
    # sudo vi /etc/httpd/conf.d/genkeycsr.conf

    Copy the file docs/sample_wsgi.conf as config.py and customize it
    # sudo cp docs/sample_wsgi.conf wsgi.conf
    # sudo vi wsgi.conf
    
    Reload apache
    # sudo systemctl reload httpd.service

    If you have selinux enabled (you should), use this command to enable the site under apache
    # chcon -Rv --type=httpd_sys_script_exec_t /srv/genkeycsr/

#### Configuration file genkeycsr.conf 
~~~
#
# Configuration file for use in apache with mod_wsgi
#
#
<VirtualHost *:443>

     ServerName fully-qualified.domain.name

     # Redhat/CentOS etc
     WSGIDaemonProcess genkeycsr user=apache group=apache threads=2
     # Debian/Ubuntu etc
     #WSGIDaemonProcess genkeycsr user=www-data group=www-data threads=2

     WSGIScriptAlias /genkeycsr /srv/genkeycsr/wsgi.py

     <Directory /srv/genkeycsr>
         Require all granted
     </Directory>

     SSLEngine on
     SSLCertificateFile /etc/letsencrypt/live/fully-qualified.domain.name/cert.pem
     SSLCertificateKeyFile /etc/letsencrypt/live/fully-qualified.domain.name/privkey.pem

</VirtualHost>
~~~

#### wsgi.py file
~~~python
#!/usr/bin/python3

import sys
import os
import site

# python 3.6 (Redhat/CentOS 7)
#site.addsitedir('/srv/genkeycsr/.env/lib/python3.6/site-packages')
# python 3.9 (Ubuntu 20.04+, RedHat/CentOS/Rocky 8)
site.addsitedir('/srv/genkeycsr/.env/lib/python3.9/site-packages')

# if you want to change default config values, copy the sample_config.py file under docs/ 
# to the root of the environment and modify the options there
#
# you can also change the location of this file and set it here
#
os.environ['GENKEYCSR_CONFIG_PATH'] = '/srv/genkeycsr/config.py'

sys.path.insert(0, '/srv/genkeycsr')

from genkeycsr import app as application

application.config['ready'] = True
~~~
