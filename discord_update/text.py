"""
This is the source code of discord-update, a graphical utility 
for managing and updating Discord on Linux systems.

Licensed under the DanKert Non-Commercial License.
You should have received a copy of the license in this archive (see LICENSE).

Author: DanKert, 2026.
"""
from __future__ import annotations

import os
import json
import locale
from typing import Dict

LANGUAGE_NAMES: Dict[str, str] = {
    "ru": "Русский",
    "en": "English",
    "ro": "Română",
}

TEXTS: Dict[str, Dict[str, str]] = {
    "ru": {
        "app_title": "Discord Update",
        "method_detecting_installation": "Анализ среды установки...",
        "select_source_label": "Выбрать источник:",
        "system_check_status": "Проверка состояния системы...",
        "check_updates": "Проверить обновления",
        "install_discord": "Установить Discord",
        "updating": "Обновление...",
        "installing": "Установка...",
        "update_discord": "Обновить Discord",
        "updates_not_required": "Обновления не требуются",
        "available_update": "Доступно обновление! Серверная версия: {remote_version} (Ваша: {local_version}).",
        "latest_version_installed": "✨ У вас установлена самая последняя версия Discord ({version}). Обновление не требуется!",
        "github": "GitHub",
        "language_button": "Язык",
        "language_selected": "{language}",
        "installation_not_found": "Discord не обнаружен. Выберите доступный источник для чистой установки.",
        "mode_detected": "Найден: {mode_name} ({version})",
        "checking_remote_version": "Сверяем локальную версию с серверами релизов...",
        "error_check_version": "Не удалось проверить серверную версию. Вы можете запустить принудительное обновление.",
        "retry": "Повторить попытку",
        "status_download_deb": "Загрузка свежего пакета Discord (DEB)...",
        "status_install_deb": "Установка пакета (требуются права root)...",
        "status_download_tar": "Загрузка универсального архива Discord (tar.gz)...",
        "status_prepare_tar": "Подготовка директории и распаковка архива...",
        "status_create_shortcut": "Создание ярлыка запуска (.desktop)...",
        "status_snap_install": "Установка Discord из Snap Store (введите пароль)...",
        "status_snap_update": "Обновление Discord через Snap (введите пароль)...",
        "status_flatpak_install": "Установка Discord из Flathub...",
        "status_flatpak_update": "Проверка обновлений во Flatpak...",
        "status_already_latest": "Discord уже обновлен до последней версии!",
        "status_success_installed": "Discord успешно установлен!",
        "status_success_updated": "Discord успешно обновлен!",
        "status_success_installed_tar": "Discord (tar.gz) успешно добавлен в домашнюю папку!",
        "status_success_updated_tar": "Discord (tar.gz) успешно обновлен!",
        "error_apt": "Ошибка при работе с APT: {error}",
        "error_snap": "Ошибка Snap: {error}",
        "error_flatpak": "Ошибка Flatpak: {error}",
        "error_default_apt": "Ошибка авторизации или отмена установки.",
        "error_default_flatpak": "Ошибка выполнения команды flatpak.",
        "error_auth_root": "Отказ в авторизации root.",
        "unexpected_failure": "Произошел непредвиденный сбой: {error}",
        "installer_option_tar_gz": "Универсальный архив (tar.gz)",
        "installer_option_deb": "DEB Пакет (APT)",
        "installer_option_snap": "Snap Store",
        "installer_option_flatpak": "Flatpak (Flathub)",
        "mode_name_deb": "DEB",
        "mode_name_tar.gz": "Tar.GZ",
        "mode_name_snap": "Snap",
        "mode_name_flatpak": "Flatpak",
        "cli_actions": "Действия:",
        "cli_action_exit": "Выход",
        "cli_action_change_language": "Сменить язык",
        "cli_choose_language": "Выберите язык:",
        "cli_choose_install_source": "Выберите источник установки:",
        "cli_cancel": "Отмена",
        "cli_invalid_choice": "Неверный выбор, попробуйте ещё раз.",
    },
    "en": {
        "app_title": "Discord Update",
        "method_detecting_installation": "Analyzing installation environment...",
        "select_source_label": "Select source:",
        "system_check_status": "Checking system status...",
        "check_updates": "Check for updates",
        "install_discord": "Install Discord",
        "updating": "Updating...",
        "installing": "Installing...",
        "update_discord": "Update Discord",
        "updates_not_required": "No updates are required",
        "available_update": "Update available! Server version: {remote_version} (Yours: {local_version}).",
        "latest_version_installed": "✨ You already have the latest Discord version ({version}). No update needed!",
        "github": "GitHub",
        "language_button": "Language",
        "language_selected": "{language}",
        "installation_not_found": "Discord was not found. Choose an available source to install it.",
        "mode_detected": "Detected: {mode_name} ({version})",
        "checking_remote_version": "Comparing local version with release servers...",
        "error_check_version": "Failed to check the remote version. You can run an update manually.",
        "retry": "Retry",
        "status_download_deb": "Downloading Discord package (DEB)...",
        "status_install_deb": "Installing package (root privileges required)...",
        "status_download_tar": "Downloading Discord archive (tar.gz)...",
        "status_prepare_tar": "Preparing directory and extracting archive...",
        "status_create_shortcut": "Creating launch shortcut (.desktop)...",
        "status_snap_install": "Installing Discord from Snap Store (enter password)...",
        "status_snap_update": "Updating Discord via Snap (enter password)...",
        "status_flatpak_install": "Installing Discord from Flathub...",
        "status_flatpak_update": "Checking Flatpak updates...",
        "status_already_latest": "Discord is already up to date!",
        "status_success_installed": "Discord was installed successfully!",
        "status_success_updated": "Discord was updated successfully!",
        "status_success_installed_tar": "Discord (tar.gz) was added to your home folder successfully!",
        "status_success_updated_tar": "Discord (tar.gz) was updated successfully!",
        "error_apt": "APT error: {error}",
        "error_snap": "Snap error: {error}",
        "error_flatpak": "Flatpak error: {error}",
        "error_default_apt": "Authorization denied or install canceled.",
        "error_default_flatpak": "Flatpak command failed.",
        "error_auth_root": "Authorization denied by root.",
        "unexpected_failure": "An unexpected failure occurred: {error}",
        "installer_option_tar_gz": "Universal archive (tar.gz)",
        "installer_option_deb": "DEB Package (APT)",
        "installer_option_snap": "Snap Store",
        "installer_option_flatpak": "Flatpak (Flathub)",
        "mode_name_deb": "DEB",
        "mode_name_tar.gz": "Tar.GZ",
        "mode_name_snap": "Snap",
        "mode_name_flatpak": "Flatpak",
        "cli_actions": "Actions:",
        "cli_action_exit": "Exit",
        "cli_action_change_language": "Change language",
        "cli_choose_language": "Choose language:",
        "cli_choose_install_source": "Choose install source:",
        "cli_cancel": "Cancel",
        "cli_invalid_choice": "Invalid choice, please try again.",
    },
    "ro": {
        "app_title": "Discord Update",
        "method_detecting_installation": "Analizez mediul de instalare...",
        "select_source_label": "Selectare sursă:",
        "system_check_status": "Verific starea sistemului...",
        "check_updates": "Verifică actualizări",
        "install_discord": "Instalează Discord",
        "updating": "Se actualizează...",
        "installing": "Se instalează...",
        "update_discord": "Actualizează Discord",
        "updates_not_required": "Nu sunt necesare actualizări",
        "available_update": "Actualizare disponibilă! Versiunea serverului: {remote_version} (A ta: {local_version}).",
        "latest_version_installed": "✨ Ai deja cea mai nouă versiune Discord ({version}). Nu este necesară actualizare!",
        "github": "GitHub",
        "language_button": "Limbă",
        "language_selected": "{language}",
        "installation_not_found": "Discord nu a fost găsit. Alege o sursă disponibilă pentru a-l instala.",
        "mode_detected": "Detectat: {mode_name} ({version})",
        "checking_remote_version": "Compar versiunea locală cu serverele de lansare...",
        "error_check_version": "Nu am putut verifica versiunea de la distanță. Poți rula o actualizare manual.",
        "retry": "Încearcă din nou",
        "status_download_deb": "Se descarcă pachetul Discord (DEB)...",
        "status_install_deb": "Se instalează pachetul (privilegii root necesare)...",
        "status_download_tar": "Se descarcă arhiva Discord (tar.gz)...",
        "status_prepare_tar": "Se pregătește directorul și se extrage arhiva...",
        "status_create_shortcut": "Se creează scurtătura de lansare (.desktop)...",
        "status_snap_install": "Se instalează Discord din Snap Store (introdu parola)...",
        "status_snap_update": "Se actualizează Discord via Snap (introdu parola)...",
        "status_flatpak_install": "Se instalează Discord din Flathub...",
        "status_flatpak_update": "Se verifică actualizările Flatpak...",
        "status_already_latest": "Discord este deja actualizat!",
        "status_success_installed": "Discord a fost instalat cu succes!",
        "status_success_updated": "Discord a fost actualizat cu succes!",
        "status_success_installed_tar": "Discord (tar.gz) a fost adăugat cu succes în dosarul tău!",
        "status_success_updated_tar": "Discord (tar.gz) a fost actualizat cu succes!",
        "error_apt": "Eroare APT: {error}",
        "error_snap": "Eroare Snap: {error}",
        "error_flatpak": "Eroare Flatpak: {error}",
        "error_default_apt": "Autorizație refuzată sau instalare anulată.",
        "error_default_flatpak": "Comanda Flatpak a eșuat.",
        "error_auth_root": "Autorizație refuzată de root.",
        "unexpected_failure": "A apărut o eroare neașteptată: {error}",
        "installer_option_tar_gz": "Arhivă universală (tar.gz)",
        "installer_option_deb": "Pachet DEB (APT)",
        "installer_option_snap": "Snap Store",
        "installer_option_flatpak": "Flatpak (Flathub)",
        "mode_name_deb": "DEB",
        "mode_name_tar.gz": "Tar.GZ",
        "mode_name_snap": "Snap",
        "mode_name_flatpak": "Flatpak",
        "cli_actions": "Acțiuni:",
        "cli_action_exit": "Ieșire",
        "cli_action_change_language": "Schimbă limba",
        "cli_choose_language": "Alege limba:",
        "cli_choose_install_source": "Alege sursa de instalare:",
        "cli_cancel": "Anulează",
        "cli_invalid_choice": "Alegere invalidă, încearcă din nou.",
    },
}

