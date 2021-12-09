from flask_wtf import FlaskForm
from wtforms import StringField, EmailField

from wtforms.validators import DataRequired, HostnameValidation, Length, IPAddress, Email, ValidationError
from re import split
from typing import Sized
from validators import email, domain, ValidationFailure
from iso3166 import countries

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
    org_unit_name = StringField('Organizational Unit Name (eg, section) ')
    common_name = StringField('Common Name (server FQDN)', 
                          validators=[DataRequired(message='Please enter a full qualified common name.')])
    email = EmailField('Email Address', 
                          validators=[DataRequired(message='Please enter a valid email.')])
    ipaddr = StringField('IP Address',
                          validators=[DataRequired(message='Please enter a valid IP Address.'), 
                          IPAddress(ipv4=True, ipv6=False, message='please enter a valid IP address')])
    
    def validate_country(form, field):
        try:
            countries.get(field.data)
        except KeyError:
            raise ValidationError(f'country 2 letter code invalid [{field.data}]')

    def validate_common_name(form, field):
        if not domain(field.data):
            raise ValidationError(f'common name too short or invalid [{field.data}]')

    def validate_email(form, field):
        if not email(field.data):
            raise ValidationError(f'email invalid [{field.data}]')


    