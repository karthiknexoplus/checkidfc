from fastapi import FastAPI, Request, Response

app = FastAPI()

@app.post("/api/bank/tag_details")
async def tag_details(request: Request):
    xml_data = await request.body()
    # Here you would parse, verify, and process the XML as needed
    # For now, just echo back a sample response
    response_xml = """
    <etc:RespTagDetails xmlns:etc="http://npci.org/etc/schema/">
      <Head msgId="123" orgId="PGSH" ts="2024-06-07T15:00:00" ver="1.0"/>
      <Txn id="123" note="" orgTxnId="" refId="" refUrl="" ts="2024-06-07T15:00:00" type="FETCH">
        <Resp respCode="000" result="SUCCESS" successReqCnt="1" totReqCnt="1" ts="2024-06-07T15:01:00">
          <Vehicle errCode="000">
            <VehicleDetails>
              <Detail name="TAGID" value="34161FA82032D69802008A60"/>
              <Detail name="REGNUMBER" value="ZZ00BB007"/>
              <Detail name="TID" value="34161FA82032D69802008A60"/>
              <Detail name="VEHICLECLASS" value="VC4"/>
              <Detail name="TAGSTATUS" value="A"/>
              <Detail name="EXCCODE" value="01"/>
              <Detail name="COMVEHICLE" value="F"/>
            </VehicleDetails>
          </Vehicle>
        </Resp>
      </Txn>
      <Signature>...</Signature>
    </etc:RespTagDetails>
    """
    return Response(content=response_xml, media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bank_api_server:app", host="0.0.0.0", port=8000, reload=True) 