from re import split
from typing import Sized
from flask_wtf import FlaskForm
from validators.utils import ValidationFailure
from wtforms import StringField, EmailField
from wtforms.validators import DataRequired, HostnameValidation, Length, IPAddress, Email, ValidationError
from validators import email, domain, ValidationFailure

class GenKeyCSRForm(FlaskForm):
    country = StringField('Country Name (2 letter code)', 
                          validators=[DataRequired(message='Please enter a 2 letter country code.'), 
                          Length(min=2, max=2, message='use country code with 2 letters.')])
    state = StringField('State or Province Name (full name)',
                          validators=[DataRequired(message='Please enter a state or province name.'),])
    locality = StringField('Locality Name (eg, city) ', 
                          validators=[DataRequired(message='Please enter a locality name.')])
    org_name = StringField('Organization Name (eg, company)', 
                          validators=[DataRequired(message='Please enter an organization name.')])
    org_unit_name = StringField('Organizational Unit Name (eg, section) '),
    common_name = StringField('Common Name (server FQDN)', 
                          validators=[DataRequired(message='Please enter a full qualified common name.')])
    email = EmailField('Email Address', 
                          validators=[DataRequired(message='Please enter a valid email.'), 
                          Email(message='invalid email')])
    ipaddr = StringField('IP Address',
                          validators=[DataRequired(message='Please enter a valid IP Address.'), 
                          IPAddress(ipv4=True, ipv6=False, message='please enter a valid IP address')])
    
    def validate_common_name(form, field):
        try:
            print(f'aqui {field.data}')
            domain(field.data)
            hostname = str(field.data)
            if hostname.find('.') < 0:
                raise ValidationError(f'common name too short or invalid {field.data}')
        except ValidationFailure:
            print('aqui não')
            raise ValidationError(f'common name too short or invalid {field.data}')
    


    