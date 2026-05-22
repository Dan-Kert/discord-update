"""
This is the source code of discord-update, a graphical utility 
for managing and updating Discord on Linux systems.

Licensed under the DanKert Non-Commercial License.
You should have received a copy of the license in this archive (see LICENSE).

Author: DanKert, 2026.
"""
import argparse
import os
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description="Automatic Discord updater for Linux")
    parser.add_argument('--h', action='help', help='Show this help message and exit')
    parser.add_argument('--cli', action='store_true', help='Run terminal version (interactive mode)')
    parser.add_argument('--check', action='store_true', help='Check for updates (CLI)')
    parser.add_argument('--update', action='store_true', help='Update/install Discord (CLI)')
    parser.add_argument(
        '--lang',
        nargs='?',
        const='__prompt__',
        help="Change language (ru/en/ro). Without a value, opens an interactive picker.",
    )
    return parser.parse_args()

def run_cli(args):
    from discord_update.cli import run_cli as _run_cli
    return _run_cli(args)

def main():
    args = parse_arguments()

    if args.cli or args.check or args.update or args.lang:
        rc = run_cli(args)
        raise SystemExit(int(rc) if rc is not None else 0)

    from PyQt6.QtWidgets import QApplication
    from discord_update.gui import run_gui_app

    app = QApplication(sys.argv)
    app.setStyle('fusion')

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    qss_path = os.path.join(BASE_DIR, "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    run_gui_app()

if __name__ == "__main__":
    main()