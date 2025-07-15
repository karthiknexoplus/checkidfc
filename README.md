# IDFC Tag Details FastAPI Service

## Setup

1. **Clone the repository and enter the directory**
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server (Locally or on EC2)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Endpoint

- **POST** `/api/bank/tag_details`
  - Content-Type: `application/xml`
  - Body: XML as per NPCI/IDFC schema
  - Forwards request to IDFC, verifies response signature, and returns vehicle details as JSON (or raw XML if details not found).

## Certificate

- The public certificate for signature verification must be present as `etolluatsigner_Public.crt.txt` in the project root.

## Example cURL

```bash
curl -X POST \
  http://<your-ec2-ip>:8000/api/bank/tag_details \
  -H 'Content-Type: application/xml' \
  --data-binary @your_request.xml
``` 