from flask import flash, current_app
import ipaddress
from ipaddress import AddressValueError

class CertNameAttribute(object):
    def __init__(self, country: str=None, state: str=None, locality: str=None,
                 org_name: str=None, common_name: str=None, email: str=None, ipaddr: str=None):
        self.country = country
        self.state = state
        self.locality = locality
        self.org_name = org_name
        self.common_name = common_name
        self.email = email
        self.ipaddr = ipaddr
        return 
    
    def todict(self):
        return({
            'country': self.country,
            'state': self.state,
            'locality': self.locality,
            'org_name': self.org_name,
            'email': self.email,
            'ipaddr': self.ipaddr
        })

# I did nothing here. Just adapted what was on the following link to my needs.
# thanks all from cryptography
#
# https://cryptography.io/en/latest/x509/tutorial/#creating-a-certificate-signing-request-csr
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

def generate_key_and_csr(name: str=None, domain: str=None, attributes: CertNameAttribute=None):
    if name is None:
        flash('error', 'can\'t generate a key without a name')
        return None
    
    if domain is None:
        flash('error', 'can\'t generate a key/csr pair without  a domain')
        return None
        
    if attributes is None:
        flash('error', 'can\'t generate a key/csr pair without country/state/location/company/common_name attributes')
        return None
     
    if attributes.ipaddr is None:
        flash('error', 'can\'t generate a key/csr pair without an IP Address')
        return None
    
    full_qdn = f'{name}.{domain}'
    try:
        ipaddr = ipaddress.IPv4Address(attributes.ipaddr)
    except AddressValueError as e:
        flash('error', f'IP Address error: {e.message}')
        return None

    # Generate our key
    try:
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
    except KeyError:
        flash('error', 'could not generate the key')
        return None

    try:
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            # Provide various details about who we are.
            x509.NameAttribute(NameOID.COUNTRY_NAME, attributes.country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, attributes.state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, attributes.locality),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, attributes.org_name),
            x509.NameAttribute(NameOID.COMMON_NAME, attributes.common_name),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, attributes.email),
        ])).add_extension(x509.SubjectAlternativeName([
            # Describe what sites we want this certificate for.
            x509.DNSName(domain),
            x509.DNSName(full_qdn),
            x509.DNSName(attributes.common_name),
            x509.DNSName(name),
            x509.IPAddress(ipaddr)
        ]),
            critical=False,
        # Sign the CSR with our private key.
        ).sign(key, hashes.SHA256())
    except Exception as e:
        flash('error', f'could not generate the certificate signing request {e.message}')
        return None
    
    # I need them in pem format 
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"))
    csr_pem = csr.public_bytes(serialization.Encoding.PEM)

    # PEM format is byte coded. decode to unicode.
    return key_pem.decode('utf8'), csr_pem.decode('utf8')
