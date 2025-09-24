
# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

block_cipher = None

PROJECT_DIR = Path(__file__).resolve().parent

a = Analysis(
    ['server_runner.py'],
    pathex=[os.fspath(PROJECT_DIR)],
    binaries=[],
    datas=[
        (os.fspath(PROJECT_DIR / 'templates'), 'templates'),
        (os.fspath(PROJECT_DIR / 'assets'), 'assets'),
        (os.fspath(PROJECT_DIR / 'settings.json'), '.'),
        (os.fspath(PROJECT_DIR / 'logs'), 'logs'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TransmissionWebServer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_info_entries=None,
    console=True,  # Run with a console to show server logs
    disable_window_close=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
