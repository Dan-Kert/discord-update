"""
This is the source code of discord-update, a graphical utility 
for managing and updating Discord on Linux systems.

Licensed under the DanKert Non-Commercial License.
You should have received a copy of the license in this archive (see LICENSE).

Author: DanKert, 2026.
"""
import shutil
import sys
import os
from discord_update.text import (
    available_languages,
    get_language_name,
    load_language,
    save_language,
    set_language,
    t,
)
from discord_update.utils import detect_discord_installation, get_remote_version
from discord_update.updater import run_update_sync

class _Ansi:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"


def _supports_color() -> bool:
    return bool(getattr(sys.stdout, "isatty", lambda: False)()) and not bool(
        os.environ.get("NO_COLOR")
    )

def _c(text: str, color: str) -> str:
    if not _supports_color():
        return text
    return f"{color}{text}{_Ansi.RESET}"

def _print(text: str = "") -> None:
    sys.stdout.write(str(text) + "\n")
    try:
        sys.stdout.flush()
    except Exception:
        pass

def _eprint(text: str = "") -> None:
    sys.stderr.write(str(text) + "\n")
    try:
        sys.stderr.flush()
    except Exception:
        pass

def _banner() -> str:
    width = shutil.get_terminal_size((80, 20)).columns
    max_width = max(40, min(width - 2, 86))
    line = "─" * max_width
    title = "DISCORD UPDATER"
    pad = max(0, (max_width - len(title)) // 2)
    centered_title = (" " * pad) + title
    return f"{_c(line, _Ansi.GRAY)}\n{_c(centered_title, _Ansi.CYAN)}\n{_c(line, _Ansi.GRAY)}"

def _status():
    mode, local_version = detect_discord_installation()
    check_mode = "deb" if mode == "tar.gz" else mode
    remote_version = None
    if mode != "not_found":
        remote_version = get_remote_version(check_mode)
    return mode, local_version, remote_version

def _format_ok(ok: bool) -> str:
    return _c("✔", _Ansi.GREEN) if ok else _c("✖", _Ansi.RED)

def _print_summary(mode: str, local_version: str, remote_version: str | None) -> None:
    lang = load_language()
    _print(_banner())
    _print(f"{t('app_title')}  {_c(f'(lang={lang})', _Ansi.GRAY)}")

    if mode == "not_found":
        _print(f"{_format_ok(False)} {t('installation_not_found')}")
        return

    _print(f"{_format_ok(True)} {t('mode_detected', mode_name=mode, version=local_version)}")
    if remote_version:
        up_to_date = str(local_version).strip() == str(remote_version).strip()
        if up_to_date:
            _print(f"{_format_ok(True)} {t('latest_version_installed', version=remote_version)}")
        else:
            _print(f"{_format_ok(False)} {t('available_update', remote_version=remote_version, local_version=local_version)}")
    else:
        _print(f"{_c('!', _Ansi.YELLOW)} {t('error_check_version')}")

def _prompt_choice(prompt: str, choices: dict[str, str]) -> str:
    while True:
        _print(prompt)
        value = input(_c("> ", _Ansi.BLUE)).strip()
        if value in choices:
            return value
        _print(_c(t("cli_invalid_choice"), _Ansi.YELLOW))

def _language_prompt() -> str | None:
    langs = available_languages()
    if not langs:
        _eprint("No languages available.")
        return None

    preferred = ["ru", "ro", "en"]
    ordered = [c for c in preferred if c in langs] + [c for c in sorted(langs.keys()) if c not in preferred]

    mapping: dict[str, str] = {}
    _print(_banner())
    _print(_c(t("cli_choose_language"), _Ansi.BOLD))
    for i, code in enumerate(ordered, start=1):
        mapping[str(i)] = code
        _print(f"  {_c(str(i), _Ansi.CYAN)}) {langs[code]} {_c(f'({code})', _Ansi.GRAY)}")
    _print(f"  {_c('0', _Ansi.CYAN)}) {_c(t('cli_cancel'), _Ansi.GRAY)}")

    while True:
        choice = input(_c("> ", _Ansi.BLUE)).strip()
        if choice == "0":
            return None
        if choice in mapping:
            return mapping[choice]
        _print(_c(t("cli_invalid_choice"), _Ansi.YELLOW))

def set_cli_language(lang_code: str) -> int:
    langs = available_languages()
    if lang_code not in langs:
        _eprint(_c(f"Unknown language: {lang_code}", _Ansi.RED))
        _eprint("Available: " + ", ".join(sorted(langs.keys())))
        return 2
    save_language(lang_code)
    set_language(lang_code)
    _print(f"{_format_ok(True)} Language set: {lang_code} ({get_language_name(lang_code)})")
    return 0

def _do_update(mode: str, action: str) -> int:
    interactive = bool(getattr(sys.stdout, "isatty", lambda: False)())
    last_percent = {"value": -1}

    def render_progress(percent: int) -> None:
        percent = max(0, min(100, int(percent)))
        if percent == last_percent["value"]:
            return
        last_percent["value"] = percent

        bar_width = 20
        filled = int(round((percent / 100) * bar_width))
        empty = bar_width - filled
        bar = _c("#" * filled, _Ansi.GREEN) + _c(" " * empty, _Ansi.GRAY)
        line = f"[{bar}] - {_c(str(percent) + '%', _Ansi.CYAN)}"
        if interactive:
            sys.stdout.write("\r" + line + " " * 4)
            sys.stdout.flush()
        else:
            _print(line)

    def status_cb(msg: str) -> None:
        if interactive and last_percent["value"] >= 0:
            sys.stdout.write("\n")
            sys.stdout.flush()
        _print(msg)

    def progress_cb(value: int) -> None:
        render_progress(int(value))

    ok, message = run_update_sync(mode=mode, action=action, status_cb=status_cb, progress_cb=progress_cb)
    if interactive and last_percent["value"] >= 0:
        sys.stdout.write("\n")
        sys.stdout.flush()
    if ok:
        _print(_c(message, _Ansi.GREEN))
        return 0
    _eprint(_c(message, _Ansi.RED))
    return 1

def run_interactive() -> int:
    while True:
        mode, local_version, remote_version = _status()
        _print_summary(mode, str(local_version), remote_version)
        _print("")

        actions: dict[str, str] = {}
        if mode == "not_found":
            _print(_c(t("cli_actions"), _Ansi.BOLD))
            _print(f"  {_c('1', _Ansi.CYAN)}) {t('install_discord')}")
            _print(f"  {_c('2', _Ansi.CYAN)}) {t('cli_action_change_language')}")
            _print(f"  {_c('0', _Ansi.CYAN)}) {t('cli_action_exit')}")
            actions = {"1": "install", "2": "lang", "0": "quit"}
        else:
            _print(_c(t("cli_actions"), _Ansi.BOLD))
            _print(f"  {_c('1', _Ansi.CYAN)}) {t('check_updates')}")
            _print(f"  {_c('2', _Ansi.CYAN)}) {t('update_discord')}")
            _print(f"  {_c('3', _Ansi.CYAN)}) {t('cli_action_change_language')}")
            _print(f"  {_c('0', _Ansi.CYAN)}) {t('cli_action_exit')}")
            actions = {"1": "check", "2": "update", "3": "lang", "0": "quit"}

        choice = _prompt_choice("", actions)
        action = actions[choice]

        if action == "quit":
            return 0

        if action == "lang":
            code = _language_prompt()
            if code:
                set_cli_language(code)
            _print("")
            continue

        if action == "check":
            _print("")
            continue

        if action == "install":
            _print(_c(t("cli_choose_install_source"), _Ansi.BOLD))
            _print(f"  {_c('1', _Ansi.CYAN)}) tar.gz (user)")
            _print(f"  {_c('2', _Ansi.CYAN)}) deb (apt)")
            _print(f"  {_c('3', _Ansi.CYAN)}) snap")
            _print(f"  {_c('4', _Ansi.CYAN)}) flatpak")
            _print(f"  {_c('0', _Ansi.CYAN)}) {_c(t('cli_cancel'), _Ansi.GRAY)}")
            src_map = {"1": "tar.gz", "2": "deb", "3": "snap", "4": "flatpak"}
            while True:
                src = input(_c("> ", _Ansi.BLUE)).strip()
                if src == "0":
                    break
                if src in src_map:
                    _do_update(mode=src_map[src], action="install")
                    break
                _print(_c(t("cli_invalid_choice"), _Ansi.YELLOW))
            _print("")
            continue
        _do_update(mode=mode, action="update")
        _print("")

def run_cli(args) -> int:
    set_language(load_language())

    if getattr(args, "lang", None) == "__prompt__":
        code = _language_prompt()
        if not code:
            return 0
        return set_cli_language(code)

    if getattr(args, "lang", None):
        return set_cli_language(args.lang)

    if getattr(args, "check", False):
        mode, local_version, remote_version = _status()
        _print_summary(mode, str(local_version), remote_version)
        return 0

    if getattr(args, "update", False):
        mode, _local_version = detect_discord_installation()
        if mode == "not_found":
            return run_interactive()
        return _do_update(mode=mode, action="update")
    return run_interactive()
