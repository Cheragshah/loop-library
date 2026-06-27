#!/usr/bin/env bash
# Refresh the trending loop catalog (Excel + dashboard). Wire into cron/launchd.
cd "$(dirname "$0")/.." || exit 1
/usr/bin/python3 collect.py >> "$(dirname "$0")/../data/refresh.log" 2>&1
