"""Base script for downloading Minecraft language files."""

import json
import sys
import tomllib as tl
from datetime import datetime
from pathlib import Path

import requests as r

# The absolute path of the script's directory.
SCRIPT_DIR = Path(__file__).resolve().parent

CONFIG_PATH = SCRIPT_DIR / "configuration.toml"
if not CONFIG_PATH.exists():
    print(
        "Configuration file not found. "
        "Please place 'configuration.toml' in the same directory as the script."
    )
    sys.exit()

with open(CONFIG_PATH, "rb") as f:
    config = tl.load(f)

MINECRAFT_VERSION: str = config["version"]
VERSIONS_DIR = SCRIPT_DIR / config["version_folder"]
OUTPUT_DIR = SCRIPT_DIR / config["output_folder"]
REMOVE_CLIENT_JAR: bool = config["remove_client"]
LANGUAGE_LIST: list[str] = config["language_list"]

VERSIONS_DIR.mkdir(exist_ok=True)

version_manifest_path = VERSIONS_DIR / "version_manifest_v2.json"
try:
    print("Fetching version manifest 'version_manifest_v2.json'...\n")
    manifest_response = r.get(
        "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
        timeout=60,
    )
    manifest_response.raise_for_status()
    version_manifest_json = manifest_response.json()
    with open(version_manifest_path, "wb") as f:
        f.write(manifest_response.content)
except r.exceptions.RequestException:
    if version_manifest_path.exists():
        print("Failed to fetch version manifest. Using the existing local copy.\n")
        with open(version_manifest_path, encoding="utf-8") as f:
            version_manifest_json = json.load(f)
    else:
        print("Failed to fetch version manifest and no local copy is available.")
        print("Please check your internet connection or provide a valid manifest file.")
        sys.exit()

if MINECRAFT_VERSION == "latest":
    MINECRAFT_VERSION = version_manifest_json["latest"]["snapshot"]

version_info: dict = next(
    (v for v in version_manifest_json["versions"] if v["id"] == MINECRAFT_VERSION), {}
)

if not version_info:
    print("The specified version could not be found in the version manifest.")
    print("Please ensure the version number is correct.")
    sys.exit()

LANG_DIR = VERSIONS_DIR / MINECRAFT_VERSION
print(f"Selected version: {MINECRAFT_VERSION}\n")

# Check if the selected version is 18w02a or newer, which uses JSON format.
release_time_18w02a = datetime.fromisoformat("2018-01-10T11:54:55+00:00")
release_time_chosen_version = datetime.fromisoformat(version_info["releaseTime"])

if release_time_18w02a > release_time_chosen_version:
    print("Selected version uses the legacy .lang format for language files.")
    print("Please choose version 18w02a or newer.")
    sys.exit()
