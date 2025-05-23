import os
import requests
import subprocess
import zipfile
import time

VERSION_FILE = "/opt/outlawdart/version.txt"
VERSIONS_JSON_URL = "https://raw.githubusercontent.com/ravinance/outlawdart-patchs/main/version.json"
PATCH_TMP = "/tmp/outlaw_patch.zip"
GAME_PATH = "/opt/outlawdart/BD BUILDVmono.x86_64"
GAME_DIR = "/opt/outlawdart/"

# Lire version locale
local_version = "0.0.0"
if os.path.exists(VERSION_FILE):
    with open(VERSION_FILE, "r") as f:
        local_version = f.read().strip()

print(f"[UPDATER] Version actuelle : {local_version}")

# Télécharger versions.json
try:
    r = requests.get(VERSIONS_JSON_URL)
    r.raise_for_status()
    updates = r.json()["updates"]
except Exception as e:
    print(f"[UPDATER] Erreur lecture versions.json : {e}")
    subprocess.Popen(["bash", "-c", "startx"])
    exit(0)

# Appliquer les patchs en chaîne
while local_version in updates and updates[local_version]["next"]:
    next_version = updates[local_version]["next"]
    patch_url = updates[local_version]["url"]

    print(f"[UPDATER] Patch {local_version} → {next_version}")
    print(f"[UPDATER] Téléchargement depuis : {patch_url}")

    try:
        with requests.get(patch_url, stream=True) as r:
            r.raise_for_status()
            with open(PATCH_TMP, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception as e:
        print(f"[UPDATER] ❌ Erreur téléchargement : {e}")
        break

    print("[UPDATER] 📦 Décompression...")
    try:
        with zipfile.ZipFile(PATCH_TMP, 'r') as zip_ref:
            zip_ref.extractall(GAME_DIR)
    except Exception as e:
        print(f"[UPDATER] ❌ Erreur décompression : {e}")
        break

    os.remove(PATCH_TMP)

    # Mise à jour du fichier version
    with open(VERSION_FILE, "w") as f:
        f.write(next_version)

    print(f"[UPDATER] ✅ Patch appliqué : {next_version}")
    local_version = next_version

print("[UPDATER] ✅ Mise à jour terminée.")
print("[UPDATER] Lancement du jeu dans 5 secondes...")
time.sleep(5)
subprocess.Popen(["bash", "-c", "startx"])