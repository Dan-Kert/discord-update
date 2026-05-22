"""
This is the source code of discord-update, a graphical utility 
for managing and updating Discord on Linux systems.

Licensed under the DanKert Non-Commercial License.
You should have received a copy of the license in this archive (see LICENSE).

Author: DanKert, 2026.
"""
import os
import sys
import subprocess
import urllib.request
import tarfile
import traceback
try:
    from PyQt6.QtCore import QThread, pyqtSignal
except ImportError:
    class _DummySignal:
        def emit(self, *args, **kwargs):
            return None

    def pyqtSignal(*args, **kwargs):  # type: ignore
        return _DummySignal()

    class QThread:  # type: ignore
        def __init__(self, *args, **kwargs):
            super().__init__()

        def start(self):
            return self.run()
from discord_update.text import t
from discord_update.utils import get_remote_version

def run_update_sync(mode="deb", action="update", status_cb=None, progress_cb=None):

    def _status(msg: str):
        if callable(status_cb):
            try:
                status_cb(msg)
            except Exception:
                pass

    def _progress(val: int):
        if callable(progress_cb):
            try:
                progress_cb(int(val))
            except Exception:
                pass

    worker = DiscordUpdaterWorker(mode=mode, action=action)

    return worker._run_sync(_status, _progress)

