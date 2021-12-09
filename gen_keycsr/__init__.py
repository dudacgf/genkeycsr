import os

from flask import Flask, render_template, flash
from flask.helpers import get_flashed_messages
from flask.json import jsonify
from flask_fontawesome import FontAwesome

from .libs.genkeycsr import CertNameAttribute, generate_key_and_csr
from .libs.frmattributes import GenKeyCSRForm

app = Flask(__name__)
fa = FontAwesome(app)

#
# configuration settings and defaults
app.config.from_mapping(
    SECRET_KEY = os.urandom(24),
    UPLOAD_FOLDER = '/var/tmp',
    SESSION_COOKIE_SAMESITE = "Lax",
    # FICTITIOUS COUNTRY TO FILL THE FORM FIELDS
    GENCSR_COUNTRY = 'AU',
    GENCSR_STATE = 'Some-State',
    GENCSR_LOCALITY = '',
    GENCSR_ORGNAME = 'Internet Widgits Pty Ltd',
    GENCSR_ORG_UNIT_NAME = '',
    GENCSR_COMMON_NAME = 'CHANGE-ME.COMMON.name',
    GENCSR_EMAIL = '',
    GENCSR_LOGO = '/static/images/keycsr_default_logo.jpg',
    GENCSR_FAVICON = '/static/images/keycsr_default_logo.png'
)
# you can put any config option in a python file and set its path via ENVVAR GENCSR_CONFIG_PATH
if 'GENCSR_CONFIG_PATH' in os.environ:
    try:
        app.config.from_pyfile(os.environ.get('GENCSR_CONFIG_PATH'))
    except FileNotFoundError:
        pass

#
# create instance dirs if any
try:
    os.makedirs(app.instance_path)
except OSError:
    pass
    
#
# route that generates the key/csr pair and sends it back.
# receives. request.formdata with the certificate attributes
# returns: json struc with key and csr in pem format
@app.route('/generate_key_csr_pair', methods=['POST'])
def generate_pair():
    form = GenKeyCSRForm()
    if not form.validate_on_submit():
        flash('error validating form')
        return jsonify({'status': 'error', 'messages': render_template('form_errors.html', form=form, messages = get_flashed_messages)})

    attributes = CertNameAttribute()
    form.populate_obj(attributes)
    
    # generate the key/csr pair
    name = attributes.common_name[0]
    domain = attributes.common_name[1:]
    key, csr = generate_key_and_csr(name, domain, attributes)
    if key is None:
        flash('error', 'problem generating the key/csr pair')
        return jsonify({'status': 'error', 'messages': get_flashed_messages()})
    
    flash('message', 'key/csr par generated successfuly')
    return jsonify({'status': 'success', 'key': key, 'csr': csr})

# 
# main route. populate form with attribute default values (mine or from configuration file.py)
@app.route('/', methods=['POST', 'GET'])
def vstest():
    form = GenKeyCSRForm()            
    form.country.data=app.config['GENCSR_COUNTRY']
    form.state.data=app.config['GENCSR_STATE']
    form.locality.data=app.config['GENCSR_LOCALITY']
    form.org_name.data=app.config['GENCSR_ORGNAME']
    form.org_unit_name.data=app.config['GENCSR_ORG_UNIT_NAME']
    form.common_name.data=app.config['GENCSR_COMMON_NAME']
    form.email.data=app.config['GENCSR_EMAIL']
    
    return render_template('index.html', form=form)

