"""Minecraft legacy language file downloader."""

import hashlib
import json
import sys
import tomllib as tl
from pathlib import Path
from zipfile import ZipFile

import requests as r

TARGET_VERSIONS = {
    #    "legacy": "1.7",
    "1.7.3": "1.7.3",
    "1.7.4": "1.7.4",
    "1.7.10": "1.7.10",
    "14w25a": "14w25a",
    "14w31a": "14w31a",
    "1.8": "1.8.9",
    "1.9": "1.9.4",
    "1.10": "1.10.2",
    "1.11": "1.11.2",
    "1.12": "1.12.2",
    "1.13": "1.13",
    "1.13.1": "1.13.2",
    "1.14": "1.14.4",
    "1.15": "1.15.2",
    "1.16": "1.16.5",
    "1.17": "1.17.1",
    "1.18": "1.18.2",
    "1.19": "1.19.2",
}

# The absolute path of the script's directory.
SCRIPT_DIR = Path(__file__).resolve().parent

# Load configuration from the TOML file
CONFIG_PATH = SCRIPT_DIR / "configuration.toml"
if not CONFIG_PATH.exists():
    print(
        "Configuration file not found. "
        "Please place 'configuration.toml' in the same directory as the script."
    )
    sys.exit()

with open(CONFIG_PATH, "rb") as f:
    config = tl.load(f)

OUTPUT_DIR = SCRIPT_DIR / config["legacy_assets_output_folder"]
REMOVE_CLIENT_JAR: bool = config["remove_client"]
LANGUAGE_LIST: list[str] = config["language_list"]


def get_response(url: str) -> r.Response | None:
    """Send a GET request to the specified URL and return the response."""
    try:
        resp = r.get(url, timeout=120)
        resp.raise_for_status()
        return resp
    except r.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return None


def download_file(url: str, file_name: str, file_path: Path, expected_sha1: str) -> bool:
    """Download a file, verify its SHA1 checksum, and retry on failure."""
    for attempt in range(3):
        print(f"Downloading '{file_name}' (Attempt {attempt + 1}/3)...")
        response = get_response(url)
        if not response:
            print(f"Download failed for '{file_name}'. Retrying...\n")
            continue

        with open(file_path, "wb") as f:
            f.write(response.content)

        with open(file_path, "rb") as f:
            actual_sha1 = hashlib.file_digest(f, "sha1").hexdigest()

        if actual_sha1 == expected_sha1:
            size_in_bytes = file_path.stat().st_size
            size_mb = round(size_in_bytes / 1048576, 2)
            print(f"SHA1 checksum consistent for {file_name}. File size: {size_mb:.2f} MB")
            return True

        print(
            f"SHA1 checksum mismatch for {file_name}. Expected {expected_sha1}, got {actual_sha1}."
        )
        print(f"Retrying (Attempt {attempt + 2}/3).\n")
    else:
        print(f"Failed to download '{file_name}' correctly after 3 attempts.\n")
        if file_path.exists():
            file_path.unlink()
        return False


def extract_en_us_from_jar(client_jar_path: Path, version_output_dir: Path, lang_base_path: str):
    """Extract only the en_us language file from a client.jar using the specified base path."""
    print(f"Extracting 'en_us' from {client_jar_path.name}...")
    try:
        with ZipFile(client_jar_path) as client_zip:
            search_paths = [
                (f"{lang_base_path}en_us.json", "en_us.json"),
                (f"{lang_base_path}en_us.lang", "en_us.lang"),
            ]
            for zip_path, out_name in search_paths:
                if zip_path in client_zip.namelist():
                    print(f"  Found '{zip_path}', extracting...")
                    with (
                        client_zip.open(zip_path) as source,
                        open(version_output_dir / out_name, "wb") as target,
                    ):
                        target.write(source.read())
                    return
            print("  - 'en_us' language file not found in this version's JAR.")
    except Exception as e:
        print(f"An error occurred during extraction: {e}")


