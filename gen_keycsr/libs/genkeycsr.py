from flask import flash, current_app
import datetime
from ipaddress import IPv4Address, AddressValueError

# I did nothing here. Just adapted what was on the following link to my needs.
# thanks all from cryptography
#
# https://cryptography.io/en/latest/x509/tutorial/#creating-a-certificate-signing-request-csr
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidKey

class CertNameAttributes(object):
    def __init__(self, country: str=None, state: str=None, locality: str=None,
                 org_name: str=None, org_unit_name: str=None, common_name: str=None, email: str=None, 
                 ipaddr: str=None, self_signed: bool=False):
        self.country = country
        self.state = state
        self.locality = locality
        self.org_name = org_name
        self.org_unit_name = org_unit_name
        self.common_name = common_name
        self.email = email
        self.ipaddr = ipaddr
        self.self_signed = self_signed
        return 
    
class CriptographyGenerator(object):
    def __init__(self, attributes: CertNameAttributes=None):

        if attributes is None:
            flash('error', 'can\'t generate anything without attributes like country, common_name etc.')
            return None

        if attributes.country is None:
            flash('error', 'can\'t generate anything without a country.')
            return None
        if attributes.state is None:
            flash('error', 'can\'t generate anything without a state or provice name.')
            return None
        if attributes.locality is None:
            flash('error', 'can\'t generate anything without a locality name.')
            return None
        if attributes.org_name is None:
            flash('error', 'can\'t generate anything without an organization name.')
            return None
        if attributes.common_name is None:
            flash('error', 'can\'t generate anything without a common_name.')
            return None
        if attributes.email is None:
            flash('error', 'can\'t generate anything without an email.')
            return None
        if attributes.ipaddr is None:
            flash('error', 'can\'t generate anything without an IP address.')
            return None
        
        self.country = attributes.country
        self.state = attributes.state
        self.locality = attributes.locality
        self.org_name = attributes.org_name
        self.org_unit_name = attributes.org_unit_name
        self.common_name = attributes.common_name
        self.email = attributes.email
        self.ipaddr = attributes.ipaddr
        self.self_signed = attributes.self_signed
        self.key_size = current_app.config.get('GENKEYCSR_KEY_SIZE', None)
        if self.key_size is None:
            self.key_size = 2048
        return 
    
    # generate a new rsa private key 
    def new_key(self):
        try:
            self.key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size,
            )
        except KeyError:
            flash('error', 'could not generate the key')
            return None

        return self.key

    #
    # Generates a certificate signing request
    # receives the private key in RSAPrivateKey format and the Attributes to the certificate
    # return a certitificate signing request
    #
    def new_csr(self):
        if self.key is None:
            flash('error', 'can\'t generate a certificate signing request without a key')
            return None

        try:
            subject = self.new_subject()
            subjectAltName = self.new_subject_alternative_name()
            self.csr = x509.CertificateSigningRequestBuilder().subject_name(subject
                ).add_extension( subjectAltName, critical=False,
                ).sign(self.key, hashes.SHA256()
            )
        except InvalidKey as e:
            flash('error', f'could not generate the certificate signing request {e.message}')
            return None

        return self.csr

    #
    # Generates a self signed certificate 
    # receives CertNameAttributess with attributes to the certificate
    # return a self signed certificate
    #
    def new_ss_crt(self):
        if self.key is None:
            flash('error', 'can\'t generate a self signed certificate without a key')
            return None
        
        try:
            subject = self.new_subject()
            subjectAltName = self.new_subject_alternative_name()
            self.crt = x509.CertificateBuilder().subject_name(subject
                ).issuer_name ( subject 
                ).public_key( self.key.public_key()
                ).serial_number( x509.random_serial_number()
                ).not_valid_before( datetime.datetime.utcnow()
                ).not_valid_after( datetime.datetime.utcnow() + datetime.timedelta(days=365)
                ).add_extension( subjectAltName, critical=False,
                ).sign(self.key, hashes.SHA256()
            )
        except InvalidKey as e:
            flash('error', f'could not generate the certificate signing request {e.message}')
            return None
        
        return self.crt

    # returns a x509.Name object with the attributes to create the certificate
    def new_subject(self):
        return x509.Name([
                # Provide various details about who we are.
                    x509.NameAttribute(NameOID.COUNTRY_NAME, self.country),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.state),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, self.locality),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.org_name),
                    x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, self.org_unit_name),
                    x509.NameAttribute(NameOID.COMMON_NAME, self.common_name),
                    x509.NameAttribute(NameOID.EMAIL_ADDRESS, self.email),
                ])

    # returns a x509.SubjectAlternativeName object with the attributes to create the certificate
    def new_subject_alternative_name(self):
        # attributes i want to use as subject alternative names
        name = self.common_name.split('.')[0]    
        domain = self.common_name.split('.')[1:]
        domain = '.'.join(domain)
        full_qdn = f'{name}.{domain}'
        
        # ipaddr must be passed as a valid ipaddress.IPV4Address
        try:
            ipaddr = IPv4Address(self.ipaddr)
        except AddressValueError as e:
            flash(f'Invalid IP Address {self.ipaddr}')
            return None

        return x509.SubjectAlternativeName([
                    # Describe what sites we want this certificate for.
                    x509.DNSName(domain),
                    x509.DNSName(full_qdn),
                    x509.DNSName(self.common_name),
                    x509.DNSName(name),
                    x509.IPAddress(ipaddr)
                ])

    # Converts the private key to pem format 
    def key_to_pem(self):
        key_pem = self.key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"))
    
        return key_pem.decode('utf8')

    # Converts the certificate signing request to pem format
    def csr_to_pem(self):
        csr_pem = self.csr.public_bytes(serialization.Encoding.PEM).decode('utf8')
        
        return csr_pem

    # Converts the self-signed certificate to pem format
    def sscrt_to_pem(self):
        crt_pem = self.crt.public_bytes(serialization.Encoding.PEM).decode('utf8')

        return crt_pem
