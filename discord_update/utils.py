"""
This is the source code of discord-update, a graphical utility 
for managing and updating Discord on Linux systems.

Licensed under the DanKert Non-Commercial License.
You should have received a copy of the license in this archive (see LICENSE).

Author: DanKert, 2026.
"""
import shutil
import os
import subprocess
import json
import urllib.request

def detect_discord_installation():
    tar_base_dir = os.path.expanduser("~/.local/share/Discord")
    tar_bin_path = os.path.join(tar_base_dir, "discord")
    
    if os.path.exists(tar_bin_path):
        build_info_path = os.path.join(tar_base_dir, "resources", "build_info.json")
        if os.path.exists(build_info_path):
            try:
                with open(build_info_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "version" in data:
                        return "tar.gz", str(data["version"]).strip()
            except:
                pass
        return "tar.gz", "1.0.139"

    if shutil.which("dpkg-query"):
        try:
            res = subprocess.run(
                ["dpkg-query", "-W", "-f=${Version}", "discord"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
            )
            if res.returncode == 0 and res.stdout.strip():
                return "deb", res.stdout.strip().split("-")[0]
        except:
            pass

    if shutil.which("snap"):
        try:
            res = subprocess.run(
                ["snap", "list", "discord"], 
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
            )
            if res.returncode == 0:
                lines = res.stdout.splitlines()
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 2:
                        return "snap", parts[1]
        except:
            pass
            
        if os.path.exists("/snap/discord/current"):
            return "snap", "Installed"

    if shutil.which("flatpak"):
        try:
            res = subprocess.run(
                ["flatpak", "list", "--columns=application,version"], 
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
            )
            for line in res.stdout.splitlines():
                if "com.discordapp.Discord" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        return "flatpak", parts[1]
                    return "flatpak", "Installed"
        except:
            pass

    if shutil.which("discord"):
        real_path = os.path.realpath(shutil.which("discord"))
        if "snap" not in real_path and "flatpak" not in real_path:
            build_info_path = "/usr/share/discord/resources/build_info.json"
            if os.path.exists(build_info_path):
                try:
                    with open(build_info_path, "r") as f:
                        data = json.load(f)
                        if "version" in data:
                            return "deb", data["version"]
                except:
                    pass
        return "deb", "Installed"
    return "not_found", "Not Found"

class NoRedirectionHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return fp

def get_remote_version(mode):
    base_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        if mode == "tar.gz":
            url = "https://discord.com/api/updates/stable?platform=linux"
            req = urllib.request.Request(url, headers=base_headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data and "name" in data:
                    return str(data["name"]).strip()
            return None

        elif mode == "deb":
            opener = urllib.request.build_opener(NoRedirectionHandler)
            url = "https://discord.com/api/download?platform=linux&format=deb"
            req = urllib.request.Request(url, headers=base_headers)
            
            with opener.open(req, timeout=5) as response:
                redirect_url = response.headers.get('Location', '')
                if redirect_url:
                    filename = redirect_url.split('/')[-1]
                    version = filename.replace('discord-', '').replace('.deb', '')
                    if version:
                        return version
                return None

        elif mode == "snap":
            if shutil.which("snap"):
                env = os.environ.copy()
                env["LC_ALL"] = "C"
                res = subprocess.run(
                    ["snap", "info", "discord", "--unicode=never"],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env, timeout=5
                )
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        if "latest/stable:" in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                return parts[1]
                        if "tracking:" in line and "stable" in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                return parts[1]
                        if "installed:" in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                return parts[1]
            return None

        elif mode == "flatpak":
            url = "https://flathub.org/api/v2/appstream/com.discordapp.Discord"
            req = urllib.request.Request(url, headers=base_headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if "version" in data and data["version"]:
                    return str(data["version"])
                
                releases = data.get("releases", [])
                if releases and isinstance(releases, list) and "version" in releases[0]:
                    return str(releases[0]["version"])
                return None
                
    except Exception as e:
        print(f"[API Error] Failed to get remote version for {mode}: {e}")
        return None