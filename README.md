# InspireWorks IVR Demo

A multi-level Interactive Voice Response (IVR) system built with Plivo Voice API, demonstrating outbound calling, language selection, audio playback, and call forwarding.

---

## Features

- Outbound calling via REST API
- Two-level IVR menu system
- Language selection (English / Spanish)
- DTMF input handling
- Audio message playback
- Call forwarding to an associate

---

## Prerequisites

- Python 3.8+
- Plivo account with Voice API access
- A Plivo phone number
- Public URL for webhooks (ngrok or localtunnel)

---

## Required Plivo Credentials

You will need the following credentials from your Plivo Console (https://console.plivo.com):

| Credential | Description | Where to Find |
|------------|-------------|---------------|
| `PLIVO_AUTH_ID` | Your Plivo Auth ID | Dashboard > Account > Auth ID |
| `PLIVO_AUTH_TOKEN` | Your Plivo Auth Token | Dashboard > Account > Auth Token |
| `PLIVO_FROM_NUMBER` | Your Plivo phone number (E.164 format) | Phone Numbers > Your Numbers |

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Plivo_Tech_assessment
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Plivo credentials:

```
PLIVO_AUTH_ID=your_auth_id_here
PLIVO_AUTH_TOKEN=your_auth_token_here
PLIVO_FROM_NUMBER=+1234567890
ASSOCIATE_NUMBER=+0987654321
BASE_URL=https://your-tunnel-url.loca.lt
```

### 5. Set Up Public URL for Webhooks

Plivo requires a publicly accessible URL for IVR webhooks. Use localtunnel:

```bash
npx localtunnel --port 5001
```

Copy the generated URL (e.g., `https://xyz.loca.lt`) and update `BASE_URL` in your `.env` file.

---

## Steps to Run and Test

### 1. Start the Server

```bash
source venv/bin/activate
python app.py
```

The server will start at `http://localhost:5001`.

### 2. Start the Tunnel (in a separate terminal)

```bash
npx localtunnel --port 5001
```

Note: On first visit to the localtunnel URL, you may need to enter your public IP address. Find it with:

```bash
curl -s ifconfig.me
```

### 3. Access the Web Interface

Open `http://localhost:5001` in your browser.

### 4. Make a Test Call

1. Enter a phone number in E.164 format (e.g., `+14155551234`)
2. Click "Call"
3. Answer the incoming call on your phone

### 5. Navigate the IVR

**Level 1 - Language Selection:**
- Press 1 for English
- Press 2 for Spanish

**Level 2 - Action Menu:**
- Press 1 to hear an audio message
- Press 2 to connect to an associate

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/make-call` | POST | Initiate outbound call |
| `/ivr/welcome` | POST | IVR Level 1 (language selection) |
| `/ivr/language-selected` | POST | Process language choice |
| `/ivr/menu` | POST | IVR Level 2 (action menu) |
| `/ivr/action` | POST | Process action choice |

---

## Project Structure

```
Plivo_Tech_assessment/
├── app.py              # Flask application with IVR logic
├── config.py           # Environment configuration
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not committed)
├── .env.example        # Environment template
├── static/
│   └── index.html      # Web interface
└── README.md           # This file
```

---

## Troubleshooting

**"src and destination cannot overlap" error:**
You cannot call the same number that is configured as `PLIVO_FROM_NUMBER`. Use a different destination number.

**500 Internal Server Error:**
Check that `BASE_URL` in `.env` matches your current tunnel URL and restart the Flask server.

**Webhook not receiving requests:**
Ensure the tunnel is running and the URL is accessible. Visit the tunnel URL in a browser to verify.

---

## Documentation References

- [Plivo Voice API](https://www.plivo.com/docs/voice/)
- [GetInput XML Element](https://www.plivo.com/docs/voice/xml/getinput/)
- [Outbound Calls API](https://www.plivo.com/docs/voice/api/call/)
