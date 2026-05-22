<p align="center">
  <img src="icon/logo.png" alt="discord-update logo" width="260px"/>
</p>
<h1 align="center">discord-update</h1>

<p align="center">
  <img src="https://img.shields.io/badge/OS-Linux-orange?style=for-the-badge&logo=linux" alt="OS Linux"/>
  <img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python" alt="Python Version"/>
  <img src="https://img.shields.io/badge/UI-PyQt6-green?style=for-the-badge&logo=qt" alt="UI PyQt6"/>
  <img src="https://img.shields.io/badge/License-DanKert-red?style=for-the-badge" alt="License"/>
</p>

---

**discord-update** is a lightweight, secure, and user-friendly graphical utility designed for Linux systems to easily update Discord without messing around with manual archive extractions or package issues.

It automatically detects your current installation (whether it's raw `tar.gz` or system-wide `deb`), fetches the latest remote version from the official API, and safely performs a clean update using background multi-threading.

---

## ✨ Features

* 🔍 **Smart Detection:** Automatically discovers where and how Discord is installed on your Linux machine.
* 🌐 **Multi-language Support:** Full built-in localization (easily switches context languages).
* ⚙️ **Tailored Installer Modes:** Supports processing official `.deb` files or extracting `.tar.gz` binaries.
* 🛡️ **Polkit Integration:** Uses modern system policies (`pkexec`) for secure, temporary root elevation only when writing to protected directories.
* 🎨 **Discord-inspired UI:** Beautiful custom dark theme matching the native Discord desktop application style.
---

## 📸 Screenshots

<p align="center">
  <img src="/icon/preview.png" alt="Application Preview" width="250px"/>
</p>

---

## 🚀 Installation & Usage

### 1. Clone the repository
```bash
git clone [https://github.com/DanKert/discord-update.git](https://github.com/DanKert/discord-update.git)
cd discord-update