def main():
    """Download and extract language files for all target versions."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    version_manifest_path = OUTPUT_DIR / "version_manifest_v2.json"
    print("Fetching global version manifest...")
    manifest_response = get_response(
        "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
    )

    if manifest_response:
        version_manifest_json = manifest_response.json()
        with open(version_manifest_path, "wb") as f:
            f.write(manifest_response.content)
        print("Successfully fetched global manifest.\n")
    elif version_manifest_path.exists():
        print("Failed to fetch manifest. Using local copy.\n")
        with open(version_manifest_path, encoding="utf-8") as f:
            version_manifest_json = json.load(f)
    else:
        print("Failed to fetch manifest and no local copy is available. Exiting.")
        sys.exit()

    for output_folder_name, version_id in TARGET_VERSIONS.items():
        print(f"--- Processing version: {version_id} ({output_folder_name}) ---")
        version_info: dict = next(
            (v for v in version_manifest_json["versions"] if v["id"] == version_id), {}
        )

        if not version_info:
            print(f"Version '{version_id}' not found in manifest. Skipping.\n")
            continue

        # Determine the correct language path based on the version folder name
        legacy_folders = ["legacy", "1.7.3", "1.7.4"]
        lang_base_path = "lang/" if output_folder_name in legacy_folders else "minecraft/lang/"

        version_output_dir = OUTPUT_DIR / output_folder_name
        version_output_dir.mkdir(exist_ok=True)
        temp_download_dir = OUTPUT_DIR / version_id
        temp_download_dir.mkdir(exist_ok=True)

        version_manifest_resp = get_response(version_info["url"])
        if not version_manifest_resp:
            print(f"Could not fetch manifest for {version_id}. Skipping.\n")
            continue

        client_manifest = version_manifest_resp.json()

        if "assetIndex" in client_manifest:
            print(
                "Found asset index. "
                f"Searching for non-en_us languages with path '{lang_base_path}'..."
            )
            asset_index_info = client_manifest["assetIndex"]
            asset_index_resp = get_response(asset_index_info["url"])

            if asset_index_resp:
                asset_objects = asset_index_resp.json().get("objects", {})
                versions_1_15_and_up = ["1.15", "1.16", "1.17", "1.18", "1.19"]

                for lang_code in LANGUAGE_LIST:
                    if lang_code == "en_us":
                        continue

                    if lang_code in ["lzh", "zh_hk"] and version_id not in versions_1_15_and_up:
                        print(f"Skipping '{lang_code}' for version {version_id} (older than 1.15).")
                        continue

                    lang_parts = lang_code.split("_")
                    lang_code_upper = (
                        f"{lang_parts[0]}_{lang_parts[1].upper()}"
                        if len(lang_parts) > 1
                        else lang_code
                    )

                    if lang_code in ["lzh", "zh_hk"]:
                        search_keys = [(f"{lang_base_path}{lang_code}.json", f"{lang_code}.json")]
                    else:
                        search_keys = [
                            (f"{lang_base_path}{lang_code}.json", f"{lang_code}.json"),
                            (f"{lang_base_path}{lang_code}.lang", f"{lang_code}.lang"),
                            (f"{lang_base_path}{lang_code_upper}.lang", f"{lang_code_upper}.lang"),
                        ]

                    found_asset = False
                    for key, out_name in search_keys:
                        if key in asset_objects:
                            asset = asset_objects[key]
                            file_hash = asset["hash"]
                            file_url = f"https://resources.download.minecraft.net/{file_hash[:2]}/{file_hash}"
                            download_file(
                                file_url, out_name, version_output_dir / out_name, file_hash
                            )
                            found_asset = True
                            break

                    if not found_asset:
                        print(
                            f"Language '{lang_code}' not found in asset index with specified paths."
                        )
            else:
                print(f"Could not fetch asset index for {version_id}. Skipping asset downloads.\n")
        else:
            print(f"Version {version_id} does not have an assetIndex. Skipping asset downloads.")

        if "en_us" in LANGUAGE_LIST:
            print(f"\nHandling 'en_us' via client.jar (searching in '{lang_base_path}')...")
            client_downloads = client_manifest.get("downloads", {})
            client_jar_info = client_downloads.get("client", {})
            client_url = client_jar_info.get("url")
            client_sha1 = client_jar_info.get("sha1")

            if client_url and client_sha1:
                client_jar_path = temp_download_dir / "client.jar"
                if download_file(client_url, f"{version_id}.jar", client_jar_path, client_sha1):
                    extract_en_us_from_jar(client_jar_path, version_output_dir, lang_base_path)

                if REMOVE_CLIENT_JAR and client_jar_path.exists():
                    print(f"Removing temporary file {client_jar_path.name}...")
                    client_jar_path.unlink()
            else:
                print(f"No client.jar info found for {version_id} to extract en_us. Skipping.\n")

        try:
            if not any(temp_download_dir.iterdir()):
                temp_download_dir.rmdir()
        except OSError:
            pass
        print(f"--- Finished processing {version_id}. ---\n")


if __name__ == "__main__":
    main()
