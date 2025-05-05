#!/usr/bin/env python3

import sys
import os
import re
from datetime import datetime

# Root of all WATO config folders
WATO_ROOT = "/omd/sites/monitoring/etc/check_mk/conf.d/wato"

if len(sys.argv) != 2:
    print("3 Contract Expiration - ERROR: Hostname not provided")
    exit(3)

hostname = sys.argv[1]
expiration_str = None

# Regex pattern to find contract_expiration for a given host
host_regex = re.compile(
    rf".*'{re.escape(hostname)}'.*?'contract_expiration'\s*:\s*'(\d{{2}}/\d{{2}}/\d{{4}})'"
)

try:
    # Walk through all subfolders to find hosts.mk files
    for root, dirs, files in os.walk(WATO_ROOT):
        for file in files:
            if file == "hosts.mk":
                full_path = os.path.join(root, file)
                with open(full_path, "r") as f:
                    for line in f:
                        match = host_regex.search(line.strip())
                        if match:
                            expiration_str = match.group(1)
                            break
                if expiration_str:
                    break  # Found the host, no need to keep searching
        if expiration_str:
            break

    if not expiration_str:
        print(f"3 Contract Expiration - ERROR: No contract_expiration found for host '{hostname}' in any hosts.mk")
        exit(3)

    # Evaluate expiration
    expiration_date = datetime.strptime(expiration_str, "%m/%d/%Y")
    today = datetime.now()
    days_left = (expiration_date - today).days

    if days_left < 0:
        print(f"2 Contract Expiration - EXPIRED {abs(days_left)} days ago on {expiration_date.strftime('%m/%d/%Y')}")
    elif days_left <= 30:
        print(f"1 Contract Expiration - Expiring soon: {days_left} days left (on {expiration_date.strftime('%m/%d/%Y')})")
    else:
        print(f"0 Contract Expiration - Valid: {days_left} days left (expires {expiration_date.strftime('%m/%d/%Y')})")

except Exception as e:
    print(f"3 Contract Expiration - ERROR: {str(e)}")
    exit(3)
