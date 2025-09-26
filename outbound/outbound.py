import os
from dotenv import load_dotenv

# ── load .env into os.environ ─────────────────────────────────────────────
load_dotenv()
# ────────────────────────────────────────────────────────────────────────────

import sys
import argparse
import logging
import requests
import random
import requests
import phonenumbers

# === CONFIGURE LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# DEFAULT BOT ID
DEFAULT_BOT_ID = "d608e2af-a089-4b5a-973d-7f59b42bbdb0"
VAPI_PHONE_NUMBER_ID_1 = "01b4edd4-5c58-4dff-9b28-9f4085b70946"
VAPI_PHONE_NUMBER_ID_2 = "bb4a763d-a45b-4fee-8c6f-9dcad25a8ee7"
VAPI_PHONE_NUMBER_ID_3 = "69aa2ac1-dad3-4769-9e4f-28768aeb04d1"
TWILIO_PHONE_NUMBER_ID = "8d77de4f-c464-4441-915d-1622af72baa2"

# Lab number, use this
LAB_NUMBER = "36442f48-d61f-46dd-bdb9-a64ae290f0e8"

my_number_pool = [LAB_NUMBER]


def get_available_phone_number(pool=[], used_numbers=[]):
    """
    Get an available phone number from the pool that is not in used_numbers.
    If a number has hit max usage, pass that in in used_numbers array
    This function will use a random number from the pool that is not in used_numbers.
    """
    if len(used_numbers) >= len(pool):
        logger.error("All phone numbers in the pool are already used.")
        sys.exit(1)
    while True:
        idx = random.randint(0, len(pool) - 1)
        if pool[idx] not in used_numbers:
            return pool[idx]


def validate_phone_number(p):
    if not p.strip().startswith("+"):
        number = phonenumbers.parse(p, region="US")
    else:
        number = phonenumbers.parse(p)  # region not needed if + is present

    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)


def call_outbound(to, fro, bot_id=None):
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

    if to == "911":
        logger.error("You cannot call 911 using this script. Please use a real phone.")
        sys.exit(1)

    url = "https://api.vapi.ai/call"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "assistantId": bot_id,
        "assistantOverrides": {
            "variableValues": {
                # any liquid variables you want to set for prompt interpolation
            }
        },
        "phoneNumberId": fro,
        "customer": {"number": to},
    }

    return requests.request("POST", url, headers=headers, json=payload)


def main():
    parser = argparse.ArgumentParser(description="Trigger an outbound Vapi call")
    parser.add_argument("--bot_id", required=False, help="Your Vapi bot ID")
    parser.add_argument(
        "--to", required=True, help="Destination phone numbers (+E.164)"
    )
    parser.add_argument(
        "--used_up",
        required=False,
        help="from phone numbers already used (comma-separated)",
    )
    args = parser.parse_args()

    try:
        tos = set([validate_phone_number(p) for p in args.to.split(",")])
        used_up = args.used_up.split(",") if args.used_up else []
        print(used_up, len(used_up))
        for to in tos:
            fro = get_available_phone_number(my_number_pool, used_up)
            result = call_outbound(to, fro, args.bot_id)
            logger.info(
                f"Call initiated successfully from {fro} to {to}: {result.status_code} {result.text}"
            )

    except Exception as exc:
        logger.error(f"Failed to make call: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
