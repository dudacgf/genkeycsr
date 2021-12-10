import os

from flask import Flask, render_template, flash
from flask.helpers import get_flashed_messages
from flask.json import jsonify
from flask_fontawesome import FontAwesome

from .libs.genkeycsr import (CertNameAttribute, generate_key, generate_cert_sign_request, 
                            generate_cert_self_signed, key_to_pem, csr_to_pem, sscrt_to_pem)
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
    GENKEYCSR_KEY_SIZE = 2048,
    GENKEYCSR_COUNTRY = 'AU',
    GENKEYCSR_STATE = 'Some-State',
    GENKEYCSR_LOCALITY = '',
    GENKEYCSR_ORGNAME = 'Internet Widgits Pty Ltd',
    GENKEYCSR_ORG_UNIT_NAME = '',
    GENKEYCSR_COMMON_NAME = 'CHANGE-ME.COMMON.name',
    GENKEYCSR_EMAIL = '',
    GENKEYCSR_LOGO = 'images/keycsr_default_logo.jpg',
    GENKEYCSR_FAVICON = 'images/keycsr_default_logo.png'
)
# you can put any config option in a python file and set its path via ENVVAR GENKEYCSR_CONFIG_PATH
if 'GENKEYCSR_CONFIG_PATH' in os.environ:
    try:
        app.config.from_pyfile(os.environ.get('GENKEYCSR_CONFIG_PATH'))
    except FileNotFoundError:
        pass

#
# create instance dirs if any
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

def flash_messages_to_dict():
    messages = [{'message': m, 'category':c} for c, m in
            get_flashed_messages(with_categories=True)];
    return messages


#
# route that generates the key/(csr/self-signed crt) pair and sends it back.
# receives: request.formdata with the certificate attributes
# returns: json struc with key and csr in pem format
@app.route('/generate_pair', methods=['POST'])
def generate_pair():
    form = GenKeyCSRForm()
    if not form.validate_on_submit():
        flash('--error validating form--')
        return jsonify({'status': 'error', 'messages': render_template('form_errors.html', form=form, messages = flash_messages_to_dict())})

    attributes = CertNameAttribute()
    form.populate_obj(attributes)
    
    # generate the private key
    key = generate_key(app.config['GENKEYCSR_KEY_SIZE'])
    if key is None:
        flash('error', 'problem generating the key/csr pai.r')
        return jsonify({'status': 'error', 'messages': flash_messages_to_dict()})

    # generate the csr/self-signed crt depending on self_signed checkbox received from form
    if not attributes.self_signed:
        cert = generate_cert_sign_request(key, attributes)
        if cert is None:
            flash('error', 'problem generating certificate signing request.')
            return jsonify({'status': 'error', 'messages': flash_messages_to_dict()})
        cert_pem = csr_to_pem(cert)
    else:
        cert = generate_cert_self_signed(key, attributes)
        if cert is None:
            flash('error', 'problem generating self-signed certificate.')
            return jsonify({'status': 'error', 'messages': flash_messages_to_dict()})
        cert_pem = sscrt_to_pem(cert)

    flash('success', 'key/cert (signing request or self-signed) pair generated successfuly')
    return jsonify({'status': 'success', 'key': key_to_pem(key), 'cert': cert_pem})

# 
# main route. populate form with attribute default values (mine or from configuration {file}.py)
@app.route('/', methods=['POST', 'GET'])
def vstest():
    form = GenKeyCSRForm()            
    form.country.data=app.config['GENKEYCSR_COUNTRY']
    form.state.data=app.config['GENKEYCSR_STATE']
    form.locality.data=app.config['GENKEYCSR_LOCALITY']
    form.org_name.data=app.config['GENKEYCSR_ORGNAME']
    form.org_unit_name.data=app.config['GENKEYCSR_ORG_UNIT_NAME']
    form.common_name.data=app.config['GENKEYCSR_COMMON_NAME']
    form.email.data=app.config['GENKEYCSR_EMAIL']
    
    return render_template('index.html', form=form)

