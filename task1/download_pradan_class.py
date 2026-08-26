#!/usr/bin/env python3
"""
PRADAN Data Download Script for CLASS L1
"""

import threading
import time
from pathlib import Path
from urllib.parse import urlparse
import requests

MAX_RETRIES = 5
RETRY_WAIT_SECONDS = 15
CHUNK_SIZE_MB = 8

url_prefix = "https://pradan.issdc.gov.in"

cookie_string = (
    "FGTServer=5DB1E9B68132028CF7976EE4DF4CBB47C2F908C978D8DADB79380837E680FA20672DD56B0798AF381BF6;"
    "FGTServer=5DB1E9B68132028CF7976EE4DF4CBB47C2F908C978D8DADB79380837E680FA20672DD56B0798AF381BF6;"
    "JSESSIONID=e1cbb5d7f38a7e2187bc658b6db1;JSESSIONID=e1cb556e5df4ff13fb44fc2dc009;"
    "FGTServer=5DB1E9B68132028CF7976EE4DF4CBB47C2F908C978D8DADB79380837E680FA20672DD56B0798AF381BF6;"
    "OAuth_Token_Request_State=c5adcac6-2292-4ad3-b35c-83769834febd;"
)

headers = {"Cookie": cookie_string}

# Full sequence covering 2020-05-29 around 10:40:00 to 10:43:00
# Starting from 10:40:04 up to 10:43:00 (with step of 8s, millisecond offset 257)
base_path = "/ch2/protected/downloadData/POST_OD/isda_archive/ch2_bundle/cho_bundle/nop/cla_collection/cla/data/calibrated/2020/05/29"

# We generate the full set of 8s chunks from 10:40:04 to 10:43:00:
timestamps = [
    ("104004257", "104012257"),
    ("104012257", "104020257"),
    ("104020257", "104028257"),
    ("104028257", "104036257"),
    ("104036257", "104044257"),
    ("104044257", "104052257"),
    ("104052257", "104100257"),
    ("104100257", "104108257"),
    ("104108257", "104116257"),
    ("104116257", "104124257"),
    ("104124257", "104132257"),
    ("104132257", "104140257"),
    ("104140257", "104148257"),
    ("104148257", "104156257"),
    ("104156257", "104204257"),
    ("104204257", "104212257"),
    ("104212257", "104220257"),
    ("104220257", "104228257"),
    ("104228257", "104236257"),
    ("104236257", "104244257"),
    ("104244257", "104252257"),
    ("104252257", "104300257"),
]

data_file_paths = [
    "/ch2/protected/downloadData/POST_OD/isda_archive/ch2_bundle/cho_bundle/nop/cla_collection/cla/data/derived/Al-Si/ch2_cla_l1-5_map_al-si_combined_v1.tif?class",
    "/ch2/protected/downloadData/POST_OD/isda_archive/ch2_bundle/cho_bundle/nop/cla_collection/cla/data/derived/Mg-Al/ch2_cla_l1-5_map_mg-al_combined_v1.tif?class",
]

for t_start, t_end in timestamps:
    data_file_paths.append(
        f"{base_path}/ch2_cla_l1_20200529T{t_start}_20200529T{t_end}.fits?class"
    )

host_name = urlparse(url_prefix).netloc
base_dir = Path(r"c:\Users\invet\OneDrive\Desktop\Inter-IIT\Datasets")

session = requests.Session()


def keep_alive():
    keep_alive_url = url_prefix + "/ch2/protected/payload.xhtml"
    for _ in range(144):
        time.sleep(300)
        try:
            session.get(keep_alive_url, headers=headers, timeout=(15, 30))
        except Exception as e:
            print(f"\n[KEEP-ALIVE ERROR] {e}")


threading.Thread(target=keep_alive, daemon=True).start()

download_count = 0

for file_index, file_path in enumerate(data_file_paths, start=1):
    url = url_prefix + file_path
    clean_path = file_path.split("?")[0]
    relative_path = clean_path.lstrip("/")
    final_file = base_dir / host_name / relative_path
    partial_file = Path(str(final_file) + ".part")

    final_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n[{file_index}/{len(data_file_paths)}] Downloading {final_file.name}...")

    if final_file.exists() and final_file.stat().st_size > 0:
        print("Already downloaded. Skipping.")
        download_count += 1
        continue

    success = False
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resume_from = 0
            request_headers = headers.copy()
            if partial_file.exists():
                resume_from = partial_file.stat().st_size
                request_headers["Range"] = f"bytes={resume_from}-"

            with session.get(
                url,
                headers=request_headers,
                stream=True,
                timeout=(30, 120),
                allow_redirects=False,
            ) as response:
                if response.status_code not in (200, 206):
                    raise RuntimeError(f"HTTP {response.status_code}")

                mode = "ab" if resume_from > 0 else "wb"
                downloaded = resume_from
                with open(partial_file, mode) as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE_MB * 1024 * 1024):
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded += len(chunk)

            partial_file.rename(final_file)
            size_mb = final_file.stat().st_size / (1024**2)
            print(f"-> Completed ({size_mb:.4f} MB)")
            download_count += 1
            success = True
            break
        except Exception as e:
            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(2)

    if not success:
        print(f"Failed to download: {clean_path}")

print(f"\nAll downloads completed: {download_count}/{len(data_file_paths)} files.")

