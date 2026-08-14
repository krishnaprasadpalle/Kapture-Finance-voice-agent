from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
import uuid

app = FastAPI(
    title="Kapture Finance Voice Agent API",
    version="1.0.0"
)

# Mock customer database
CUSTOMERS = {

    "rahul-sharma": {
        "full_name": "Rahul Sharma",
        "date_of_birth": "1998-05-12",
        "phone_last4": "4321",
        "verified": False,
        "loan_type": "Personal Loan",
        "overdue_emi": 8499,
        "days_past_due": 12,
    }
}

AUTH_SESSIONS = {}


class VerifyCustomerRequest(BaseModel):
    full_name: str
    date_of_birth: str
    phone_last4: str


class PromiseToPayRequest(BaseModel):
    auth_token: str
    customer_name: str
    amount: float
    ptp_date: str


class PaymentLinkRequest(BaseModel):
    auth_token: str
    customer_name: str
    amount: float


class DispositionRequest(BaseModel):
    customer_name: str
    disposition: str
    notes: str | None = None


class AuthRequest(BaseModel):
    auth_token: str



@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Kapture Finance Voice Agent Backend"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }



@app.post("/verify-customer")
def verify_customer(data: VerifyCustomerRequest):
    customer = CUSTOMERS["rahul-sharma"]

    is_verified = (
        data.full_name.strip().lower() == customer["full_name"].lower()
        and data.date_of_birth == customer["date_of_birth"]
        and data.phone_last4 == customer["phone_last4"]
    )

    if not is_verified:
        return {
            "verified": False,
            "message": "Customer verification failed"
        }

    auth_token = str(uuid.uuid4())

    AUTH_SESSIONS[auth_token] = {
        "customer_id": "rahul-sharma",
        "verified": True
    }

    return {
        "verified": True,
        "auth_token": auth_token,
        "message": "Customer verified successfully"
    }



@app.post("/account-details")
def get_account_details(data: AuthRequest):

    session = AUTH_SESSIONS.get(data.auth_token)

    if not session or not session["verified"]:
        raise HTTPException(
            status_code=403,
            detail="Valid customer verification required"
        )

    customer = CUSTOMERS[session["customer_id"]]

    return {
        "customer_name": customer["full_name"],
        "loan_type": customer["loan_type"],
        "overdue_emi": customer["overdue_emi"],
        "days_past_due": customer["days_past_due"]
    }


@app.post("/promise-to-pay")
def log_promise_to_pay(data: PromiseToPayRequest):
    session = AUTH_SESSIONS.get(data.auth_token)

    if not session or not session["verified"]:
        raise HTTPException(
            status_code=403,
            detail="Valid customer verification required"
        )

    return {
        "success": True,
        "message": "Promise to pay logged successfully",
        "promise": {
            "customer_name": data.customer_name,
            "amount": data.amount,
            "ptp_date": data.ptp_date
        }
    }

@app.post("/send-payment-link")
def send_payment_link(data: PaymentLinkRequest):
    session = AUTH_SESSIONS.get(data.auth_token)

    if not session or not session["verified"]:
        raise HTTPException(
            status_code=403,
            detail="Valid customer verification required"
        )

    customer = CUSTOMERS[session["customer_id"]]

    mock_payment_link = "https://pay.kapturefinance.mock/rahul-sharma"

    return {
        "success": True,
        "message": "Payment link sent successfully",
        "channel": "SMS",
        "phone_number": customer["phone_number"],
        "amount": data.amount,
        "payment_link": mock_payment_link
    }


@app.post("/mark-disposition")
def mark_disposition(data: DispositionRequest):
    allowed_dispositions = [
        "promise_to_pay",
        "already_paid",
        "do_not_call",
        "wrong_person",
        "dispute",
        "hardship",
        "callback_requested",
        "hostile",
        "no_response",
    ]

    if data.disposition not in allowed_dispositions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid disposition. Allowed values: {allowed_dispositions}"
        )

    return {
        "success": True,
        "message": "Disposition logged successfully",
        "disposition": data.disposition,
        "customer_name": data.customer_name,
        "notes": data.notes,
    }