_current_language = "ru"

def _get_config_path() -> str:
    config_dir = os.path.expanduser("~/.config/discord-update")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "language.json")

def _get_system_language() -> str:
    lang_code = locale.getdefaultlocale()[0]
    if not lang_code:
        return "en"
    
    primary_lang = lang_code.split('_')[0].lower()

    if primary_lang in TEXTS:
        return primary_lang
    return "en"

def save_language(language: str) -> None:
    config_path = _get_config_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({'language': language}, f)
    except Exception:
        pass

def load_language() -> str:
    config_path = _get_config_path()

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                lang = data.get('language')
                if lang in TEXTS:
                    return lang
        except Exception:
            pass
    return _get_system_language()

def set_language(language: str) -> None:
    global _current_language
    if language in TEXTS:
        _current_language = language

def get_language() -> str:
    return _current_language

def t(key: str, **kwargs) -> str:
    language_texts = TEXTS.get(_current_language, {})
    template = language_texts.get(key, key)
    try:
        return template.format(**kwargs)
    except Exception:
        return template

def get_mode_label(mode: str) -> str:
    return TEXTS[_current_language].get(f"mode_name_{mode}", mode)

def get_installer_label(option: str) -> str:
    return TEXTS[_current_language].get(f"installer_option_{option}", option)

def get_language_name(language: str) -> str:
    return LANGUAGE_NAMES.get(language, language)

def available_languages() -> Dict[str, str]:
    return LANGUAGE_NAMES.copy()