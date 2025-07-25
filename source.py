"""Minecraft language file downloader."""

import hashlib
import sys
from pathlib import Path
from zipfile import ZipFile

import requests as r

from base import LANG_DIR, LANGUAGE_LIST, REMOVE_CLIENT_JAR, version_info


def get_response(url: str) -> r.Response:
    """Send a GET request to the specified URL and return the response.

    Args:
        url (str): The URL to request.

    Returns:
        r.Response: The response object.

    """
    try:
        resp = r.get(url, timeout=60)
        resp.raise_for_status()
        return resp
    except r.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        sys.exit()


def download_file(url: str, file_name: str, file_path: Path, expected_sha1: str) -> None:
    """Download a file, verify its SHA1 checksum, and retry on failure.

    Args:
        url (str): The URL to download from.
        file_name (str): The name of the file for logging purposes.
        file_path (Path): The path to save the file.
        expected_sha1 (str): The expected SHA1 hash of the file.

    """
    for attempt in range(3):
        with open(file_path, "wb") as f:
            f.write(get_response(url).content)

        with open(file_path, "rb") as f:
            actual_sha1 = hashlib.file_digest(f, "sha1").hexdigest()

        if actual_sha1 == expected_sha1:
            size_in_bytes = file_path.stat().st_size
            size_mb = round(size_in_bytes / 1048576, 2)
            size_kb = round(size_in_bytes / 1024, 2)
            size_str = f"{size_mb} MB" if size_in_bytes > 1048576 else f"{size_kb} KB"
            print(f"SHA1 checksum consistent. File size: {size_in_bytes} B ({size_str})\n")
            return

        print(f"SHA1 checksum mismatch for {file_name}. Retrying (Attempt {attempt + 2}/3).\n")
    else:
        print(f"Failed to download '{file_name}' correctly after 3 attempts.\n")
        file_path.unlink()  # Clean up failed download


LANG_DIR.mkdir(exist_ok=True)

# Fetch client manifest
client_manifest_url = version_info["url"]
client_filename = client_manifest_url.rsplit("/", 1)[-1]
print(f"Fetching client manifest '{client_filename}'...")
client_manifest = get_response(client_manifest_url).json()

# Fetch asset index
asset_index_url = client_manifest["assetIndex"]["url"]
asset_index_filename = asset_index_url.rsplit("/", 1)[-1]
print(f"Fetching asset index '{asset_index_filename}'...\n")
asset_index = get_response(asset_index_url).json()["objects"]

# Download client.jar
client_url = client_manifest["downloads"]["client"]["url"]
client_sha1 = client_manifest["downloads"]["client"]["sha1"]
client_path = LANG_DIR / "client.jar"
print(f"Downloading client archive 'client.jar' ({client_sha1})...")
download_file(client_url, "client.jar", client_path, client_sha1)

# Extract en_us.json from client.jar
if client_path.exists():
    with ZipFile(client_path) as client_zip:
        print("Extracting 'en_us.json' from client.jar...")
        with (
            client_zip.open("assets/minecraft/lang/en_us.json") as source,
            open(LANG_DIR / "en_us.json", "wb") as target,
        ):
            target.write(source.read())

# Clean up client.jar if configured
if REMOVE_CLIENT_JAR and client_path.exists():
    print("Removing client.jar...\n")
    client_path.unlink()

# Download other specified language files
if "en_us" in LANGUAGE_LIST:
    LANGUAGE_LIST.remove("en_us")

for lang_code in LANGUAGE_LIST:
    lang_filename = f"{lang_code}.json"
    lang_asset_key = f"minecraft/lang/{lang_filename}"
    lang_asset = asset_index.get(lang_asset_key)

    if lang_asset:
        file_hash = lang_asset["hash"]
        print(f"Downloading language file '{lang_filename}' ({file_hash})...")
        download_url = f"https://resources.download.minecraft.net/{file_hash[:2]}/{file_hash}"
        download_file(
            download_url,
            lang_filename,
            LANG_DIR / lang_filename,
            file_hash,
        )
    else:
        print(f"Language file '{lang_filename}' not found in asset index.\n")

print("Download process completed.")
