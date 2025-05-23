import os
import requests
import subprocess
import zipfile
import time


# === CONFIG ===
VERSION_FILE = "/opt/outlawdart/version.txt"
VERSION_JSON_URL = "https://raw.githubusercontent.com/ravinance/outlawdart-patchs/main/version.json"
PATCH_TMP = "/tmp/outlaw_patch.zip"
GAME_PATH = "/opt/outlawdart/BD BUILDVmono.x86_64"
GAME_DIR = "/opt/outlawdart/"

# === 1. Lire version locale ===
local_version = "0.0.0"
if os.path.exists(VERSION_FILE):
    with open(VERSION_FILE, "r") as f:
        local_version = f.read().strip()

print(f"[UPDATER] Version actuelle : {local_version}")

# === 2. Télécharger version.json ===
try:
    r = requests.get(VERSION_JSON_URL)
    r.raise_for_status()
    data = r.json()
    remote_version = data["version"]
    patch_url = data["url"]
except Exception as e:
    print(f"[UPDATER]  Erreur lecture version distante : {e}")
    subprocess.Popen([GAME_PATH])
    exit(0)

print(f"[UPDATER] Version disponible : {remote_version}")

# === 3. Comparer ===
if remote_version == local_version:
    print("[UPDATER]  Aucune mise à jour nécessaire.")
    subprocess.Popen([GAME_PATH])
    exit(0)

# === 4. Télécharger le patch ===
print(f"[UPDATER]  Téléchargement depuis : {patch_url}")
try:
    with requests.get(patch_url, stream=True) as r:
        r.raise_for_status()
        with open(PATCH_TMP, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
except Exception as e:
    print(f"[UPDATER]  Erreur téléchargement : {e}")
    subprocess.Popen([GAME_PATH])
    exit(0)

# === 5. Décompression ===
print("[UPDATER]  Décompression...")
try:
    with zipfile.ZipFile(PATCH_TMP, 'r') as zip_ref:
        zip_ref.extractall(GAME_DIR)
except Exception as e:
    print(f"[UPDATER]  Erreur décompression : {e}")
    subprocess.Popen([GAME_PATH])
    exit(0)

os.remove(PATCH_TMP)

# === 6. Sauvegarder nouvelle version ===
with open(VERSION_FILE, "w") as f:
    f.write(remote_version)

# === 7. Relancer l'application ===
print("[UPDATER]  Mise à jour terminée.")
print("[UPDATER]  Lancement du jeu...")


time.sleep(5)

subprocess.Popen(["bash", "-c", "startx"])