class DiscordUpdaterWorker(QThread):
    progress_changed = pyqtSignal(int)
    status_changed = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, mode="deb", action="update"):
        super().__init__()
        self.mode = mode
        self.action = action
        self.deb_url = "https://discord.com/api/download?platform=linux&format=deb"
        self.tar_url = "https://discord.com/api/download?platform=linux&format=tar.gz"
        self.download_path_deb = os.path.expanduser("~/discord_update_temp.deb")
        self.download_path_tar = os.path.expanduser("~/discord_update_temp.tar.gz")
        self.tar_install_dir = os.path.expanduser("~/.local/share")
        self.tar_discord_bin = os.path.expanduser("~/.local/share/Discord/discord")

    def _run_sync(self, status_cb, progress_cb):
        try:
            if self.action == "check_only":
                check_mode = "deb" if self.mode == "tar.gz" else self.mode
                remote_ver = get_remote_version(check_mode)
                if remote_ver:
                    return True, str(remote_ver).strip()
                return False, t("error_check_version")

            if self.mode == "deb":
                status_cb(t("status_download_deb"))
                self.download_file(self.deb_url, self.download_path_deb, progress_cb=progress_cb)

                status_cb(t("status_install_deb"))
                progress_cb(96)

                cmd = ["pkexec", "env", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install", "-y", self.download_path_deb]
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,
                    text=True,
                )

                if process.returncode == 0:
                    progress_cb(100)
                    msg = t("status_success_installed") if self.action == "install" else t("status_success_updated")
                    return True, msg
                error_msg = process.stderr.strip() or t("error_default_apt")
                return False, t("error_apt", error=error_msg)

            if self.mode == "tar.gz":
                status_cb(t("status_download_tar"))
                self.download_file(self.tar_url, self.download_path_tar, progress_cb=progress_cb)

                status_cb(t("status_prepare_tar"))
                progress_cb(90)

                os.makedirs(self.tar_install_dir, exist_ok=True)

                target_discord_folder = os.path.join(self.tar_install_dir, "Discord")
                if os.path.exists(target_discord_folder):
                    import shutil
                    try:
                        shutil.rmtree(target_discord_folder)
                        print("[Updater] Previous Discord directory successfully removed before clean extraction.")
                    except Exception as e:
                        print(f"[Updater] Warning: failed to remove previous Discord directory: {e}")

                with tarfile.open(self.download_path_tar, "r:gz") as tar:
                    try:
                        tar.extractall(path=self.tar_install_dir, filter='fully_trusted')
                    except TypeError:
                        tar.extractall(path=self.tar_install_dir)

                status_cb(t("status_create_shortcut"))
                progress_cb(95)
                self.create_tar_desktop_shortcut()

                progress_cb(100)
                msg = t("status_success_installed_tar") if self.action == "install" else t("status_success_updated_tar")
                return True, msg

            if self.mode == "snap":
                progress_cb(20)

                if self.action == "install":
                    status_cb(t("status_snap_install"))
                    cmd = ["pkexec", "snap", "install", "discord"]
                else:
                    status_cb(t("status_snap_update"))
                    cmd = ["pkexec", "snap", "refresh", "discord"]

                progress_cb(50)
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if process.returncode == 0:
                    progress_cb(100)
                    output = process.stdout.lower() + process.stderr.lower()
                    if "has no updates available" in output or "already up-to-date" in output:
                        return True, t("status_already_latest")
                    msg = t("status_success_installed") if self.action == "install" else t("status_success_updated")
                    return True, msg

                error_msg = process.stderr.strip() or t("error_apt", error="renouncement root.")
                return False, t("error_snap", error=error_msg)

            if self.mode == "flatpak":
                progress_cb(20)

                if self.action == "install":
                    status_cb(t("status_flatpak_install"))
                    cmd = ["flatpak", "install", "-y", "flathub", "com.discordapp.Discord"]
                else:
                    status_cb(t("status_flatpak_update"))
                    cmd = ["flatpak", "update", "-y", "com.discordapp.Discord"]

                progress_cb(60)
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if process.returncode == 0:
                    progress_cb(100)
                    msg = t("status_success_installed") if self.action == "install" else t("status_success_updated")
                    return True, msg

                error_msg = process.stderr.strip() or t("error_default_flatpak")
                return False, t("error_flatpak", error=error_msg)

            return False, t("unexpected_failure", error=f"Unknown mode: {self.mode}")

        except Exception as e:
            print("\n🚨 [CRITICAL ERROR]:")
            traceback.print_exc()
            return False, t("unexpected_failure", error=str(e))
        finally:
            for path in [self.download_path_deb, self.download_path_tar]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"[Updater] Temporary file {os.path.basename(path)} successfully deleted.")
                    except Exception as clean_error:
                        print(f"[Updater] Failed to delete temporary file: {clean_error}")

    def run(self):
        try:
            # === Check Only Version ===
            if self.action == "check_only":
                check_mode = "deb" if self.mode == "tar.gz" else self.mode
                remote_ver = get_remote_version(check_mode)
                if remote_ver:
                    self.finished.emit(True, str(remote_ver).strip())
                else:
                    self.finished.emit(False, t("error_check_version"))
                return

            # === DEB (APT) ===
            if self.mode == "deb":
                self.status_changed.emit(t("status_download_deb"))
                self.download_file(self.deb_url, self.download_path_deb)

                self.status_changed.emit(t("status_install_deb"))
                self.progress_changed.emit(96)

                cmd = ["pkexec", "env", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install", "-y", self.download_path_deb]
                process = subprocess.run(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    stdin=subprocess.DEVNULL, 
                    text=True
                )

                if process.returncode == 0:
                    self.progress_changed.emit(100)
                    msg = t("status_success_installed") if self.action == "install" else t("status_success_updated")
                    self.finished.emit(True, msg)
                else:
                    error_msg = process.stderr.strip() or t("error_default_apt")
                    self.finished.emit(False, t("error_apt", error=error_msg))

            # === TAR.GZ ===
            elif self.mode == "tar.gz":
                self.status_changed.emit(t("status_download_tar"))
                self.download_file(self.tar_url, self.download_path_tar)
                
                self.status_changed.emit(t("status_prepare_tar"))
                self.progress_changed.emit(90)
                
                os.makedirs(self.tar_install_dir, exist_ok=True)
                
                target_discord_folder = os.path.join(self.tar_install_dir, "Discord")
                if os.path.exists(target_discord_folder):
                    import shutil
                    try:
                        shutil.rmtree(target_discord_folder)
                        print("[Updater] Previous Discord directory successfully removed before clean extraction.")
                    except Exception as e:
                        print(f"[Updater] Warning: failed to remove previous Discord directory: {e}")
                
                with tarfile.open(self.download_path_tar, "r:gz") as tar:
                    try:
                        tar.extractall(path=self.tar_install_dir, filter='fully_trusted')
                    except TypeError:
                        tar.extractall(path=self.tar_install_dir)
                
                self.status_changed.emit(t("status_create_shortcut"))
                self.progress_changed.emit(95)
                self.create_tar_desktop_shortcut()
                
                self.progress_changed.emit(100)
                msg = t("status_success_installed_tar") if self.action == "install" else t("status_success_updated_tar")
                self.finished.emit(True, msg)

            # === SNAP ===
            elif self.mode == "snap":
                self.progress_changed.emit(20)
                
                if self.action == "install":
                    self.status_changed.emit(t("status_snap_install"))
                    cmd = ["pkexec", "snap", "install", "discord"]
                else:
                    self.status_changed.emit(t("status_snap_update"))
                    cmd = ["pkexec", "snap", "refresh", "discord"]
                
                self.progress_changed.emit(50)
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if process.returncode == 0:
                    self.progress_changed.emit(100)
                    output = process.stdout.lower() + process.stderr.lower()
                    if "has no updates available" in output or "already up-to-date" in output:
                        self.finished.emit(True, t("status_already_latest"))
                    else:
                        msg = t("status_success_installed") if self.action == "install" else t("status_success_updated")
                        self.finished.emit(True, msg)
                else:
                    error_msg = process.stderr.strip() or t("error_apt", error="Отказ в авторизации root.")
                    self.finished.emit(False, t("error_snap", error=error_msg))

            # === FLATPAK ===
            elif self.mode == "flatpak":
                self.progress_changed.emit(20)
                
                if self.action == "install":
                    self.status_changed.emit(t("status_flatpak_install"))
                    cmd = ["flatpak", "install", "-y", "flathub", "com.discordapp.Discord"]
                else:
                    self.status_changed.emit(t("status_flatpak_update"))
                    cmd = ["flatpak", "update", "-y", "com.discordapp.Discord"]
                
                self.progress_changed.emit(60)
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if process.returncode == 0:
                    self.progress_changed.emit(100)
                    msg = t("status_success_installed") if self.action == "install" else t("status_success_updated")
                    self.finished.emit(True, msg)
                else:
                    error_msg = process.stderr.strip() or t("error_default_flatpak")
                    self.finished.emit(False, t("error_flatpak", error=error_msg))

        except Exception as e:
            print("\n🚨 [CRITICAL INSTALLATION THREAD ERROR]:")
            traceback.print_exc()
            self.finished.emit(False, t("unexpected_failure", error=str(e)))
            
        finally:
            # === Clear ===
            for path in [self.download_path_deb, self.download_path_tar]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"[Updater] Temporary file {os.path.basename(path)} successfully deleted.")
                    except Exception as clean_error:
                        print(f"[Updater] Failed to delete temporary file: {clean_error}")

    def download_file(self, url, dest_path, progress_cb=None):
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
        )
        with urllib.request.urlopen(req) as response:
            total_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0
            block_size = 1024 * 64

            with open(dest_path, 'wb') as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    bytes_downloaded += len(buffer)
                    f.write(buffer)
                    
                    if total_size > 0:
                        percent = int((bytes_downloaded / total_size) * 100)
                        gui_percent = int(percent * 0.85)
                        self.progress_changed.emit(gui_percent)
                        if callable(progress_cb):
                            progress_cb(gui_percent)

    def create_tar_desktop_shortcut(self):
        """create .desktop file for tar.gz installation in ~/.local/share/applications"""
        desktop_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(desktop_dir, exist_ok=True)
        desktop_file_path = os.path.join(desktop_dir, "discord-tar.desktop")
        
        icon_path = os.path.join(self.tar_install_dir, "Discord", "discord.png")
        
        content = f"""[Desktop Entry]
        Name=Discord
        StartupWMClass=discord
        Comment=All-in-one voice and text chat for gamers
        GenericName=Internet Messenger
        Exec={self.tar_discord_bin}
        Icon={icon_path}
        Type=Application
        Categories=Network;InstantMessaging;
        Path={os.path.expanduser('~')}
        """
        with open(desktop_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        try:
            os.chmod(desktop_file_path, 0o755)
        except Exception:
            pass
