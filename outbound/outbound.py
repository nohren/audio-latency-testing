import os
from dotenv import load_dotenv

# ── load .env into os.environ ─────────────────────────────────────────────
load_dotenv()  
# ────────────────────────────────────────────────────────────────────────────

import sys
import argparse
import logging
import requests
# import datetime
# from time import sleep
import requests

# === CONFIGURE LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

#DEFAULT BOT ID
DEFAULT_BOT_ID = "d608e2af-a089-4b5a-973d-7f59b42bbdb0"
VAPI_PHONE_NUMBER_ID = "01b4edd4-5c58-4dff-9b28-9f4085b70946"
TWILIO_PHONE_NUMBER_ID = "8d77de4f-c464-4441-915d-1622af72baa2"

def call_outbound(to, bot_id=None):
    api_key = os.getenv("VAPI_API_KEY")
    bot_id = bot_id or DEFAULT_BOT_ID
    if not api_key:
        logger.error("Missing VAPI_API_KEY environment variable")
        sys.exit(1)

    if not bot_id:
        logger.error("Missing bot id environment variable or command line argument")
        sys.exit(1)

    if not to:
        logger.error("Missing destination phone number")
        sys.exit(1)

    if to == '911':
        logger.error("You cannot call 911 using this script. Please use a real phone.")
        sys.exit(1)

    url = "https://api.vapi.ai/call"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    payload = {
    "assistantId": bot_id,
    "phoneNumberId": VAPI_PHONE_NUMBER_ID,
    "customer": {
        "number": to
        }
    }

    return requests.request("POST", url, headers=headers, json=payload)


def main():
    parser = argparse.ArgumentParser(description="Trigger an outbound Vapi call")
    parser.add_argument("--bot_id",     required=False, help="Your Vapi bot ID")
    parser.add_argument("--to",      required=True, help="Destination phone numbers (+E.164)")
    args = parser.parse_args()

    try:
        tos = args.to.split(",")
        for to in tos:
            result = call_outbound(to, args.bot_id)
            logger.info(f"Call initiated successfully: {result.status_code} {result.text}")
        
    except Exception as exc:
        logger.error(f"Failed to make call: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
