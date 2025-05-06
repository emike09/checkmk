#!/usr/bin/env python3

import sys
import os
import re
from datetime import datetime

# === CONFIGURABLE WARNING/CRITICAL THRESHOLDS ===
WARN_DAYS = 30
CRIT_DAYS = 15

# === WATO folder path ===
WATO_ROOT = "/omd/sites/monitoring/etc/check_mk/conf.d/wato"

# === Get hostname from CLI args ===
if len(sys.argv) != 2:
    print("3 Contract Expiration Date - UNKNOWN - Hostname not provided")
    sys.exit(3)

hostname = sys.argv[1]
expiration_str = None

# === Regex to find 'contract_expiration' for the host ===
host_regex = re.compile(
    rf".*'{re.escape(hostname)}'.*?'contract_expiration'\s*:\s*'(\d{{2}}/\d{{2}}/\d{{4}})'"
)

try:
    # Search recursively for hosts.mk entries
    for root, dirs, files in os.walk(WATO_ROOT):
        for file in files:
            if file == "hosts.mk":
                with open(os.path.join(root, file), "r") as f:
                    for line in f:
                        match = host_regex.search(line.strip())
                        if match:
                            expiration_str = match.group(1)
                            break
                if expiration_str:
                    break
        if expiration_str:
            break

    if not expiration_str:
        print("3 Contract Expiration Date - UNKNOWN - No contract_expiration found for host '{}'".format(hostname))
        sys.exit(3)

    # Parse the expiration date
    expiration_date = datetime.strptime(expiration_str, "%m/%d/%Y")
    today = datetime.now()
    days_left = (expiration_date - today).days

    # Determine state
    if days_left < 0:
        exit_code = 2
        state_text = f"CRITICAL - EXPIRED {abs(days_left)} days ago (on {expiration_date.strftime('%m/%d/%Y')})"
    elif days_left <= CRIT_DAYS:
        exit_code = 2
        state_text = f"CRITICAL - Only {days_left} days left (expires {expiration_date.strftime('%m/%d/%Y')})"
    elif days_left <= WARN_DAYS:
        exit_code = 1
        state_text = f"WARNING - {days_left} days left (expires {expiration_date.strftime('%m/%d/%Y')})"
    else:
        exit_code = 0
        state_text = f"OK - {days_left} days left (expires {expiration_date.strftime('%m/%d/%Y')})"

    # Final output in proper Nagios format
    print(f"{exit_code} Contract Expiration Date - {state_text}")
    sys.exit(exit_code)

except Exception as e:
    print(f"3 Contract Expiration Date - UNKNOWN - Error: {str(e)}")
    sys.exit(3)
