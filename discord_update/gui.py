"""
This is the source code of discord-update, a graphical utility 
for managing and updating Discord on Linux systems.

Licensed under the DanKert Non-Commercial License.
You should have received a copy of the license in this archive (see LICENSE).

Author: DanKert, 2026.
"""
import sys
import os
import shutil
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QComboBox, QMenu
from PyQt6.QtCore import Qt, QUrl, QTimer, QProcess
from PyQt6.QtGui import QPixmap, QDesktopServices, QIcon
from discord_update.updater import DiscordUpdaterWorker
from discord_update.text import (
    set_language,
    t,
    get_installer_label,
    get_mode_label,
    get_language_name,
    available_languages,
    load_language,
    save_language,
)
from discord_update.utils import detect_discord_installation

class DiscordUpdateGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.repo_url = "https://github.com/Dan-Kert/discord-update"
        self.github_icon_path = os.path.join("icon", "github.png")
        self.logo_path = os.path.join("icon", "logo.png")
        self.updater_thread = None
        self.current_mode = "deb"
        self.current_action = "update"
        self.local_version = None
        self.current_language = load_language()
        set_language(self.current_language)
        self.init_ui()
        self.check_system_status()

    def load_stylesheet(self):
        """use style.qss"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        qss_path = os.path.join(current_dir, "style.qss")
        
        if not os.path.exists(qss_path):
            qss_path = "style.qss"

        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"[Warning] Style sheet file not found at {qss_path}. Default Qt styles will be used.")

    def init_ui(self):
        # based(title, size, icon, fixed size, custom flags)
        self.setFixedSize(400, 520)
        self.setWindowTitle(t('app_title'))

        if os.path.exists(self.logo_path):
            self.setWindowIcon(QIcon(self.logo_path))

        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)

        self.load_stylesheet()

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 15)
        layout.setSpacing(15)                      

        # logo
        self.logo_label = QLabel(self)
        self.logo_label.setObjectName("LogoLabel")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if os.path.exists(self.logo_path):
            logo_pixmap = QPixmap(self.logo_path)
            if not logo_pixmap.isNull():
                self.logo_label.setPixmap(logo_pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(self.logo_label)

        # (deb/snap/flatpak/tar.gz version)
        self.method_label = QLabel(t('method_detecting_installation'), self)
        self.method_label.setObjectName("MethodLabel")
        self.method_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.method_label)

        # platform selector
        self.installer_box = QWidget(self)
        box_layout = QHBoxLayout(self.installer_box)
        box_layout.setContentsMargins(0, 0, 0, 0)
        self.installer_label = QLabel(t("select_source_label"), self)
        self.mode_selector = QComboBox(self)
        box_layout.addWidget(self.installer_label)
        box_layout.addWidget(self.mode_selector)
        layout.addWidget(self.installer_box)
        self.installer_box.hide()

        layout.addStretch()

        # Status
        self.status_label = QLabel(t('system_check_status'), self)
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Action button
        self.action_button = QPushButton(t("check_updates"), self)
        self.action_button.clicked.connect(self.on_action_clicked)
        layout.addWidget(self.action_button)

        #.progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        self.progress_bar.hide()

        self.progress_target = 0
        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(16)
        self.progress_timer.timeout.connect(self._animate_progress)

        # GitHub button and language selector
        bottom_layout = QHBoxLayout()
        
        self.github_label = QLabel(self)
        self.github_label.setObjectName("GithubIcon")
        self.github_label.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if os.path.exists(self.github_icon_path):
            github_pixmap = QPixmap(self.github_icon_path)
            if not github_pixmap.isNull():
                self.github_label.setPixmap(github_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.github_label.setText(t('github'))
            self.github_label.setStyleSheet("color: #949BA4; font-size: 12px;")
        
        self.github_label.mousePressEvent = self.open_github_repo
        bottom_layout.addWidget(self.github_label)
        bottom_layout.addStretch()

        self.language_button = QPushButton(self)
        self.language_button.setObjectName("LanguageButton")
        self.language_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.language_button.setMinimumWidth(70)
        self.language_button.setMaximumWidth(90)
        self.language_button.setMinimumHeight(24)
        self.language_menu = QMenu(self)
        self.language_menu.triggered.connect(self.on_language_selected)
        self._populate_language_menu()
        self.language_button.setMenu(self.language_menu)
        self._update_language_button_text()
        bottom_layout.addWidget(self.language_button)
        
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def check_system_status(self):
        mode, status = detect_discord_installation()
        
        self.current_mode = mode
        self.local_version = status

        if mode == "not_found":
            self.current_action = "install"
            self.set_method_text("installation_not_found")
            self.set_status_text("installation_not_found")
            self.action_button.setText(t("install_discord"))
            self.action_button.setEnabled(True)
            
            self._populate_installer_options()
            self.installer_box.show()
        else:
            self.current_action = "update"
            self.method_label.setText(t("mode_detected", mode_name=get_mode_label(mode), version=status))
            self.installer_box.hide()
            
            self.action_button.setEnabled(False)
            self.action_button.setText(t("checking_remote_version"))
            self.set_status_text("checking_remote_version")
            
            self.updater_thread = DiscordUpdaterWorker(self.current_mode, "check_only")
            self.updater_thread.finished.connect(self.on_version_check_finished)
            self.updater_thread.start()

    def on_version_check_finished(self, success, remote_version):
        if not success or not remote_version:
            self.set_status_text("error_check_version")
            self.action_button.setText(t("update_discord"))
            self.action_button.setEnabled(True)
            return

        if self.local_version == remote_version:
            self.set_status_text("latest_version_installed", version=remote_version)
            self.action_button.setText(t("updates_not_required"))
            self.action_button.setEnabled(False)
        else:
            self.set_status_text("available_update", remote_version=remote_version, local_version=self.local_version)
            self.action_button.setText(t("update_discord"))
            self.action_button.setEnabled(True)

    def open_github_repo(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            QDesktopServices.openUrl(QUrl(self.repo_url))

    def _update_language_button_text(self):
        self.language_button.setText(self.current_language.upper())

    def set_status_text(self, key: str, **kwargs):
        try:
            self._last_status_key = key
            self._last_status_args = kwargs
        except Exception:
            self._last_status_key = None
            self._last_status_args = {}
        self.status_label.setText(t(key, **kwargs))

    def set_method_text(self, key: str, **kwargs):
        try:
            self._last_method_key = key
            self._last_method_args = kwargs
        except Exception:
            self._last_method_key = None
            self._last_method_args = {}
        self.method_label.setText(t(key, **kwargs))

    def _rerender_dynamic_texts(self):
        if getattr(self, '_last_method_key', None):
            try:
                self.method_label.setText(t(self._last_method_key, **(self._last_method_args or {})))
            except Exception:
                pass
        if getattr(self, '_last_status_key', None):
            try:
                self.status_label.setText(t(self._last_status_key, **(self._last_status_args or {})))
            except Exception:
                pass

    def _populate_language_menu(self):
        self.language_menu.clear()
        for lang_code, lang_name in available_languages().items():
            if lang_code != self.current_language:
                action = self.language_menu.addAction(lang_name)
                action.setData(lang_code)
        

    def on_language_selected(self, action):
        if not action:
            return
        if getattr(self, '_language_switching', False):
            return
        selected_language = action.data()
        if selected_language == self.current_language:
            return
        self._language_switching = True
        self.language_button.setEnabled(False)
        self.current_language = selected_language
        set_language(selected_language)
        save_language(selected_language)
        self._restart_application()

    def _restart_application(self):
        started = False
        try:
            started = QProcess.startDetached(sys.executable, sys.argv)
        finally:
            app = QApplication.instance()
            if app is not None:
                app.quit()
                QTimer.singleShot(150, lambda: os._exit(0))

    def _refresh_ui_texts_safe(self):
        self.setWindowTitle(t("app_title"))
        self.installer_label.setText(t("select_source_label"))
        self.action_button.setText(t("check_updates"))
        self._update_language_button_text()
        self._refresh_installer_options()

    def _refresh_ui_texts(self):
        self._refresh_ui_texts_safe()

    def _refresh_installer_options(self):
        if self.current_action != "install":
            return
        current_value = self.mode_selector.currentData()
        self.mode_selector.clear()
        self._populate_installer_options()
        if current_value is not None:
            index = self.mode_selector.findData(current_value)
            if index != -1:
                self.mode_selector.setCurrentIndex(index)

    def _populate_installer_options(self):
        self.mode_selector.clear()
        self.mode_selector.addItem(get_installer_label("tar.gz"), "tar.gz")
        if shutil.which("dpkg-query") or shutil.which("apt-get"):
            self.mode_selector.addItem(get_installer_label("deb"), "deb")
        if shutil.which("snap"):
            self.mode_selector.addItem(get_installer_label("snap"), "snap")
        if shutil.which("flatpak"):
            self.mode_selector.addItem(get_installer_label("flatpak"), "flatpak")

    def _animate_progress(self):
        current_value = self.progress_bar.value()
        if current_value < self.progress_target:
            step = min(4, self.progress_target - current_value)
            self.progress_bar.setValue(current_value + step)
        elif current_value > self.progress_target:
            self.progress_bar.setValue(self.progress_target)
        else:
            self.progress_timer.stop()

    def on_worker_progress(self, value):
        self.progress_target = max(0, min(100, int(value)))
        if not self.progress_timer.isActive():
            self.progress_timer.start()

    def on_action_clicked(self):
        self.action_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        if self.current_action == "install":
            self.current_mode = self.mode_selector.currentData()
            self.action_button.setText(t("installing"))
        else:
            self.action_button.setText(t("updating"))

        self.updater_thread = DiscordUpdaterWorker(self.current_mode, self.current_action)
        self.updater_thread.status_changed.connect(self.status_label.setText)
        self.updater_thread.progress_changed.connect(self.on_worker_progress)
        self.updater_thread.finished.connect(self.on_updater_finished)
        self.updater_thread.start()

    def on_updater_finished(self, success, message):
        self.progress_bar.hide()
        
        if success:
            self.status_label.setText(f"✨ {message}")
            self.check_system_status()
        else:
            self.status_label.setText(message)
            self.action_button.setText(t("retry"))
            self.action_button.setEnabled(True)

def run_gui_app():
    app = QApplication(sys.argv)
    window = DiscordUpdateGUI()
    window.show()
    sys.exit(app.exec())