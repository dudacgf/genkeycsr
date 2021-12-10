import builtins
from cryptography import exceptions
from cryptography.x509.base import load_pem_x509_certificate
from flask import flash
import datetime
from ipaddress import IPv4Address, AddressValueError

# I did nothing here. Just adapted what was on the following link to my needs.
# thanks all from cryptography
#
# https://cryptography.io/en/latest/x509/tutorial/#creating-a-certificate-signing-request-csr
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidKey

class CertNameAttribute(object):
    def __init__(self, country: str=None, state: str=None, locality: str=None,
                 org_name: str=None, common_name: str=None, email: str=None, 
                 ipaddr: str=None, self_signed: bool=False):
        self.country = country
        self.state = state
        self.locality = locality
        self.org_name = org_name
        self.common_name = common_name
        self.email = email
        self.ipaddr = ipaddr
        self.self_signed = self_signed
        return 
    
def generate_key(size: int=2048):
    # Generate our key
    try:
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=size,
        )
    except KeyError:
        flash('error', 'could not generate the key')
        return None

    return key

#
# Generates a certificate signing request
# receives the private key in RSAPrivateKey format and the Attributes to the certificate
# return a certitificate signing request
#
def generate_cert_sign_request(key: str= rsa.RSAPrivateKey, attributes: CertNameAttribute=None):
    if key is None:
        flash('error', 'can\'t generate a certificate signing request without a key')
        return None

    if attributes is None:
        flash('error', 'can\'t generate a  certificate signing request without country/state/location/company/common_name attributes')
        return None
     
    try:
        subject = new_subject(attributes)
        subjectAltName = new_subject_alternative_name(attributes)
        csr = x509.CertificateSigningRequestBuilder().subject_name(subject
            ).add_extension( subjectAltName, critical=False,
            ).sign(key, hashes.SHA256()
        )
    except InvalidKey as e:
        flash('error', f'could not generate the certificate signing request {e.message}')
        return None

    return csr

#
# Generates a self signed certificate 
# receives CertNameAttributes with attributes to the certificate
# return a self signed certificate
#
def generate_cert_self_signed(key: rsa.RSAPrivateKey=None, attributes: CertNameAttribute=None):
    if key is None:
        flash('error', 'can\'t generate a self signed certificate without a key')
        return None
    
    if attributes is None:
        flash('error', 'can\'t generate a self signed certificate without country/state/location/company/common_name attributes')
        return None
     
    try:
        subject = new_subject(attributes)
        subjectAltName = new_subject_alternative_name(attributes)
        crt = x509.CertificateBuilder().subject_name(subject
            ).issuer_name ( subject 
            ).public_key( key.public_key()
            ).serial_number( x509.random_serial_number()
            ).not_valid_before( datetime.datetime.utcnow()
            ).not_valid_after( datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension( subjectAltName, critical=False,
            ).sign(key, hashes.SHA256()
        )
    except InvalidKey as e:
        flash('error', f'could not generate the certificate signing request {e.message}')
        return None
    
    return crt

# returns a x509.Name object with the attributes to create the certificate
def new_subject(attributes: CertNameAttribute=None):
    if attributes == None:
        flash('error', f'can\'t create a certificate without attributes')
        return None
    
    return x509.Name([
               # Provide various details about who we are.
                x509.NameAttribute(NameOID.COUNTRY_NAME, attributes.country),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, attributes.state),
                x509.NameAttribute(NameOID.LOCALITY_NAME, attributes.locality),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, attributes.org_name),
                x509.NameAttribute(NameOID.COMMON_NAME, attributes.common_name),
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, attributes.email),
            ])

# returns a x509.SubjectAlternativeName object with the attributes to create the certificate
def new_subject_alternative_name(attributes: CertNameAttribute=None):
    if attributes == None:
        flash('error', f'can\'t create a certificate without attributes')

    # attributes i want to use as subject alternative names
    name = attributes.common_name.split('.')[0]    
    domain = attributes.common_name.split('.')[1:]
    domain = '.'.join(domain)
    full_qdn = f'{name}.{domain}'
    
    # ipaddr must be passed as a valid ipaddress.IPV4Address
    try:
        ipaddr = IPv4Address(attributes.ipaddr)
    except AddressValueError as e:
        flash(f'Invalid IP Address {attributes.ipaddr}')
        return None

    return x509.SubjectAlternativeName([
                # Describe what sites we want this certificate for.
                x509.DNSName(domain),
                x509.DNSName(full_qdn),
                x509.DNSName(attributes.common_name),
                x509.DNSName(name),
                x509.IPAddress(ipaddr)
            ])

# Converts the private key to pem format 
def key_to_pem(key: rsa.RSAPrivateKey):
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"))
   
    return key_pem.decode('utf8')

# Converts the certificate signing request to pem format
def csr_to_pem(csr: x509.CertificateSigningRequest):
    csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode('utf8')
    
    return csr_pem

# Converts the self-signed certificate to pem format
def sscrt_to_pem(crt: x509.CertificateSigningRequest):
    crt_pem = crt.public_bytes(serialization.Encoding.PEM).decode('utf8')

    return crt_pem



