from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
import requests
from lxml import etree
import xmlsec
import os
from datetime import datetime

app = FastAPI()

IDFC_API_URL = "https://etolluatapi.idfcfirstbank.com/dimtspay_toll_services/toll/ReqTagDetails/v2"
CERT_FILE = "etolluatsigner_Public.crt.txt"

@app.post("/api/bank/tag_details")
async def tag_details(request: Request):
    try:
        # Read incoming XML
        xml_data = await request.body()
        
        # Forward the XML to IDFC API
        headers = {"Content-Type": "application/xml"}
        idfc_response = requests.post(IDFC_API_URL, data=xml_data, headers=headers)
        if idfc_response.status_code != 200:
            return JSONResponse(status_code=502, content={"error": "Failed to get response from IDFC API"})

        # Parse the XML response
        try:
            root = etree.fromstring(idfc_response.content)
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": "Invalid XML from IDFC API", "details": str(e)})

        # Find the Signature node
        signature_node = root.find('.//{http://www.w3.org/2000/09/xmldsig#}Signature')
        if signature_node is None:
            return JSONResponse(status_code=500, content={"error": "No Signature found in response"})

        # Verify the signature
        try:
            manager = xmlsec.KeysManager()
            key = xmlsec.Key.from_file(CERT_FILE, xmlsec.KeyFormat.CERT_PEM)
            manager.add_key(key)
            ctx = xmlsec.SignatureContext(manager)
            ctx.verify(signature_node)
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": "Signature verification failed", "details": str(e)})

        # Extract vehicle details
        vehicle_details = {}
        details_nodes = root.findall('.//Detail')
        for detail in details_nodes:
            name = detail.attrib.get('name')
            value = detail.attrib.get('value')
            if name and value:
                vehicle_details[name] = value

        # If no details found, return the whole XML as fallback
        if not vehicle_details:
            return Response(content=idfc_response.content, media_type="application/xml")

        return vehicle_details
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal server error", "details": str(e)}) 