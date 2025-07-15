import sys
import requests
from lxml import etree
import xmlsec
import json
import os

API_URL = "https://fastag.onebee.in/api/bank/tag_details"
PRIVATE_KEY_FILE = "signer_private_key.pem"
PUBLIC_CERT_FILE = "signer_public_cert.pem"


def sign_xml(xml_path, signed_xml_path):
    # Parse the XML
    xml = etree.parse(xml_path)
    root = xml.getroot()

    # Create signature template
    signature_node = xmlsec.template.create(
        root,
        xmlsec.Transform.EXCL_C14N,
        xmlsec.Transform.RSA_SHA256
    )
    root.insert(0, signature_node)

    # Add reference
    ref = xmlsec.template.add_reference(signature_node, xmlsec.Transform.SHA256)
    xmlsec.template.add_transform(ref, xmlsec.Transform.ENVELOPED)

    # Add KeyInfo and X509Data
    key_info = xmlsec.template.ensure_key_info(signature_node)
    xmlsec.template.add_x509_data(key_info)

    # Sign
    sign_ctx = xmlsec.SignatureContext()
    sign_ctx.key = xmlsec.Key.from_file(PRIVATE_KEY_FILE, xmlsec.KeyFormat.PEM)
    sign_ctx.key.load_cert_from_file(PUBLIC_CERT_FILE, xmlsec.KeyFormat.PEM)
    sign_ctx.sign(signature_node)

    # Save signed XML
    with open(signed_xml_path, "wb") as f:
        f.write(etree.tostring(xml, pretty_print=True))


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <request.xml>")
        sys.exit(1)

    xml_file = sys.argv[1]
    signed_xml_file = "signed_request.xml"

    # Check for private key and cert
    if not os.path.exists(PRIVATE_KEY_FILE) or not os.path.exists(PUBLIC_CERT_FILE):
        print(f"Error: Private key or public cert not found. Expected '{PRIVATE_KEY_FILE}' and '{PUBLIC_CERT_FILE}' in current directory.")
        sys.exit(1)

    # Sign the XML
    try:
        sign_xml(xml_file, signed_xml_file)
        print(f"Signed XML saved to {signed_xml_file}")
    except Exception as e:
        print(f"Error signing XML: {e}")
        sys.exit(2)

    # Send signed XML
    with open(signed_xml_file, 'rb') as f:
        signed_xml = f.read()

    headers = {"Content-Type": "application/xml"}
    response = requests.post(API_URL, data=signed_xml, headers=headers)
    print(f"Response status: {response.status_code}")
    print(response.text)

if __name__ == "__main__":
    main() 