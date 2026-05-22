"""
This is the source code of discord-update, a graphical utility 
for managing and updating Discord on Linux systems.

Licensed under the DanKert Non-Commercial License.
You should have received a copy of the license in this archive (see LICENSE).

Author: DanKert, 2026.
"""
from setuptools import setup, find_packages

setup(
    name="discord-update",
    version="0.1.0",
    description="Graphical utility for managing and updating Discord on Linux",
    long_description="""discord-update is a lightweight, secure, and user-friendly 
    graphical utility designed for Linux systems to easily update Discord without 
    messing around with manual archive extractions.
    """,
    long_description_content_type="text/plain",
    author="DanKert",
    author_email="dankerts@proton.me",
    license="Custom Non-Commercial License",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    package_data={
        "discord_update": ["icon/*.png", "*.qss"],
    },
    install_requires=[
        "requests==2.31.0",
        "PyQt6>=6.6.1",
    ],
    entry_points={
        "console_scripts": [
            "dicsord-updater=discord_update.main:main",
            "discord-updater=discord_update.main:main",
        ]
    },
)