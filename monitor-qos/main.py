#!/usr/bin/env python3
"""
This script performs a LibreSpeed test via HTTP every hour and prints the results with a timestamp.
"""

import subprocess
import json
import time
from datetime import datetime, timezone

def run_fast_test():
    try:
        # Call fast-cli with JSON output
        proc = subprocess.run(
            ["fast", "--json"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(proc.stdout)
        upload = data.get("uploaded")
        upload_unit = data.get("uploadUnit")
        if upload is not None and upload_unit == "Kbps":
            upload_mbps = upload / 1024
        else:
            upload_mbps = upload
        return {
            "download_mbps": data.get("downloadSpeed"),
            "downloaded_mb": data.get("downloaded"),
            "upload_mbps": upload_mbps,
            "latency_ms": data.get("latency"),
            "buffer_bloat": data.get("bufferBloat"),
            "user_location": data.get("userLocation"),
            "client_ip": data.get("userIp")
        }
    except subprocess.CalledProcessError as e:
        return {"error": f"fast-cli error: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}"}

if __name__ == "__main__":
    while True:
        result = run_fast_test()
        timestamp = datetime.now(timezone.utc).isoformat()
        print(f"{timestamp} LibreSpeed test result:", result)
        time.sleep(3600)  # wait one hour