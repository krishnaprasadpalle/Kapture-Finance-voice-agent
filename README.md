# Kapture Finance Collections Voicebot

## Overview
Maya is a Vapi-based outbound collections voice agent for the Kapture Finance take-home assignment.

The prototype authenticates Rahul Sharma before revealing any debt information, retrieves mock account details,
captures a promise-to-pay (PTP), can trigger a mock payment link, and records final call dispositions such as
`promise_to_pay` and `already_paid`.

## Demo Customer
- Customer: Rahul Sharma
- Loan: Personal Loan
- Overdue EMI: ₹8,499
- Days past due: 12
- Demo DOB: 1998-05-12
- Registered phone last four digits: 4321

## Architecture
Vapi handles voice orchestration:
`Call -> Soniox STT -> GPT-4.1 -> Tool/API calls -> Vapi Elliot TTS -> Customer`

The tool server is a local FastAPI application exposed to Vapi through an ngrok HTTPS tunnel.

See `architecture_diagram.png` and `Kapture_Finance_HLD.pdf`.

## Vapi Choices
- Transcriber: Soniox STT RT v5
  - Selected for low-latency English transcription during the prototype.
- Model: GPT-4.1
  - Selected for reliable structured instruction following and tool selection.
- Voice: Vapi Elliot v2
  - Selected for a natural, professional collections-agent tone.

During the build, the Vapi dashboard showed approximate component latencies of:
- STT: ~410 ms
- Model: ~690 ms
- TTS: ~430 ms

## Backend Setup

### 1. Create and activate the environment
```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run FastAPI
```powershell
uvicorn app.main:app --reload --port 8000
```

Swagger:
```text
http://127.0.0.1:8000/docs
```

### 4. Run ngrok
```powershell
ngrok http 8000
```

Current prototype URL used during the build:
```text
https://kapture-finance-voice-agent.onrender.com
```

> Important: free ngrok URLs can change after restart. If the URL changes, update every Vapi API Request tool.

## Tool Endpoints
- `POST /verify-customer`
- `POST /account-details`
- `POST /promise-to-pay`
- `POST /send-payment-link`
- `POST /mark-disposition`

See `tool_schemas.json` for schemas.

## State-Enforced Authentication
The backend does not rely only on the prompt.

1. `verify_customer` checks full name, DOB, and phone last four digits.
2. On success, the backend creates an `auth_token`.
3. Sensitive endpoints such as `/account-details`, `/promise-to-pay`, and `/send-payment-link` require a valid token.
4. A server restart invalidates the in-memory demo sessions.

This prevents the LLM from simply deciding that a caller is verified.

## Verified Demo Paths

### Successful Promise-to-Pay
Expected tool sequence:
1. `verify_customer`
2. `get_account_details`
3. `log_promise_to_pay`
4. `send_payment_link` (if accepted)
5. `mark_disposition` -> `promise_to_pay`

### Already Paid Edge Case
After verification, customer says the EMI was already paid.
Expected behavior:
- Maya does not argue or ask the customer to pay again.
- Maya acknowledges the statement.
- `mark_disposition` is called with `already_paid`.
- Call ends politely.

Tool execution was verified using Vapi logs and the ngrok inspector.

## What Broke and How It Was Debugged

### 1. ngrok command not found
WinGet installed `ngrok.exe`, but its folder was not on PATH.
The binary was located under the WinGet packages directory and run via full path.

### 2. ngrok agent too old
The original agent was v3.3.1 and the account required >=3.20.
The agent was updated to v3.39.10.

### 3. Maya said "I'll verify" and then stayed silent
The assistant initially described the verification action without actually invoking the tool.
This caused a silence timeout.

Fixes:
- strengthened the system prompt with mandatory exact tool-call rules;
- strengthened the `verify_customer` tool description;
- removed filler/holding language around tool calls;
- added explicit tool-failure behavior;
- verified tool execution using Vapi/ngrok logs.

### 4. Prompt-only authentication was not strong enough
The initial backend stored a global `verified=True` flag.
It was replaced with generated authentication tokens so sensitive calls require state enforced by the server.

## Compliance / Guardrails
- No debt disclosure before successful verification.
- No debt disclosure to a third party or wrong person.
- No threats, harassment, shaming, or invented consequences.
- Do-not-call requests stop the collection conversation.
- Already-paid and dispute flows do not demand duplicate payment.
- Tool/account information is never fabricated.

## Limitations / Improvements
With more time:
- replace in-memory session state with Redis or a persistent datastore;
- bind auth sessions to Vapi `call_id`;
- use a real CRM/loan account API;
- integrate a real SMS/WhatsApp payment-link provider;
- add callback/human-agent escalation;
- add automated Vapi simulations/evals for privacy and tool calling;
- add bilingual EN/HI regression tests;
- deploy the FastAPI server rather than depending on a temporary ngrok URL;
- add signed webhook authentication and secret management.

## Submission Contents
- `Kapture_Finance_HLD.docx`
- `Kapture_Finance_HLD.pdf`
- `architecture_diagram.png`
- `SYSTEM_PROMPT.json`
- `tool_schemas.json`
- `README.md`
- `SUBMISSION_CHECKLIST.md`
