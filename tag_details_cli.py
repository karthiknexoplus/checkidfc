import sys
import requests
from lxml import etree
import xmlsec
import json

IDFC_API_URL = "https://etolluatapi.idfcfirstbank.com/dimtspay_toll_services/toll/ReqTagDetails/v2"
CERT_FILE = "etolluatsigner_Public.crt.txt"


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <request.xml>")
        sys.exit(1)

    xml_file = sys.argv[1]
    with open(xml_file, 'rb') as f:
        xml_data = f.read()

    # Send request
    headers = {"Content-Type": "application/xml"}
    response = requests.post(IDFC_API_URL, data=xml_data, headers=headers)
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} from IDFC API")
        sys.exit(2)

    # Parse response
    try:
        root = etree.fromstring(response.content)
    except Exception as e:
        print(f"Error: Invalid XML from IDFC API: {e}")
        sys.exit(3)

    # Find the Signature node
    signature_node = root.find('.//{http://www.w3.org/2000/09/xmldsig#}Signature')
    if signature_node is None:
        print("Error: No Signature found in response")
        sys.exit(4)

    # Verify the signature
    try:
        manager = xmlsec.KeysManager()
        key = xmlsec.Key.from_file(CERT_FILE, xmlsec.KeyFormat.CERT_PEM)
        manager.add_key(key)
        ctx = xmlsec.SignatureContext(manager)
        ctx.verify(signature_node)
    except Exception as e:
        print(f"Error: Signature verification failed: {e}")
        sys.exit(5)

    # Extract vehicle details
    vehicle_details = {}
    details_nodes = root.findall('.//Detail')
    for detail in details_nodes:
        name = detail.attrib.get('name')
        value = detail.attrib.get('value')
        if name and value:
            vehicle_details[name] = value

    if vehicle_details:
        print(json.dumps(vehicle_details, indent=2))
    else:
        print("No vehicle details found. Full response:")
        print(response.content.decode(errors='replace'))

if __name__ == "__main__":
    main() 